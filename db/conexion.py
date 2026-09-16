import os
import sqlite3


def obtener_conexion():
    db_path = os.path.join(os.path.dirname(__file__), "autowash.db")
    conexion = sqlite3.connect(db_path)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

# Tabla de lavados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lavados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo_vehiculo TEXT NOT NULL,
            tipo_lavado TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)

    # Tabla de vehículos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            placa TEXT NOT NULL UNIQUE,
            tipo_vehiculo TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    conexion.commit()
    conexion.close()

    _crear_admin_por_defecto()


def _crear_admin_por_defecto():
    """Crea un usuario admin/admin123 si la tabla usuarios está vacía."""
    from logica.login_logica import crear_usuario_admin_si_no_existe
    crear_usuario_admin_si_no_existe()
