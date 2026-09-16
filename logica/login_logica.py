import hashlib
import os

from datos.usuarios_datos import (
    obtener_usuario_por_nombre,
    insertar_usuario,
    contar_usuarios,
)


def _generar_salt():
    """Genera un salt aleatorio en formato hexadecimal."""
    return os.urandom(16).hex()


def _generar_hash(contrasena, salt):
    """Combina contraseña + salt y calcula el hash SHA-256."""
    texto = (contrasena + salt).encode("utf-8")
    return hashlib.sha256(texto).hexdigest()


def crear_usuario(nombre_usuario, contrasena):
    """
    Crea un nuevo usuario con contraseña hasheada.
    Lanza ValueError si el nombre de usuario o la contraseña son inválidos,
    o si el nombre de usuario ya existe.
    """
    nombre_usuario = (nombre_usuario or "").strip()
    if not nombre_usuario:
        raise ValueError("El nombre de usuario no puede estar vacío.")
    if not contrasena:
        raise ValueError("La contraseña no puede estar vacía.")

    if obtener_usuario_por_nombre(nombre_usuario) is not None:
        raise ValueError("Ese nombre de usuario ya existe.")

    salt = _generar_salt()
    contrasena_hash = _generar_hash(contrasena, salt)
    insertar_usuario(nombre_usuario, contrasena_hash, salt)


def validar_login(nombre_usuario, contrasena):
    """
    Valida las credenciales del usuario.
    Devuelve True si son correctas, False en caso contrario.
    No lanza excepción por credenciales incorrectas (eso es un resultado
    normal del login, no un error del sistema).
    """
    nombre_usuario = (nombre_usuario or "").strip()
    if not nombre_usuario or not contrasena:
        return False

    usuario = obtener_usuario_por_nombre(nombre_usuario)
    if usuario is None:
        return False

    if usuario["activo"] != 1:
        return False

    hash_calculado = _generar_hash(contrasena, usuario["salt"])
    return hash_calculado == usuario["contrasena_hash"]


def crear_usuario_admin_si_no_existe():
    """
    Crea el usuario admin por defecto SOLO si la tabla usuarios está vacía.
    Se llama una vez al inicializar la base de datos.
    """
    if contar_usuarios() == 0:
        crear_usuario("admin", "admin123")
