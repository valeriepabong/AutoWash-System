import os
import sqlite3


def obtener_conexion():
  db_path = os.path.join(os.path.dirname(__file__), "autowash.db")
  return sqlite3.connect(db_path)


def inicializar_db():
  conexion = obtener_conexion()
  cursor = conexion.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS lavados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo_vehiculo TEXT NOT NULL,
            tipo_lavado TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

  cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, password) 
        VALUES ('admin', '1234')
    """)

  conexion.commit()
  conexion.close()