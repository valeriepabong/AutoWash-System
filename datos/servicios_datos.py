from db.conexion import obtener_conexion


class ServiciosDatos:

    @staticmethod
    def insertar_servicio(nombre, precio):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO servicios (nombre, precio, activo) VALUES (?, ?, 1)",
            (nombre, precio),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    @staticmethod
    def obtener_servicio_por_id(servicio_id):
        conexion = obtener_conexion()
        conexion.row_factory = ServiciosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, precio, activo FROM servicios WHERE id = ?",
            (servicio_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def obtener_servicio_por_nombre(nombre):
        conexion = obtener_conexion()
        conexion.row_factory = ServiciosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, precio, activo FROM servicios WHERE nombre = ?",
            (nombre,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_servicios(solo_activos=True):
        conexion = obtener_conexion()
        conexion.row_factory = ServiciosDatos._dict_factory
        cursor = conexion.cursor()
        if solo_activos:
            cursor.execute(
                "SELECT id, nombre, precio, activo FROM servicios WHERE activo = 1 ORDER BY nombre"
            )
        else:
            cursor.execute("SELECT id, nombre, precio, activo FROM servicios ORDER BY nombre")
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def contar_servicios():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM servicios")
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    @staticmethod
    def actualizar_servicio(servicio_id, nombre, precio):
        """Actualiza nombre y precio de un servicio del catálogo (Update del CRUD)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE servicios SET nombre = ?, precio = ? WHERE id = ?",
            (nombre, precio, servicio_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def desactivar_servicio(servicio_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE servicios SET activo = 0 WHERE id = ?", (servicio_id,))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))