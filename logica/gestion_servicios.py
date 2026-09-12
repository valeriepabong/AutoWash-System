from datos.vehiculo_dao import VehiculoDAO


class ServicioLavado:

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
    return cls.PRECIOS.get(tipo_lavado, {}).get(tipo_vehiculo, 0)

  @classmethod
  def registrar_servicio(cls, placa, tipo_vehiculo, tipo_lavado):
    placa_limpia = placa.strip().upper()
    if not placa_limpia:
      raise ValueError("La placa no puede estar vacía.")

    precio = cls.calcular_precio(tipo_vehiculo, tipo_lavado)
    if precio == 0:
      raise ValueError("Combinación de vehículo y lavado no válida.")

    VehiculoDAO.guardar(placa_limpia, tipo_vehiculo, tipo_lavado, precio)
    return precio

  @classmethod
  def obtener_historial(cls):
    return VehiculoDAO.obtener_todos()

  @classmethod
  def eliminar_servicio(cls, id_lavado):
    """Valida y elimina un registro por su ID."""
    if not id_lavado:
      raise ValueError("Debe seleccionar un registro para eliminar.")
    VehiculoDAO.eliminar_por_id(id_lavado)

  @classmethod
  def actualizar_servicio(
      cls, id_lavado, placa, tipo_vehiculo, tipo_lavado
  ):
    """Valida los nuevos datos y actualiza el servicio."""
    placa_limpia = placa.strip().upper()
    if not placa_limpia:
      raise ValueError("La placa no puede estar vacía.")

    precio = cls.calcular_precio(tipo_vehiculo, tipo_lavado)
    if precio == 0:
      raise ValueError("Combinación de vehículo y lavado no válida.")

    VehiculoDAO.actualizar(
        id_lavado, placa_limpia, tipo_vehiculo, tipo_lavado, precio
    )
    return precio