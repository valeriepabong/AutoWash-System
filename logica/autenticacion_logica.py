from datos.usuario_dao import UsuarioDAO


class AutenticacionServicio:

  @classmethod
  def iniciar_sesion(cls, usuario, password):
    usuario_clean = usuario.strip()
    password_clean = password.strip()

    if not usuario_clean or not password_clean:
      raise ValueError("El usuario y la contraseña son obligatorios.")

    es_valido = UsuarioDAO.validar_usuario(usuario_clean, password_clean)
    if not es_valido:
      raise ValueError("Usuario o contraseña incorrectos.")

    return True