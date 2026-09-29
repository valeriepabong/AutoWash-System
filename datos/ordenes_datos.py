from db.conexion import obtener_conexion


class OrdenesDatos:

    @staticmethod
    def crear_orden_con_detalle(vehiculo_id, fecha_hora, total, items, empleado_id=None):
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