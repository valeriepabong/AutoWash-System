from datos.empleados_datos import EmpleadosDatos


class EmpleadosLogica:

    @staticmethod
    def registrar_empleado(nombre):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del empleado es obligatorio.")
        return EmpleadosDatos.insertar_empleado(nombre)

    @staticmethod
    def listar_empleados():
        return EmpleadosDatos.listar_empleados(solo_activos=True)

    @staticmethod
    def obtener_empleado(empleado_id):
        return EmpleadosDatos.obtener_empleado_por_id(empleado_id)

    @staticmethod
    def servicios_realizados_por_empleado(empleado_id):
        if EmpleadosDatos.obtener_empleado_por_id(empleado_id) is None:
            raise ValueError("El empleado no existe.")
        return EmpleadosDatos.contar_servicios_realizados(empleado_id)

    @staticmethod
    def eliminar_empleado(empleado_id):
        if EmpleadosDatos.obtener_empleado_por_id(empleado_id) is None:
            raise ValueError("El empleado no existe.")
        EmpleadosDatos.desactivar_empleado(empleado_id)