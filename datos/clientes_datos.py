from db.conexion import obtener_conexion


class ClienteDAO:

  @staticmethod
  def guardar(nombre, telefono, placa):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
            INSERT INTO clientes (nombre, telefono, placa)
            VALUES (?, ?, ?)
        """,
        (nombre, telefono, placa),
    )
    conexion.commit()
    conexion.close()

  @staticmethod
  def obtener_todos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, telefono, placa FROM clientes")
    registros = cursor.fetchall()
    conexion.close()
    return registros

  @staticmethod
  def eliminar_por_id(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conexion.commit()
    conexion.close()