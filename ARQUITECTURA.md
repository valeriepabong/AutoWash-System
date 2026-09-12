Arquitectura por Capas - AutoWash System

 Flujo de Datos y Reglas
El proyecto sigue una arquitectura en 3 capas. La comunicación es unidireccional:

Presentación (UI) -> Lógica (Servicios) -> Datos (DAO) -> Base de Datos

resentación (`presentacion/`): Solo maneja la interfaz de usuario. Llama a la capa de Lógica.
Lógica (`logica/`): Valida reglas de negocio. Llama a la capa de Datos.
Datos (`datos/`): Ejecuta consultas SQL en la base de datos (`db/`).
Regla:La interfaz gráfica NUNCA debe hacer consultas SQL ni conectarse directamente a la base de datos.

## Ejemplo de uso (Molde)

1. Datos (`datos/vehiculo_dao.py`):

```python
from db.conexion import obtener_conexion

class VehiculoDAO:
    @staticmethod
    def contar_registros():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM lavados")
        total = cursor.fetchone()[0]
        conexion.close()
        return total