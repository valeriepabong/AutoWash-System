from db.conexion import obtener_conexion


class EmpleadosDatos:

    @staticmethod
    def insertar_empleado(nombre):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO empleados (nombre, activo) VALUES (?, 1)",
            (nombre,),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return nuevo_id

    @staticmethod
    def obtener_empleado_por_id(empleado_id):
        conexion = obtener_conexion()
        conexion.row_factory = EmpleadosDatos._dict_factory
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, activo FROM empleados WHERE id = ?",
            (empleado_id,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return fila

    @staticmethod
    def listar_empleados(solo_activos=True):
        conexion = obtener_conexion()
        conexion.row_factory = EmpleadosDatos._dict_factory
        cursor = conexion.cursor()
        if solo_activos:
            cursor.execute(
                "SELECT id, nombre, activo FROM empleados WHERE activo = 1 ORDER BY nombre"
            )
        else:
            cursor.execute("SELECT id, nombre, activo FROM empleados ORDER BY nombre")
        filas = cursor.fetchall()
        conexion.close()
        return filas

    @staticmethod
    def contar_servicios_realizados(empleado_id):
        """
        Cuenta cuántas órdenes de servicio finalizadas tiene un empleado.
        Útil para HU de 'consultar servicios realizados' por empleado.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM ordenes_servicio
            WHERE empleado_id = ? AND estado = 'entregado'
            """,
            (empleado_id,),
        )
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    @staticmethod
    def actualizar_empleado(empleado_id, nombre):
        """Actualiza el nombre de un empleado existente (Update del CRUD)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE empleados SET nombre = ? WHERE id = ?",
            (nombre, empleado_id),
        )
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def desactivar_empleado(empleado_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _dict_factory(cursor, fila):
        columnas = [descripcion[0] for descripcion in cursor.description]
        return dict(zip(columnas, fila))