from db.conexion import obtener_conexion


class VehiculoDAO:

  @staticmethod
  def guardar_registro(placa, tipo_vehiculo, tipo_lavado, precio):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
            INSERT INTO lavados (placa, tipo_vehiculo, tipo_lavado, precio)
            VALUES (?, ?, ?, ?)
        """,
        (placa, tipo_vehiculo, tipo_lavado, precio),
    )
    conexion.commit()
    conexion.close()

  @staticmethod
  def obtener_todos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, placa, tipo_vehiculo, tipo_lavado, precio FROM lavados"
    )
    registros = cursor.fetchall()
    conexion.close()
    return registros
  