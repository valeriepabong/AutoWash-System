from datos.vehiculo_dao import VehiculoDAO


class ServicioLavado:

  # Tarifas predefinidas según tipo de lavado y vehículo
  PRECIOS = {
      "Sencillo": {"Automóvil": 15000, "Camioneta": 20000, "Moto": 8000},
      "General": {"Automóvil": 25000, "Camioneta": 35000, "Moto": 15000},
      "Especial (Polichado)": {
          "Automóvil": 50000,
          "Camioneta": 70000,
          "Moto": 30000,
      },
  }

  @classmethod
  def calcular_precio(cls, tipo_vehiculo, tipo_lavado):
    """Calcula el precio del servicio según el vehículo y el tipo de lavado."""
    return cls.PRECIOS.get(tipo_lavado, {}).get(tipo_vehiculo, 0)

  @classmethod
  def registrar_servicio(cls, placa, tipo_vehiculo, tipo_lavado):
    """Valida la placa y registra el servicio en la base de datos a través del DAO."""
    placa_limpia = placa.strip().upper()
    if not placa_limpia:
      raise ValueError("La placa del vehículo no puede estar vacía.")

    precio = cls.calcular_precio(tipo_vehiculo, tipo_lavado)
    VehiculoDAO.guardar_registro(
        placa_limpia, tipo_vehiculo, tipo_lavado, precio
    )
    return precio

  @classmethod
  def obtener_historial(cls):
    """Obtiene el listado completo de servicios registrados."""
    return VehiculoDAO.obtener_todos()