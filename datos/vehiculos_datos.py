from db.conexion import obtener_conexion


class VehiculosDatos:

    @staticmethod
    def insertar_vehiculo(placa, tipo_vehiculo, cliente_id, marca=None, modelo=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO vehiculos (placa, marca, modelo, tipo_vehiculo, cliente_id, activo)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (placa, marca, modelo, tipo_vehiculo, cliente_id),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    @staticmethod
    def obtener_vehiculo_por_id(vehiculo_id):
        conexion = obtener_conexion()
        conexion.row_factory = VehiculosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, placa, marca, modelo, tipo_vehiculo, cliente_id, activo
            FROM vehiculos WHERE id = ?
            """,
            (vehiculo_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def obtener_vehiculo_por_placa(placa):
        conexion = obtener_conexion()
        conexion.row_factory = VehiculosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, placa, marca, modelo, tipo_vehiculo, cliente_id, activo
            FROM vehiculos WHERE placa = ?
            """,
            (placa,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_vehiculos_con_cliente(solo_activos=True):
        """Trae los vehículos junto con el nombre del cliente asociado (JOIN)."""
        conexion = obtener_conexion()
        conexion.row_factory = VehiculosDatos._dict_factory
        cursor = conexion.cursor()
        condicion = "WHERE v.activo = 1" if solo_activos else ""
        cursor.execute(f"""
            SELECT v.id, v.placa, v.marca, v.modelo, v.tipo_vehiculo,
                   v.cliente_id, v.activo, c.nombre AS nombre_cliente
            FROM vehiculos v
            JOIN clientes c ON c.id = v.cliente_id
            {condicion}
            ORDER BY v.id DESC
        """)
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def listar_vehiculos_por_cliente(cliente_id):
        conexion = obtener_conexion()
        conexion.row_factory = VehiculosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, placa, marca, modelo, tipo_vehiculo, cliente_id, activo
            FROM vehiculos WHERE cliente_id = ? AND activo = 1
            ORDER BY id DESC
            """,
            (cliente_id,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def actualizar_vehiculo(vehiculo_id, placa, tipo_vehiculo, cliente_id, marca=None, modelo=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE vehiculos
            SET placa = ?, marca = ?, modelo = ?, tipo_vehiculo = ?, cliente_id = ?
            WHERE id = ?
            """,
            (placa, marca, modelo, tipo_vehiculo, cliente_id, vehiculo_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def desactivar_vehiculo(vehiculo_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE vehiculos SET activo = 0 WHERE id = ?", (vehiculo_id,))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))