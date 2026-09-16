from datos.vehiculos_datos import VehiculoDAO


class VehiculoLogica:

    @staticmethod
    def registrar_vehiculo(marca, modelo, placa, tipo_vehiculo):

        marca = marca.strip()
        modelo = modelo.strip()
        placa = placa.strip().upper()
        tipo_vehiculo = tipo_vehiculo.strip()

        if not marca:
            raise ValueError("La marca del vehículo es obligatoria.")

        if not modelo:
            raise ValueError("El modelo del vehículo es obligatorio.")

        if not placa:
            raise ValueError("La placa del vehículo es obligatoria.")

        if not tipo_vehiculo:
            raise ValueError("El tipo de vehículo es obligatorio.")

        VehiculoDAO.registrar(
            marca,
            modelo,
            placa,
            tipo_vehiculo
        )


    @staticmethod
    def obtener_vehiculos():
        return VehiculoDAO.obtener_todos()


    @staticmethod
    def actualizar_vehiculo(
        id_vehiculo,
        marca,
        modelo,
        placa,
        tipo_vehiculo
    ):

        marca = marca.strip()
        modelo = modelo.strip()
        placa = placa.strip().upper()
        tipo_vehiculo = tipo_vehiculo.strip()

        if not marca:
            raise ValueError("La marca del vehículo es obligatoria.")

        if not modelo:
            raise ValueError("El modelo del vehículo es obligatorio.")

        if not placa:
            raise ValueError("La placa del vehículo es obligatoria.")

        if not tipo_vehiculo:
            raise ValueError("El tipo de vehículo es obligatorio.")

        VehiculoDAO.actualizar(
            id_vehiculo,
            marca,
            modelo,
            placa,
            tipo_vehiculo
        )


    @staticmethod
    def eliminar_vehiculo(id_vehiculo):
        VehiculoDAO.eliminar(id_vehiculo)
