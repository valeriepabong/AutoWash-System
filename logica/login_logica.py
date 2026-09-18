import hashlib
import os

from datos.usuarios_datos import UsuariosDatos


class LoginLogica:

    @staticmethod
    def _generar_salt():
        return os.urandom(16).hex()

    @staticmethod
    def _generar_hash(contrasena, salt):
        texto = (contrasena + salt).encode("utf-8")
        return hashlib.sha256(texto).hexdigest()

    @staticmethod
    def crear_usuario(nombre_usuario, contrasena):
        nombre_usuario = (nombre_usuario or "").strip()
        if not nombre_usuario:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía.")

        if UsuariosDatos.obtener_usuario_por_nombre(nombre_usuario) is not None:
            raise ValueError("Ese nombre de usuario ya existe.")

        salt = LoginLogica._generar_salt()
        contrasena_hash = LoginLogica._generar_hash(contrasena, salt)
        UsuariosDatos.insertar_usuario(nombre_usuario, contrasena_hash, salt)

    @staticmethod
    def validar_login(nombre_usuario, contrasena):
        nombre_usuario = (nombre_usuario or "").strip()
        if not nombre_usuario or not contrasena:
            return False

        usuario = UsuariosDatos.obtener_usuario_por_nombre(nombre_usuario)
        if usuario is None:
            return False

        if usuario["activo"] != 1:
            return False

        hash_calculado = LoginLogica._generar_hash(contrasena, usuario["salt"])
        return hash_calculado == usuario["contrasena_hash"]

    @staticmethod
    def iniciar_sesion(nombre_usuario, contrasena):
        """
        Igual que validar_login, pero pensado para pantallas: lanza ValueError
        con mensaje claro si las credenciales son incorrectas, en vez de
        devolver un booleano. Úsalo desde presentacion/login_view.py.
        """
        if not LoginLogica.validar_login(nombre_usuario, contrasena):
            raise ValueError("Usuario o contraseña incorrectos.")

    @staticmethod
    def crear_usuario_admin_si_no_existe():
        if UsuariosDatos.contar_usuarios() == 0:
            LoginLogica.crear_usuario("admin", "admin123")