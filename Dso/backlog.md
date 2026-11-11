# AutoWash System: Resumen del proyecto y backlog

Documento de seguimiento del Sistema de Gestión de Lavadero de Vehículos. Resume el contexto, las decisiones técnicas, lo construido en cada sprint y el estado del backlog.

---

## 1. Contexto del proyecto

Proyecto universitario enfocado en un sistema de escritorio para la administración integral de un lavadero de vehículos (empleados y administrador). El alcance comprende:
- Autenticación y control de usuarios.
- Gestión de clientes y vehículos vinculados.
- Catálogo dinámico de servicios y asignación de operarios.
- Ciclo de vida de órdenes de servicio en 4 estados (`espera`, `proceso`, `listo`, `entregado`).
- Control de inventario de insumos con recetas y descuento atómico de existencias.
- Facturación con múltiples medios de pago y consulta de facturas emitidas.
- Dashboard de reportes (ingresos, servicios más solicitados, consumo de insumos y rendimiento de empleados).

**Metodología:** Scrum.

---

## 2. Stack técnico

- **Lenguaje:** Python 3.10 o superior (compatible con Python 3.12+).
- **Interfaz gráfica:** CustomTkinter / Tkinter (Treeviews nativos estilizados).
- **Base de datos:** SQLite 3 nativo (`sqlite3`), sin dependencias pesadas de ORM.
- **Integridad referencial:** Habilitada mediante `PRAGMA foreign_keys = ON`.
- **Pruebas unitarias:** Módulo nativo `unittest` en suite automatizada (`tests/`).
- **Empaquetado final:** PyInstaller (compatible mediante resolución dinámica de ruta en `obtener_ruta_db()`).
- **Control de versiones:** Git y GitHub.

---

## 3. Arquitectura por capas

```
AutoWash-System/
├── main.py                     # Punto de entrada único del sistema
├── requirements.txt            # Dependencias del proyecto
├── CONTRIBUTING.md             # Guía para colaboradores
├── README.md                   # Documentación general y puesta en marcha
├── Dso/                        # Documentación técnica de desarrollo
│   ├── ARQUITECTURA.md         # Patrón de capas y flujo transaccional detallado
│   ├── der.md                  # DER con las 11 tablas y diccionario de datos
│   ├── backlog.md              # Estado de tareas y sprints
│   └── Documentacion_Sprint_3_y_4.md
├── db/                         # Persistencia
│   ├── autowash.db             # Base de datos SQLite local
│   └── conexion.py             # Conexión centralizada, migración y creación de tablas
├── presentacion/               # Capa 1: Vistas CustomTkinter (UI pura, sin SQL)
├── logica/                     # Capa 2: Reglas de negocio, validaciones y orquestación
├── datos/                      # Capa 3: DAOs con consultas SQL parametrizadas
├── scripts/                    # Utilidades y siembra de datos de prueba
│   └── sembrar_datos_demo.py
└── tests/                      # Suite de pruebas automatizadas
```

**Regla de oro:** Cada capa solo conoce a la de abajo:
$$\text{Presentación} \longrightarrow \text{Lógica} \longrightarrow \text{Datos} \longrightarrow \text{Base de Datos}$$

---

## 4. Histórico de Sprints

### Sprint 1: Autenticación, Clientes y Vehículos
- **Login y Usuarios:** Autenticación con SHA-256 + salt único. Creación automática del usuario `admin` (`admin123`).
- **Clientes:** Registro, actualización, listado y búsqueda insensible a mayúsculas/tildes con borrado lógico (`activo = 0`).
- **Vehículos:** Validación obligatoria y única de placas en mayúsculas, tipo de vehículo y asociación foránea al cliente.

### Sprint 2: Catálogo de Servicios y Empleados
- **Catálogo de Servicios:** Precios fijos preconfigurados (Lavado básico, Lavado completo, Encerado, Aspirado de interiores).
- **Empleados:** Gestión de operarios de lavado con borrado lógico.
- **Órdenes preliminares:** Creación de cabecera y detalle de orden con total calculado.

### Sprints 3 y 4: Estados de Órdenes, Insumos e Inventario
- **Ciclo de Estados:** Estandarización de 4 estados: `espera` $\to$ `proceso` $\to$ `listo` $\to$ `entregado`.
- **Insumos y Recetas:** Creación de tablas `insumos`, `movimientos_inventario` y la tabla intermedia `servicio_insumo` para descontar insumos automáticamente por cada servicio realizado.
- **Alertas de Stock:** Validación de niveles mínimos de insumos.

### Sprint 5: Facturación, Descuento Atómico, Reportes y Estabilización
- **S5-01 / S5-04:** Estandarización de nombres (`reportes_datos.py`, `reportes_logica.py`) e implementación de `obtener_ruta_db()` con variable `AUTOWASH_DB` para pruebas independientes y PyInstaller.
- **S5-03:** Creación del script `scripts/sembrar_datos_demo.py` para generación determinista de escenarios de prueba (clientes, vehículos, órdenes y facturas).
- **S5-07:** Implementación de `listar_ordenes_por_facturar()` y `obtener_detalle_orden()` en `FacturacionLogica`.
- **S5-08:** Orquestación atómica en una única transacción: creación de orden, renglones de detalle, descuento en existencias de insumos y auditoría en Kardex con soporte de `rollback()`.
- **S5-15:** Actualización de documentación técnica (`Dso/der.md` con 11 tablas, `Dso/ARQUITECTURA.md` con ejemplo real transaccional, `CONTRIBUTING.md` y `README.md`).

---

## 5. Modelo de Datos (11 Tablas Oficiales)

1. `usuarios` (id, nombre_usuario, contrasena_hash, salt, activo)
2. `clientes` (id, nombre, telefono, activo)
3. `vehiculos` (id, placa, marca, modelo, tipo_vehiculo, cliente_id, activo)
4. `empleados` (id, nombre, activo)
5. `servicios` (id, nombre, precio, activo)
6. `ordenes_servicio` (id, vehiculo_id, empleado_id, fecha_hora, total, estado)
7. `orden_servicio_detalle` (id, orden_id, servicio_id, precio_aplicado)
8. `insumos` (id, nombre, unidad_medida, stock_actual, stock_minimo, activo)
9. `movimientos_inventario` (id, insumo_id, tipo_movimiento, cantidad, fecha_hora, orden_id, motivo)
10. `servicio_insumo` (servicio_id, insumo_id, cantidad_consumida)
11. `facturas` (id, orden_id, metodo_pago, total, fecha_hora)

---

## 6. Ejecución del Sistema y Pruebas

1. **Instalación de dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```
3. **Poblar datos de prueba:**
   ```bash
   python scripts/sembrar_datos_demo.py
   ```
4. **Ejecutar la suite de pruebas unitarias:**
   ```bash
   python -m unittest discover -s tests
   ```
