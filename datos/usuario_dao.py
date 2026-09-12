from db.conexion import obtener_conexion


class UsuarioDAO:

  @staticmethod
  def validar_usuario(usuario, password):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario = ? AND password = ?",
        (usuario, password),
    )
    resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None