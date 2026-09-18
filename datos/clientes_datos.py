import unicodedata

from db.conexion import obtener_conexion


class ClientesDatos:

    @staticmethod
    def insertar_cliente(nombre, telefono):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, activo) VALUES (?, ?, 1)",
            (nombre, telefono),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    @staticmethod
    def obtener_cliente_por_id(cliente_id):
        conexion = obtener_conexion()
        conexion.row_factory = ClientesDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, telefono, activo FROM clientes WHERE id = ?",
            (cliente_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_clientes(solo_activos=True):
        conexion = obtener_conexion()
        conexion.row_factory = ClientesDatos._dict_factory
        cursor = conexion.cursor()
        if solo_activos:
            cursor.execute(
                "SELECT id, nombre, telefono, activo FROM clientes WHERE activo = 1 ORDER BY nombre"
            )
        else:
            cursor.execute(
                "SELECT id, nombre, telefono, activo FROM clientes ORDER BY nombre"
            )
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def buscar_clientes_por_nombre(texto_busqueda):
        conexion = obtener_conexion()
        conexion.row_factory = ClientesDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, telefono, activo FROM clientes WHERE activo = 1 ORDER BY nombre"
        )
        todos = cursor.fetchall()
        conexion.close()

        texto_normalizado = ClientesDatos._normalizar(texto_busqueda)
        return [
            cliente for cliente in todos
            if texto_normalizado in ClientesDatos._normalizar(cliente["nombre"])
        ]

    @staticmethod
    def actualizar_cliente(cliente_id, nombre, telefono):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?",
            (nombre, telefono, cliente_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def desactivar_cliente(cliente_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (cliente_id,))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _normalizar(texto):
        texto = texto.lower()
        texto = unicodedata.normalize("NFKD", texto)
        return "".join(c for c in texto if not unicodedata.combining(c))

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))