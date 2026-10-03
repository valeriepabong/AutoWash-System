from datetime import datetime

from datos.servicios_datos import ServiciosDatos
from datos.ordenes_datos import OrdenesDatos
from datos.vehiculos_datos import VehiculosDatos
from datos.empleados_datos import EmpleadosDatos
from logica.inventario_logica import InventarioLogica


class ServiciosLogica:

    # Orden válido de transición. No se puede saltar estados ni retroceder.
    FLUJO_ESTADOS = ["espera", "proceso", "terminado", "entregado"]

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
        La orden nace en estado 'espera'. El empleado es opcional en este punto:
        puede asignarse ahora o más adelante, al avanzar de estado.
        Antes de crear la orden valida que haya stock suficiente de los
        insumos que consumen los servicios elegidos, y al crearla descuenta
        ese inventario automáticamente.
        """
        if not vehiculo_id:
            raise ValueError("Debe indicar el vehículo al que se le asignará el servicio.")

        if VehiculosDatos.obtener_vehiculo_por_id(vehiculo_id) is None:
            raise ValueError("El vehículo seleccionado no existe.")

        if not servicio_ids:
            raise ValueError("Debe seleccionar al menos un servicio.")

        if empleado_id is not None:
            empleado = EmpleadosDatos.obtener_empleado_por_id(empleado_id)
            if empleado is None or empleado["activo"] != 1:
                raise ValueError("El empleado seleccionado no existe o no está activo.")

        servicio_ids = list(dict.fromkeys(servicio_ids))

        items = []
        total = 0.0
        for servicio_id in servicio_ids:
            servicio = ServiciosDatos.obtener_servicio_por_id(servicio_id)
            if servicio is None or servicio["activo"] != 1:
                raise ValueError(f"El servicio con id {servicio_id} no existe o no está disponible.")
            items.append((servicio_id, servicio["precio"]))
            total += servicio["precio"]

        InventarioLogica.validar_stock_suficiente(servicio_ids)

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        orden_id = OrdenesDatos.crear_orden_con_detalle(vehiculo_id, fecha_hora, total, items, empleado_id)

        InventarioLogica.descontar_insumos_de_servicios(servicio_ids, orden_id, fecha_hora)

        return orden_id

    @staticmethod
    def obtener_orden(orden_id):
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            return None
        orden["detalle"] = OrdenesDatos.obtener_detalle_de_orden(orden_id)
        return orden

    @staticmethod
    def listar_ordenes(solo_activas=False):
        """
        solo_activas=True devuelve solo las que no han llegado a 'entregado'
        (es decir, las que siguen en curso dentro del lavadero).
        """
        return OrdenesDatos.listar_ordenes(solo_activas=solo_activas)

    # ---------- Cambio de estado (espera -> proceso -> terminado -> entregado) ----------

    @staticmethod
    def siguiente_estado(estado_actual):
        """
        Devuelve el siguiente estado válido en el flujo, o None si ya
        está en el último estado ('entregado').
        """
        try:
            posicion = ServiciosLogica.FLUJO_ESTADOS.index(estado_actual)
        except ValueError:
            raise ValueError(f"Estado desconocido: {estado_actual}")

        if posicion == len(ServiciosLogica.FLUJO_ESTADOS) - 1:
            return None
        return ServiciosLogica.FLUJO_ESTADOS[posicion + 1]

    @staticmethod
    def cambiar_estado_orden(orden_id, nuevo_estado, empleado_id=None):
        """
        Avanza una orden al siguiente estado del flujo, validando que no se
        salten estados y que no se retroceda.
        Si la orden todavía no tiene empleado asignado, se debe indicar uno.
        """
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")

        estado_actual = orden["estado"]

        if estado_actual == "entregado":
            raise ValueError("Esta orden ya fue entregada y no puede cambiar de estado.")

        if nuevo_estado not in ServiciosLogica.FLUJO_ESTADOS:
            raise ValueError(f"'{nuevo_estado}' no es un estado válido.")

        posicion_actual = ServiciosLogica.FLUJO_ESTADOS.index(estado_actual)
        posicion_nueva = ServiciosLogica.FLUJO_ESTADOS.index(nuevo_estado)

        if posicion_nueva != posicion_actual + 1:
            raise ValueError(
                f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}' "
                f"directamente. El siguiente estado válido es "
                f"'{ServiciosLogica.FLUJO_ESTADOS[posicion_actual + 1]}'."
            )

        empleado_final = orden["empleado_id"]
        if empleado_final is None:
            if not empleado_id:
                raise ValueError("Debe indicar el empleado responsable antes de continuar.")
            empleado = EmpleadosDatos.obtener_empleado_por_id(empleado_id)
            if empleado is None or empleado["activo"] != 1:
                raise ValueError("El empleado seleccionado no existe o no está activo.")
            empleado_final = empleado_id

        OrdenesDatos.actualizar_estado(orden_id, nuevo_estado, empleado_final)