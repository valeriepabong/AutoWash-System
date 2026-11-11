# AutoWash System

Sistema de escritorio integral para la gestión de lavaderos de vehículos, desarrollado en **Python** con una interfaz moderna en **CustomTkinter** y persistencia en **SQLite**. 

Diseñado bajo una estricta **arquitectura en 3 capas** y enfocado en la confiabilidad de las operaciones, transacciones atómicas para el control de inventarios, facturación y reportes gerenciales.

---

## 🚀 Características Principales

* **Control de Acceso y Seguridad:** Autenticación de usuarios con hashing criptográfico SHA-256 y salting individual.
* **Gestión de Clientes y Vehículos:** Registro y consulta ágil con búsqueda parcial insensible a acentos/mayúsculas y vinculación obligatoria de vehículos por placa.
* **Catálogo de Servicios y Personal:** Gestión de servicios de autolavado con precios configurables y asignación de operarios responsables.
* **Ciclo de Órdenes de Servicio:** Flujo operativo completo a través de cuatro estados: `espera` $\to$ `proceso` $\to$ `listo` $\to$ `entregado`.
* **Control Atómico de Inventario:** Recetas automáticas por servicio (`servicio_insumo`) con descuento automático de existencias en el inventario (`insumos`) y trazabilidad mediante auditoría tipo Kardex (`movimientos_inventario`) con protección contra fallos (`rollback`).
* **Módulo de Facturación:** Liquidación de órdenes de servicio con selección de método de pago (Efectivo, Tarjeta, Transferencia) y consulta de facturas emitidas.
* **Panel de Reportes:** Métricas de facturación total, ticket promedio, servicios más solicitados, consumo de químicos/insumos y rendimiento por empleado.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una separación rigurosa de responsabilidades en 3 capas:

$$\text{Presentación (UI)} \longrightarrow \text{Lógica de Negocio} \longrightarrow \text{Datos (DAO)} \longrightarrow \text{Base de Datos SQLite}$$

```
AutoWash-System/
├── main.py                     # Punto de entrada de la aplicación
├── requirements.txt            # Dependencias del proyecto
├── CONTRIBUTING.md             # Directrices de contribución y ramas
├── README.md                   # Documentación principal
├── Dso/                        # Documentación técnica
│   ├── ARQUITECTURA.md         # Detalle de capas y ejemplo real transaccional
│   ├── der.md                  # DER de las 11 tablas y diccionario de datos
│   ├── backlog.md              # Resumen de sprints y decisiones técnicas
│   └── Documentacion_Sprint_3_y_4.md
├── db/                         # Configuración y conexión de base de datos
│   ├── autowash.db             # Archivo SQLite local
│   └── conexion.py             # DDL de tablas y resolución dinámica de rutas
├── presentacion/               # Capa visual (CustomTkinter)
├── logica/                     # Capa de negocio (validaciones, orquestación)
├── datos/                      # Capa de datos (DAOs con SQL parametrizado)
├── scripts/                    # Scripts utilitarios (siembra de demo)
└── tests/                      # Suite de pruebas automatizadas
```

Para ver la explicación completa del flujo y un ejemplo transaccional de código de extremo a extremo, consulta [Dso/ARQUITECTURA.md](Dso/ARQUITECTURA.md).

---

## 🗄️ Modelo de Base de Datos (DER)

La base de datos consta de **11 tablas relacionales**:

1. `usuarios` (Credenciales seguras)
2. `clientes` (Directorio de clientes)
3. `vehiculos` (Vehículos registrados y propietarios)
4. `empleados` (Personal del lavadero)
5. `servicios` (Catálogo comercial)
6. `ordenes_servicio` (Cabecera de órdenes de trabajo)
7. `orden_servicio_detalle` (Servicios contratados en cada orden)
8. `insumos` (Stock y niveles mínimos de químicos/productos)
9. `movimientos_inventario` (Kardex de entradas, salidas y consumos)
10. `servicio_insumo` (Recetas: relación N:M entre servicios e insumos requeridos)
11. `facturas` (Comprobantes fiscales de órdenes pagadas)

El diagrama completo con las relaciones de cardinalidad y el diccionario de datos detallado se encuentra en [Dso/der.md](Dso/der.md).

---

## ⚙️ Requisitos e Instalación

### Requisitos previos
* **Python 3.10 o superior** (probado en Python 3.12).
* Gestor de paquetes `pip`.

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/valeriepabong/AutoWash-System.git
cd AutoWash-System
```

### Paso 2: Crear y activar el entorno virtual
En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🚦 Puesta en Marcha

### 1. Iniciar la aplicación
Ejecuta el archivo principal desde la raíz del proyecto:
```bash
python main.py
```

### 2. Credenciales por defecto
Al iniciar por primera vez, el sistema autogenera la base de datos y un usuario administrador predeterminado:
* **Usuario:** `admin`
* **Contraseña:** `admin123`

### 3. Siembra de datos de prueba (Opcional)
Para cargar datos de demostración (clientes, vehículos, insumos, órdenes y facturas simuladas para probar reportes):
```bash
python scripts/sembrar_datos_demo.py --forzar
```

---

## 🧪 Pruebas Automatizadas

El proyecto incluye una suite de pruebas unitarias para validar la integridad del esquema, transacciones atómicas con rollback y contratos de facturación:

```bash
python -m unittest discover -s tests
```

---

## 🤝 Contribución

Por favor, consulta el archivo [CONTRIBUTING.md](CONTRIBUTING.md) para conocer las pautas de estilo, convención de nombres de ramas, mensajes de commit y el flujo de trabajo para Pull Requests.
