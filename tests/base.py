"""
tests/base.py
Clase base para las pruebas de AutoWash System.

setUp:  crea una base de datos SQLite temporal para cada prueba
        (via la variable de entorno AUTOWASH_DB) e inicializa el esquema.
tearDown: borra la BD temporal y restaura el entorno.
"""
import os
import sys
import tempfile
import unittest

# Asegurar que la raiz del proyecto esta en sys.path para que los imports
# del proyecto funcionen al ejecutar los tests desde cualquier directorio.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from db.conexion import inicializar_db


class TestBaseAutoWash(unittest.TestCase):
    """Clase base que provee una BD temporal aislada por prueba."""

    def setUp(self):
        # Crear un archivo temporal que servira como BD de esta prueba
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)  # Cerrar el descriptor; sqlite3 lo maneja solo
        os.environ["AUTOWASH_DB"] = self.db_path
        inicializar_db()

    def tearDown(self):
        # Restaurar el entorno y eliminar la BD temporal
        os.environ.pop("AUTOWASH_DB", None)
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
