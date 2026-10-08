from db.conexion import obtener_conexion


class Reportes_Datos:

    @staticmethod
    def ingresos_por_dia(fecha_desde, fecha_hasta):

        conexion = obtener_conexion()
        conexion.row_factory = Reportes_Datos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT date(fecha_hora) AS fecha,
                   COUNT(*)         AS cantidad_facturas,
                   SUM(total)       AS total_ingresos
            FROM facturas
            WHERE date(fecha_hora) BETWEEN ? AND ?
            GROUP BY date(fecha_hora)
            ORDER BY fecha ASC
            """,
            (fecha_desde, fecha_hasta),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def servicios_mas_solicitados(fecha_desde, fecha_hasta, limite=None):

        conexion = obtener_conexion()
        conexion.row_factory = Reportes_Datos._dict_factory
        cursor = conexion.cursor()

        consulta = """
            SELECT s.id                    AS servicio_id,
                   s.nombre                AS nombre_servicio,
                   COUNT(*)                AS cantidad_vendida,
                   SUM(d.precio_aplicado)  AS ingreso_generado
            FROM orden_servicio_detalle d
            JOIN facturas f ON f.orden_id = d.orden_id
            JOIN servicios s ON s.id = d.servicio_id
            WHERE date(f.fecha_hora) BETWEEN ? AND ?
            GROUP BY s.id, s.nombre
            ORDER BY cantidad_vendida DESC, ingreso_generado DESC, s.nombre ASC
        """
        parametros = [fecha_desde, fecha_hasta]

        if limite is not None:
            consulta += " LIMIT ?"
            parametros.append(int(limite))

        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def consumo_de_insumos(fecha_desde, fecha_hasta):
        """
        Cantidad total consumida de cada insumo en el rango.
        Solo cuentan los movimientos de tipo 'salida' (las entradas son
        reposicion de stock, no consumo).
        """
        conexion = obtener_conexion()
        conexion.row_factory = Reportes_Datos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT i.id            AS insumo_id,
                   i.nombre        AS nombre_insumo,
                   i.unidad_medida AS unidad_medida,
                   SUM(m.cantidad) AS cantidad_consumida
            FROM movimientos_inventario m
            JOIN insumos i ON i.id = m.insumo_id
            WHERE m.tipo_movimiento = 'salida'
              AND date(m.fecha_hora) BETWEEN ? AND ?
            GROUP BY i.id, i.nombre, i.unidad_medida
            ORDER BY cantidad_consumida DESC, i.nombre ASC
            """,
            (fecha_desde, fecha_hasta),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))