from datetime import datetime

from datos.servicios_datos import ServiciosDatos
from datos.ordenes_datos import OrdenesDatos
from datos.vehiculos_datos import VehiculosDatos


class ServiciosLogica:

    # ---------- Catálogo de servicios ----------

    @staticmethod
    def registrar_servicio(nombre, precio):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del servicio es obligatorio.")

        try:
            precio = float(precio)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número válido.")

        if precio <= 0:
            raise ValueError("El precio del servicio debe ser mayor a cero.")

        if ServiciosDatos.obtener_servicio_por_nombre(nombre) is not None:
            raise ValueError("Ya existe un servicio con ese nombre.")

        return ServiciosDatos.insertar_servicio(nombre, precio)

    @staticmethod
    def listar_servicios():
        return ServiciosDatos.listar_servicios(solo_activos=True)

    @staticmethod
    def eliminar_servicio(servicio_id):
        if ServiciosDatos.obtener_servicio_por_id(servicio_id) is None:
            raise ValueError("El servicio no existe.")
        ServiciosDatos.desactivar_servicio(servicio_id)

    @staticmethod
    def crear_catalogo_por_defecto_si_no_existe():
        """Crea un catálogo básico de servicios si la tabla está vacía."""
        if ServiciosDatos.contar_servicios() == 0:
            ServiciosLogica.registrar_servicio("Lavado básico", 15000)
            ServiciosLogica.registrar_servicio("Lavado completo", 25000)
            ServiciosLogica.registrar_servicio("Encerado", 20000)
            ServiciosLogica.registrar_servicio("Aspirado de interiores", 10000)

    # ---------- Asignación de servicios a un vehículo (HU02) ----------

    @staticmethod
    def asignar_servicios(vehiculo_id, servicio_ids):
        """
        Crea una orden de servicio para un vehículo con uno o varios servicios.
        - Valida que se haya seleccionado al menos un servicio.
        - Calcula el total automáticamente sumando los precios del catálogo.
        - Registra la fecha/hora de asignación automáticamente.
        La orden queda en estado 'pendiente', sin empleado (se asigna al finalizar).
        Devuelve el id de la orden creada.
        """
        if not vehiculo_id:
            raise ValueError("Debe indicar el vehículo al que se le asignará el servicio.")

        if VehiculosDatos.obtener_vehiculo_por_id(vehiculo_id) is None:
            raise ValueError("El vehículo seleccionado no existe.")

        if not servicio_ids:
            raise ValueError("Debe seleccionar al menos un servicio.")

        # Quitar duplicados manteniendo el orden, por si la interfaz envía el mismo id dos veces
        servicio_ids = list(dict.fromkeys(servicio_ids))

        items = []
        total = 0.0
        for servicio_id in servicio_ids:
            servicio = ServiciosDatos.obtener_servicio_por_id(servicio_id)
            if servicio is None or servicio["activo"] != 1:
                raise ValueError(f"El servicio con id {servicio_id} no existe o no está disponible.")
            items.append((servicio_id, servicio["precio"]))
            total += servicio["precio"]

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return OrdenesDatos.crear_orden_con_detalle(vehiculo_id, fecha_hora, total, items)

    @staticmethod
    def obtener_orden(orden_id):
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            return None
        orden["detalle"] = OrdenesDatos.obtener_detalle_de_orden(orden_id)
        return orden

    @staticmethod
    def listar_ordenes(solo_pendientes=False):
        return OrdenesDatos.listar_ordenes(solo_pendientes=solo_pendientes)

    @staticmethod
    def listar_ordenes_pendientes():
        return OrdenesDatos.listar_ordenes(solo_pendientes=True)

    @staticmethod
    def finalizar_orden(orden_id, empleado_id):
        """
        Cierra una orden de servicio asignando el empleado responsable.
        Lanza ValueError si la orden no existe, ya está finalizada,
        o no se indicó un empleado válido.
        """
        from datos.empleados_datos import EmpleadosDatos

        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")

        if orden["estado"] == "finalizado":
            raise ValueError("Esta orden ya fue finalizada anteriormente.")

        if not empleado_id:
            raise ValueError("Debe indicar el empleado que realizó el servicio.")

        empleado = EmpleadosDatos.obtener_empleado_por_id(empleado_id)
        if empleado is None or empleado["activo"] != 1:
            raise ValueError("El empleado seleccionado no existe o no está activo.")

        OrdenesDatos.finalizar_orden(orden_id, empleado_id)