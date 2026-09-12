import os
import sqlite3


def obtener_conexion():
  # Asegura que siempre se use la misma ruta de base de datos
  db_path = os.path.join(os.path.dirname(__file__), "autowash.db")
  return sqlite3.connect(db_path)


def inicializar_db():
  conexion = obtener_conexion()
  cursor = conexion.cursor()

  # 1. Tabla de lavados
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS lavados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo_vehiculo TEXT NOT NULL,
            tipo_lavado TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)

  # 2. Tabla de usuarios
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

  # Insertar usuario administrador por defecto
  cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, password) 
        VALUES ('admin', '1234')
    """)

  conexion.commit()
  conexion.close()