from db.conexion import obtener_conexion


class InventarioDatos:

    # ---------- CRUD de insumos ----------

    @staticmethod
    def insertar_insumo(nombre, unidad_medida, stock_minimo):
        """
        Crea el insumo con stock_actual en 0. El stock inicial (si lo hay)
        se carga aparte con registrar_movimiento, para que TODO cambio de
        cantidad -incluido el primero- quede con su rastro en el historial.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO insumos (nombre, unidad_medida, stock_actual, stock_minimo, activo)
            VALUES (?, ?, 0, ?, 1)
            """,
            (nombre, unidad_medida, stock_minimo),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    @staticmethod
    def obtener_insumo_por_id(insumo_id):
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, unidad_medida, stock_actual, stock_minimo, activo FROM insumos WHERE id = ?",
            (insumo_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def obtener_insumo_por_nombre(nombre):
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, unidad_medida, stock_actual, stock_minimo, activo FROM insumos WHERE nombre = ?",
            (nombre,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_insumos(solo_activos=True):
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        if solo_activos:
            cursor.execute(
                "SELECT id, nombre, unidad_medida, stock_actual, stock_minimo, activo "
                "FROM insumos WHERE activo = 1 ORDER BY nombre"
            )
        else:
            cursor.execute(
                "SELECT id, nombre, unidad_medida, stock_actual, stock_minimo, activo "
                "FROM insumos ORDER BY nombre"
            )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def listar_insumos_bajo_stock():
        """Insumos activos cuyo stock_actual ya llegó o bajó de su stock_minimo."""
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, nombre, unidad_medida, stock_actual, stock_minimo, activo
            FROM insumos
            WHERE activo = 1 AND stock_actual <= stock_minimo
            ORDER BY nombre
            """
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def actualizar_insumo(insumo_id, nombre, unidad_medida, stock_minimo):
        """
        Actualiza los datos descriptivos del insumo (nombre, unidad, stock mínimo).
        NO toca stock_actual: el stock solo cambia a través de registrar_movimiento,
        para que todo cambio de cantidad quede siempre con su rastro en el historial.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE insumos SET nombre = ?, unidad_medida = ?, stock_minimo = ? WHERE id = ?",
            (nombre, unidad_medida, stock_minimo, insumo_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def desactivar_insumo(insumo_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE insumos SET activo = 0 WHERE id = ?", (insumo_id,))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def contar_insumos():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM insumos")
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    # ---------- Movimientos de inventario (entradas / salidas) ----------

    @staticmethod
    def registrar_movimiento(insumo_id, tipo_movimiento, cantidad, fecha_hora, orden_id=None, motivo=None):
        """
        Registra un movimiento de inventario y actualiza stock_actual del
        insumo EN LA MISMA TRANSACCIÓN, para que nunca quede un movimiento
        guardado sin reflejarse en el stock (o viceversa).
        tipo_movimiento: 'entrada' suma al stock, 'salida' resta del stock.
        Devuelve el nuevo stock_actual.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT stock_actual FROM insumos WHERE id = ?", (insumo_id,))
            fila = cursor.fetchone()
            if fila is None:
                raise ValueError("El insumo no existe.")
            stock_actual = fila[0]

            if tipo_movimiento == "entrada":
                nuevo_stock = stock_actual + cantidad
            else:
                nuevo_stock = stock_actual - cantidad

            cursor.execute(
                "UPDATE insumos SET stock_actual = ? WHERE id = ?",
                (nuevo_stock, insumo_id),
            )
            cursor.execute(
                """
                INSERT INTO movimientos_inventario
                    (insumo_id, tipo_movimiento, cantidad, fecha_hora, orden_id, motivo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (insumo_id, tipo_movimiento, cantidad, fecha_hora, orden_id, motivo),
            )

            conexion.commit()
            return nuevo_stock
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def listar_movimientos(insumo_id=None):
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        condicion = "WHERE m.insumo_id = ?" if insumo_id else ""
        parametros = (insumo_id,) if insumo_id else ()
        cursor.execute(
            f"""
            SELECT m.id, m.insumo_id, m.tipo_movimiento, m.cantidad, m.fecha_hora,
                   m.orden_id, m.motivo, i.nombre AS nombre_insumo, i.unidad_medida
            FROM movimientos_inventario m
            JOIN insumos i ON i.id = m.insumo_id
            {condicion}
            ORDER BY m.id DESC
            """,
            parametros,
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    # ---------- Receta: qué insumos gasta cada servicio ----------

    @staticmethod
    def asociar_insumo_a_servicio(servicio_id, insumo_id, cantidad_consumida):
        """
        Crea o actualiza la 'receta': cuánto de este insumo gasta este servicio.
        Usa INSERT OR REPLACE porque (servicio_id, insumo_id) es la llave primaria
        compuesta de servicio_insumo: si ya existía la relación, la sobreescribe
        con la nueva cantidad en vez de duplicarla.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO servicio_insumo (servicio_id, insumo_id, cantidad_consumida)
            VALUES (?, ?, ?)
            """,
            (servicio_id, insumo_id, cantidad_consumida),
        )
        conexion.commit()
        conexion.close()

    @staticmethod
    def listar_insumos_de_servicio(servicio_id):
        conexion = obtener_conexion()
        conexion.row_factory = InventarioDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT si.servicio_id, si.insumo_id, si.cantidad_consumida,
                   i.nombre AS nombre_insumo, i.unidad_medida
            FROM servicio_insumo si
            JOIN insumos i ON i.id = si.insumo_id
            WHERE si.servicio_id = ?
            """,
            (servicio_id,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def quitar_insumo_de_servicio(servicio_id, insumo_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM servicio_insumo WHERE servicio_id = ? AND insumo_id = ?",
            (servicio_id, insumo_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))