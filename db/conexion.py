import os
import sqlite3


def obtener_conexion():
  db_path = os.path.join(os.path.dirname(__file__), "autowash.db")
  conexion = sqlite3.connect(db_path)
  return conexion


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

  conexion.commit()
  conexion.close()