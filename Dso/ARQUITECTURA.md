# Arquitectura por Capas - AutoWash System

## Flujo de Datos y Reglas
El proyecto sigue una arquitectura estricta en 3 capas. La comunicación es unidireccional y secuencial:

**Presentación (`presentacion/`)** $\to$ **Lógica (`logica/`)** $\to$ **Datos (`datos/`)** $\to$ **Base de Datos (`db/`)**

1. **Presentación (`presentacion/`):** Solo maneja la interfaz de usuario (CustomTkinter / Treeview). Captura eventos, muestra datos y **llama únicamente a la capa de Lógica**.
2. **Lógica (`logica/`):** Contiene y valida todas las reglas de negocio del sistema (ej. estados de órdenes, validación de campos obligatorios, cálculos). **Llama a la capa de Datos**.
3. **Datos (`datos/`):** Capa DAO (Data Access Object) que ejecuta de manera exclusiva las consultas y comandos SQL sobre la base de datos SQLite (`db/conexion.py`).

> **Regla de Oro:** La interfaz gráfica (Presentación) **NUNCA** debe hacer consultas SQL, importar módulos de conexión directamente ni manipular la base de datos.

---

## Ejemplo de Flujo Completo (Módulo de Vehículos)

### 1. Capa de Presentación (`presentacion/vehiculos_screen.py`)
La vista captura los datos ingresados por el usuario y se comunica con la lógica:
```python
from logica.vehiculos_logica import VehiculosLogica

def _registrar(self):
    placa = self.txt_placa.get().strip()
    tipo = self.cb_tipo.get()
    cliente_id = int(self.cb_clientes.get().split(" - ")[0])
    
    # La vista llama a la Lógica (nunca a la BD ni al DAO directo)
    exito, msg = VehiculosLogica.crear_vehiculo(placa, None, None, tipo, cliente_id)