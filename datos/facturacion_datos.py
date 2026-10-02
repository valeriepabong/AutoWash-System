# datos/facturacion_datos.py
from db.conexion import obtener_conexion


class FacturacionDatos:

    @staticmethod
    def insertar_factura(orden_id, metodo_pago, total, fecha_hora):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO facturas (orden_id, metodo_pago, total, fecha_hora)
            VALUES (?, ?, ?, ?)
            """,
            (orden_id, metodo_pago, total, fecha_hora),
        )
        conexion.commit()
        nueva_id = cursor.lastrowid
        conexion.close()
        return nueva_id

    @staticmethod
    def obtener_factura_por_id(factura_id):
        conexion = obtener_conexion()
        conexion.row_factory = FacturacionDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT f.id, f.orden_id, f.metodo_pago, f.total, f.fecha_hora,
                   o.fecha_hora AS fecha_servicio, o.estado,
                   v.placa, c.nombre AS nombre_cliente, c.telefono,
                   e.nombre AS nombre_empleado
            FROM facturas f
            JOIN ordenes_servicio o ON o.id = f.orden_id
            JOIN vehiculos v ON v.id = o.vehiculo_id
            JOIN clientes c ON c.id = v.cliente_id
            LEFT JOIN empleados e ON e.id = o.empleado_id
            WHERE f.id = ?
            """,
            (factura_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def obtener_factura_por_orden(orden_id):
        conexion = obtener_conexion()
        conexion.row_factory = FacturacionDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, orden_id, metodo_pago, total, fecha_hora FROM facturas WHERE orden_id = ?",
            (orden_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_facturas():
        conexion = obtener_conexion()
        conexion.row_factory = FacturacionDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT f.id, f.orden_id, f.metodo_pago, f.total, f.fecha_hora,
                   v.placa, c.nombre AS nombre_cliente
            FROM facturas f
            JOIN ordenes_servicio o ON o.id = f.orden_id
            JOIN vehiculos v ON v.id = o.vehiculo_id
            JOIN clientes c ON c.id = v.cliente_id
            ORDER BY f.id DESC
            """
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))