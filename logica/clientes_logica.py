from datos.clientes_datos import ClienteDAO


class ClienteServicio:

  @classmethod
  def registrar_cliente(cls, nombre, telefono, placa):
    nombre_limpio = nombre.strip()
    telefono_limpio = telefono.strip()
    placa_limpia = placa.strip().upper()

    if not nombre_limpio:
      raise ValueError("El nombre del cliente no puede estar vacío.")
    if not telefono_limpio:
      raise ValueError("El teléfono no puede estar vacío.")
    if not placa_limpia:
      raise ValueError("La placa del vehículo no puede estar vacía.")

    ClienteDAO.guardar(nombre_limpio, telefono_limpio, placa_limpia)

  @classmethod
  def obtener_clientes(cls):
    return ClienteDAO.obtener_todos()

  @classmethod
  def eliminar_cliente(cls, id_cliente):
    if not id_cliente:
      raise ValueError("Debe seleccionar un cliente para eliminar.")
    ClienteDAO.eliminar_por_id(id_cliente)