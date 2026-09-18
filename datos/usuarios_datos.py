from db.conexion import obtener_conexion


class UsuariosDatos:

    @staticmethod
    def obtener_usuario_por_nombre(nombre_usuario):
        conexion = obtener_conexion()
        conexion.row_factory = UsuariosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, nombre_usuario, contrasena_hash, salt, activo
            FROM usuarios
            WHERE nombre_usuario = ?
            """,
            (nombre_usuario,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def insertar_usuario(nombre_usuario, contrasena_hash, salt):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (nombre_usuario, contrasena_hash, salt, activo)
            VALUES (?, ?, ?, 1)
            """,
            (nombre_usuario, contrasena_hash, salt),
        )
        conexion.commit()
        conexion.close()

    @staticmethod
    def contar_usuarios():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))