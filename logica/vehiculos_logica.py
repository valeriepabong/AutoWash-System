from datos.vehiculos_datos import VehiculosDatos
from datos.clientes_datos import ClientesDatos


class VehiculosLogica:

    @staticmethod
    def registrar_vehiculo(placa, tipo_vehiculo, cliente_id, marca=None, modelo=None):
        placa = (placa or "").strip().upper()
        tipo_vehiculo = (tipo_vehiculo or "").strip()

        if not placa:
            raise ValueError("La placa del vehículo es obligatoria.")
        if not tipo_vehiculo:
            raise ValueError("El tipo de vehículo es obligatorio.")
        if not cliente_id:
            raise ValueError("Debe asociar el vehículo a un cliente.")

        if ClientesDatos.obtener_cliente_por_id(cliente_id) is None:
            raise ValueError("El cliente seleccionado no existe.")

        if VehiculosDatos.obtener_vehiculo_por_placa(placa) is not None:
            raise ValueError(f"Ya existe un vehículo registrado con la placa {placa}.")

        marca = (marca or "").strip() or None
        modelo = (modelo or "").strip() or None

        return VehiculosDatos.insertar_vehiculo(placa, tipo_vehiculo, cliente_id, marca, modelo)

    @staticmethod
    def obtener_vehiculos():
        return VehiculosDatos.listar_vehiculos_con_cliente(solo_activos=True)

    @staticmethod
    def obtener_vehiculos_de_cliente(cliente_id):
        return VehiculosDatos.listar_vehiculos_por_cliente(cliente_id)

    @staticmethod
    def actualizar_vehiculo(vehiculo_id, placa, tipo_vehiculo, cliente_id, marca=None, modelo=None):
        placa = (placa or "").strip().upper()
        tipo_vehiculo = (tipo_vehiculo or "").strip()

        if not placa:
            raise ValueError("La placa del vehículo es obligatoria.")
        if not tipo_vehiculo:
            raise ValueError("El tipo de vehículo es obligatorio.")

        if ClientesDatos.obtener_cliente_por_id(cliente_id) is None:
            raise ValueError("El cliente seleccionado no existe.")

        existente = VehiculosDatos.obtener_vehiculo_por_placa(placa)
        if existente is not None and existente["id"] != vehiculo_id:
            raise ValueError(f"Ya existe otro vehículo con la placa {placa}.")

        marca = (marca or "").strip() or None
        modelo = (modelo or "").strip() or None

        VehiculosDatos.actualizar_vehiculo(vehiculo_id, placa, tipo_vehiculo, cliente_id, marca, modelo)

    @staticmethod
    def eliminar_vehiculo(vehiculo_id):
        if VehiculosDatos.obtener_vehiculo_por_id(vehiculo_id) is None:
            raise ValueError("El vehículo no existe.")
        VehiculosDatos.desactivar_vehiculo(vehiculo_id)