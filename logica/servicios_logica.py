from datetime import datetime

from datos.servicios_datos import ServiciosDatos
from datos.ordenes_datos import OrdenesDatos
from datos.vehiculos_datos import VehiculosDatos
from datos.empleados_datos import EmpleadosDatos


class ServiciosLogica:

    # Secuencia oficial de estados de una orden de servicio.
    # El orden de esta lista ES la regla de negocio: solo se puede avanzar
    # a la posición inmediatamente siguiente, nunca saltar ni retroceder.
    ESTADOS_ORDEN = ["espera", "proceso", "terminado", "entregado"]

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
        def editar_servicio(servicio_id, nombre, precio):
            nombre = (nombre or "").strip()
            if not nombre:
                raise ValueError("El nombre del servicio es obligatorio.")

            try:
                precio = float(precio)
            except (TypeError, ValueError):
                raise ValueError("El precio debe ser un número válido.")

            if precio <= 0:
                raise ValueError("El precio del servicio debe ser mayor a cero.")

            if ServiciosDatos.obtener_servicio_por_id(servicio_id) is None:
                raise ValueError("El servicio no existe.")

            existente = ServiciosDatos.obtener_servicio_por_nombre(nombre)
            if existente is not None and existente["id"] != servicio_id:
                raise ValueError("Ya existe otro servicio con ese nombre.")

            ServiciosDatos.actualizar_servicio(servicio_id, nombre, precio)

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
    def asignar_servicios(vehiculo_id, servicio_ids, empleado_id=None):
        """
        Crea una orden de servicio para un vehículo con uno o varios servicios.
        - Valida que se haya seleccionado al menos un servicio.
        - Calcula el total automáticamente sumando los precios del catálogo.
        - Registra la fecha/hora de asignación automáticamente.
        - Opcionalmente permite indicar de una vez el empleado responsable.
        La orden queda en estado 'espera'. Devuelve el id de la orden creada.
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

        if empleado_id is not None:
            empleado = EmpleadosDatos.obtener_empleado_por_id(empleado_id)
            if empleado is None or empleado["activo"] != 1:
                raise ValueError("El empleado seleccionado no existe o no está activo.")

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return OrdenesDatos.crear_orden_con_detalle(
            vehiculo_id, fecha_hora, total, items, empleado_id=empleado_id
        )

    @staticmethod
    def obtener_orden(orden_id):
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            return None
        orden["detalle"] = OrdenesDatos.obtener_detalle_de_orden(orden_id)
        return orden

    @staticmethod
    def listar_ordenes(estado=None):
        """estado=None trae todas; o filtra por 'espera' | 'proceso' | 'terminado' | 'entregado'."""
        return OrdenesDatos.listar_ordenes(estado=estado)

    @staticmethod
    def listar_ordenes_pendientes():
        """Órdenes que aún no han entrado a proceso (equivalente a la antigua 'pendiente')."""
        return OrdenesDatos.listar_ordenes(estado="espera")

    @staticmethod
    def siguiente_estado(estado_actual):
        """
        Devuelve cuál es el único siguiente estado válido para 'estado_actual',
        o None si ya está en el último estado ('entregado'). Útil para que
        Frontend sepa qué botón/opción mostrar sin duplicar la regla de negocio.
        """
        indice_actual = ServiciosLogica.ESTADOS_ORDEN.index(estado_actual)
        if indice_actual == len(ServiciosLogica.ESTADOS_ORDEN) - 1:
            return None
        return ServiciosLogica.ESTADOS_ORDEN[indice_actual + 1]

    @staticmethod
    def cambiar_estado_orden(orden_id, nuevo_estado, empleado_id=None):
        """
        Avanza el estado de una orden de servicio, validando que:
        - La orden exista.
        - El nuevo estado sea uno de los válidos.
        - Se avance EXACTAMENTE una posición en la secuencia
          ["espera", "proceso", "terminado", "entregado"], sin saltar
          estados y sin retroceder.
        - Al pasar a 'proceso' exista un empleado responsable asignado
          (ya sea porque se indicó antes, o porque se indica en este llamado
          mediante el parámetro empleado_id).
        """
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")

        if nuevo_estado not in ServiciosLogica.ESTADOS_ORDEN:
            raise ValueError(
                f"Estado inválido '{nuevo_estado}'. "
                f"Los estados válidos son: {', '.join(ServiciosLogica.ESTADOS_ORDEN)}."
            )

        estado_actual = orden["estado"]
        indice_actual = ServiciosLogica.ESTADOS_ORDEN.index(estado_actual)
        indice_nuevo = ServiciosLogica.ESTADOS_ORDEN.index(nuevo_estado)

        if indice_nuevo != indice_actual + 1:
            siguiente = ServiciosLogica.siguiente_estado(estado_actual)
            if siguiente is None:
                raise ValueError("Esta orden ya fue entregada y no puede cambiar de estado.")
            raise ValueError(
                f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'. "
                f"El único siguiente estado válido es '{siguiente}'."
            )

        empleado_responsable_id = empleado_id if empleado_id is not None else orden["empleado_id"]

        if nuevo_estado == "proceso" and not empleado_responsable_id:
            raise ValueError(
                "Debe asignar un empleado responsable antes de pasar la orden a 'proceso'."
            )

        if empleado_id is not None:
            empleado = EmpleadosDatos.obtener_empleado_por_id(empleado_id)
            if empleado is None or empleado["activo"] != 1:
                raise ValueError("El empleado seleccionado no existe o no está activo.")
            OrdenesDatos.asignar_empleado(orden_id, empleado_id)

        OrdenesDatos.actualizar_estado(orden_id, nuevo_estado)