from db.conexion import obtener_conexion


class DashboardDatos:
    """Consultas de solo lectura para el Panel de Control (una consulta por dato, sin N+1)."""

    @staticmethod
    def contar_ordenes_por_estado():
        """Devuelve {'espera': n, 'proceso': n, 'terminado': n, 'entregado': n} (solo estados con filas)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT estado, COUNT(*) FROM ordenes_servicio GROUP BY estado")
        resultado = {estado: total for estado, total in cursor.fetchall()}
        conexion.close()
        return resultado

    @staticmethod
    def contar_finalizados_del_dia(fecha_iso):
        """Ordenes terminadas o entregadas cuya fecha de ingreso es la fecha dada (YYYY-MM-DD)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM ordenes_servicio
            WHERE estado IN ('terminado', 'entregado')
              AND substr(fecha_hora, 1, 10) = ?
            """,
            (fecha_iso,),
        )
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    @staticmethod
    def sumar_ingresos_del_dia(fecha_iso):
        """Suma de las facturas emitidas en la fecha dada (YYYY-MM-DD). 0 si no hay."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(total), 0) FROM facturas WHERE substr(fecha_hora, 1, 10) = ?",
            (fecha_iso,),
        )
        total = cursor.fetchone()[0]
        conexion.close()
        return float(total or 0)

    @staticmethod
    def listar_ordenes_panel(fecha_iso):
        """
        Ordenes para la tabla 'Vehiculos en Servicio Activo': todas las que siguen en
        el lavadero (espera, proceso, terminado) mas las entregadas hoy.
        Una sola consulta con JOIN; los servicios vienen concatenados.
        Claves: id, estado, fecha_hora, empleado_id, placa, tipo_vehiculo,
                nombre_cliente, servicios, factura_id, fecha_factura.
        """
        conexion = obtener_conexion()
        conexion.row_factory = DashboardDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT o.id, o.estado, o.fecha_hora, o.empleado_id,
                   v.placa, v.tipo_vehiculo,
                   c.nombre AS nombre_cliente,
                   (SELECT GROUP_CONCAT(s.nombre, ', ')
                      FROM orden_servicio_detalle d
                      JOIN servicios s ON s.id = d.servicio_id
                     WHERE d.orden_id = o.id) AS servicios,
                   f.id AS factura_id,
                   f.fecha_hora AS fecha_factura
            FROM ordenes_servicio o
            JOIN vehiculos v ON v.id = o.vehiculo_id
            JOIN clientes c ON c.id = v.cliente_id
            LEFT JOIN facturas f ON f.orden_id = o.id
            WHERE o.estado != 'entregado'
               OR substr(o.fecha_hora, 1, 10) = ?
            ORDER BY CASE o.estado
                         WHEN 'proceso'   THEN 0
                         WHEN 'espera'    THEN 1
                         WHEN 'terminado' THEN 2
                         ELSE 3
                     END,
                     o.id DESC
            """,
            (fecha_iso,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))