from db.conexion import obtener_conexion


class VehiculoDAO:

  @staticmethod
  def guardar(placa, tipo_vehiculo, tipo_lavado, precio):
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

  @staticmethod
  def eliminar_por_id(id_lavado):
    """Elimina un registro de la base de datos según su ID."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM lavados WHERE id = ?", (id_lavado,))
    conexion.commit()
    conexion.close()

  @staticmethod
  def actualizar(id_lavado, placa, tipo_vehiculo, tipo_lavado, precio):
    """Actualiza un registro existente en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
            UPDATE lavados
            SET placa = ?, tipo_vehiculo = ?, tipo_lavado = ?, precio = ?
            WHERE id = ?
        """,
        (placa, tipo_vehiculo, tipo_lavado, precio, id_lavado),
    )
    conexion.commit()
    conexion.close()