from db.conexion import obtener_conexion


class OrdenesDatos:

    @staticmethod
    def crear_orden_con_detalle(vehiculo_id, fecha_hora, total, items, empleado_id=None, conexion=None):
        propia = conexion is None
        if propia:
            conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO ordenes_servicio (vehiculo_id, empleado_id, fecha_hora, total, estado)
                VALUES (?, ?, ?, ?, 'espera')
                """,
                (vehiculo_id, empleado_id, fecha_hora, total),
            )
            orden_id = cursor.lastrowid

            for servicio_id, precio_aplicado in items:
                cursor.execute(
                    """
                    INSERT INTO orden_servicio_detalle (orden_id, servicio_id, precio_aplicado)
                    VALUES (?, ?, ?)
                    """,
                    (orden_id, servicio_id, precio_aplicado),
                )

            if propia:
                conexion.commit()
            return orden_id
        except Exception:
            if propia:
                conexion.rollback()
            raise
        finally:
            if propia:
                conexion.close()

    @staticmethod
    def crear_orden_con_detalle_y_movimientos(
        vehiculo_id, fecha_hora, total, items, consumo_insumos, empleado_id=None
    ):
        """
        Crea la orden con su detalle y registra los movimientos de salida de insumos
        en UNA SOLA transacción atómica (misma conexión y commit).
        Revalida el stock dentro de la transacción.
        Ante cualquier excepción realiza un rollback total.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # 1. Revalidar stock dentro de la transacción
            for insumo_id, cantidad_requerida in consumo_insumos.items():
                cursor.execute(
                    "SELECT nombre, unidad_medida, stock_actual FROM insumos WHERE id = ?",
                    (insumo_id,),
                )
                fila = cursor.fetchone()
                if fila is None:
                    continue
                nombre, unidad, stock_actual = fila[0], fila[1], fila[2]
                if stock_actual < cantidad_requerida:
                    raise ValueError(
                        f"Stock insuficiente de '{nombre}': se necesitan "
                        f"{cantidad_requerida} {unidad} y solo hay "
                        f"{stock_actual} {unidad} disponibles."
                    )

            # 2. Insertar orden y detalles usando la conexión compartida
            orden_id = OrdenesDatos.crear_orden_con_detalle(
                vehiculo_id, fecha_hora, total, items, empleado_id=empleado_id, conexion=conexion
            )

            # 3. Registrar salidas de inventario usando la misma conexión
            from datos.inventario_datos import InventarioDatos
            for insumo_id, cantidad_requerida in consumo_insumos.items():
                InventarioDatos.registrar_movimiento(
                    insumo_id,
                    "salida",
                    cantidad_requerida,
                    fecha_hora,
                    orden_id=orden_id,
                    motivo=f"Consumo automático de la orden #{orden_id}",
                    conexion=conexion,
                )

            conexion.commit()
            return orden_id
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def obtener_orden_por_id(orden_id):
        conexion = obtener_conexion()
        conexion.row_factory = OrdenesDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT o.id, o.vehiculo_id, o.empleado_id, o.fecha_hora, o.total, o.estado,
                   v.placa, e.nombre AS nombre_empleado
            FROM ordenes_servicio o
            JOIN vehiculos v ON v.id = o.vehiculo_id
            LEFT JOIN empleados e ON e.id = o.empleado_id
            WHERE o.id = ?
            """,
            (orden_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def obtener_detalle_de_orden(orden_id):
        conexion = obtener_conexion()
        conexion.row_factory = OrdenesDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT d.id, d.servicio_id, d.precio_aplicado, s.nombre AS nombre_servicio
            FROM orden_servicio_detalle d
            JOIN servicios s ON s.id = d.servicio_id
            WHERE d.orden_id = ?
            """,
            (orden_id,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def listar_ordenes(solo_activas=False):
        conexion = obtener_conexion()
        conexion.row_factory = OrdenesDatos._dict_factory
        cursor = conexion.cursor()
        condicion = "WHERE o.estado != 'entregado'" if solo_activas else ""
        cursor.execute(f"""
            SELECT o.id, o.vehiculo_id, o.empleado_id, o.fecha_hora, o.total, o.estado,
                   v.placa, e.nombre AS nombre_empleado
            FROM ordenes_servicio o
            JOIN vehiculos v ON v.id = o.vehiculo_id
            LEFT JOIN empleados e ON e.id = o.empleado_id
            {condicion}
            ORDER BY o.id DESC
        """)
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def actualizar_estado(orden_id, nuevo_estado, empleado_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE ordenes_servicio
            SET estado = ?, empleado_id = ?
            WHERE id = ?
            """,
            (nuevo_estado, empleado_id, orden_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))