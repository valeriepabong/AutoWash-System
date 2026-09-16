from db.conexion import obtener_conexion


class VehiculoDAO:

    @staticmethod
    def registrar(marca, modelo, placa, tipo_vehiculo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO vehiculos (marca, modelo, placa, tipo_vehiculo)
            VALUES (?, ?, ?, ?)
        """, (marca, modelo, placa, tipo_vehiculo))

        conexion.commit()
        conexion.close()


    @staticmethod
    def obtener_todos():
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id, marca, modelo, placa, tipo_vehiculo
            FROM vehiculos
            ORDER BY id
        """)

        vehiculos = cursor.fetchall()
        conexion.close()

        return vehiculos


    @staticmethod
    def actualizar(id_vehiculo, marca, modelo, placa, tipo_vehiculo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE vehiculos
            SET marca = ?,
                modelo = ?,
                placa = ?,
                tipo_vehiculo = ?
            WHERE id = ?
        """, (marca, modelo, placa, tipo_vehiculo, id_vehiculo))

        conexion.commit()
        conexion.close()


    @staticmethod
    def eliminar(id_vehiculo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM vehiculos
            WHERE id = ?
        """, (id_vehiculo,))

        conexion.commit()
        conexion.close()
