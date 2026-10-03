# AutoWash System: Resumen del proyecto y avances

Documento de seguimiento del Sistema de Gestión de Lavadero de Vehículos. Resume el contexto, las decisiones técnicas, lo que ya se construyó en cada sprint y lo que sigue pendiente.

---

## 1. Contexto del proyecto

Proyecto universitario en equipo de 6 personas. El sistema es de uso interno para un solo local (empleados y administrador), sin portal para clientes finales. El alcance de gestión es completo: servicios, clientes, empleados, inventario, facturación y reportes.

Metodología: Scrum.

## 2. Stack técnico

- Lenguaje: Python 3.12 o superior
- Interfaz gráfica: CustomTkinter (aplicación de escritorio)
- Base de datos: SQLite con el módulo `sqlite3`, sin ORM
- Empaquetado final: PyInstaller (genera un .exe)
- Control de versiones: Git y GitHub
- Editor: Visual Studio Code y PyCharm según el integrante

## 3. Arquitectura por capas

```
AutoWash-System/
├── main.py            punto de entrada único
├── requirements.txt
├── presentacion/      pantallas (CustomTkinter)
├── logica/            reglas de negocio y validaciones
├── datos/             acceso a datos (SQL puro)
└── db/
    └── conexion.py    conexión y creación de tablas
```

Regla de oro: cada capa solo conoce a la de abajo. La presentación llama a la lógica, la lógica llama a datos, y datos llama a la conexión. La interfaz nunca ve SQL.

Convención acordada para todo el backend: clases con métodos estáticos (por ejemplo `ClientesLogica.registrar_cliente(...)`), nombres de archivo en la forma `algo_logica.py` y `algo_datos.py`. Los registros se devuelven como diccionarios, no como tuplas.

## 4. Lo que pasó al inicio del Sprint 1 (lecciones aprendidas)

Durante el arranque hubo un problema de coordinación: existían archivos duplicados que hacían lo mismo con nombres distintos (por ejemplo dos versiones de login, dos archivos de conexión y dos versiones del módulo de vehículos). Además, alguien había reintroducido contraseñas en texto plano y una tabla vieja llamada `lavados`.

Se resolvió así:

- Se eliminaron los archivos duplicados y el código muerto.
- Se dejó `db/conexion.py` como único archivo oficial de conexión.
- Se estandarizó todo el backend al estilo de clases con métodos estáticos.
- Se eliminó la tabla `lavados` y el módulo que dependía de ella.
- Se corrigió el `.gitignore`, que apuntaba a `.venv/` cuando la carpeta real se llama `venv/`, y que además no excluía los archivos `.db`.

Lecciones para el equipo:

- Antes de modificar archivos de `logica/` o `datos/`, avisar a quien es responsable de esa capa.
- Nunca subir `venv/`, archivos `.db`, `.idea/` ni `.vscode/` a GitHub.
- Si el esquema de una tabla cambia, hay que borrar el archivo `autowash.db` local para que se regenere, porque `CREATE TABLE IF NOT EXISTS` no modifica tablas que ya existen.
- Nunca ejecutar directamente archivos de `logica/` o `datos/`. Siempre se corre `main.py` desde la raíz del proyecto (en PyCharm, marcando la raíz como Sources Root).

## 5. Sprint 1: completado

Objetivo: login, clientes, vehículos y la base para asignar servicios.

**HU17, Login básico.** Terminada y probada.
- Validación de usuario y contraseña, con bloqueo de acceso sin login.
- Las contraseñas se guardan con hash SHA-256 más un salt aleatorio por usuario, nunca en texto plano.
- Al iniciar la aplicación por primera vez se crea automáticamente el usuario `admin` con contraseña `admin123`, solo si la tabla de usuarios está vacía.
- Acceso único para todos, sin roles diferenciados.

**HU05, Registrar y consultar clientes.** Terminada y probada.
- El nombre es obligatorio y el teléfono es opcional.
- Se permiten nombres repetidos, porque dos clientes distintos pueden llamarse igual. El cliente se identifica por su id.
- Listado ordenado alfabéticamente y búsqueda parcial que ignora mayúsculas y tildes (buscar "gom" encuentra "Gómez").
- El borrado es lógico: el cliente se marca como inactivo para no perder su historial.

**HU01, Registrar ingreso de vehículo.** Terminada y probada.
- La placa es obligatoria y única, y se guarda en mayúsculas.
- El tipo de vehículo es obligatorio. Marca y modelo son opcionales.
- Cada vehículo pertenece obligatoriamente a un cliente, y se valida que ese cliente exista.
- En pantalla, el cliente se elige desde un desplegable de clientes ya registrados, para evitar duplicados por errores de tipeo.

**Frontend del Sprint 1.** Pantallas de login, dashboard, clientes y vehículos, conectadas desde `main.py` con navegación por callbacks (login, luego dashboard, luego clientes o vehículos).

## 6. Base de datos actual

Tablas del Sprint 1:

- `usuarios`: id, nombre_usuario (único), contrasena_hash, salt, activo.
- `clientes`: id, nombre, telefono, activo.
- `vehiculos`: id, placa (única), marca, modelo, tipo_vehiculo, cliente_id (llave foránea a clientes), activo.

Tablas del Sprint 2:

- `empleados`: id, nombre, activo.
- `servicios`: id, nombre (único), precio, activo. Es el catálogo de servicios con precio fijo.
- `ordenes_servicio`: id, vehiculo_id, empleado_id (opcional hasta finalizar), fecha_hora, total, estado (pendiente o finalizado).
- `orden_servicio_detalle`: id, orden_id, servicio_id, precio_aplicado. Es la tabla intermedia que permite varios servicios en una misma orden.

Relaciones principales:

- Un cliente puede tener muchos vehículos.
- Un vehículo puede tener muchas órdenes de servicio.
- Una orden puede incluir muchos servicios, a través de la tabla de detalle.
- Un empleado puede finalizar muchas órdenes.
- `usuarios` no se relaciona con las demás tablas a propósito, porque el login es independiente del negocio.

Decisiones de diseño importantes:

- Se guarda `precio_aplicado` en el detalle como copia del precio del momento. Así, si el precio del catálogo sube después, las órdenes históricas no cambian.
- Todas las tablas usan borrado lógico con la columna `activo`.
- Las llaves foráneas están activadas con `PRAGMA foreign_keys = ON`.
- La orden y su detalle se crean en una sola transacción. Si algo falla, se deshace todo y no queda una orden a medias.

## 7. Sprint 2: avance actual

Objetivo: asignar servicios a un vehículo y manejar empleados.

Reglas de negocio acordadas:

- Un vehículo puede recibir varios servicios en una misma visita.
- Los precios son fijos y vienen del catálogo; el empleado no los edita al asignar.
- La fecha y hora se registran automáticamente al crear la orden.
- El total se calcula automáticamente sumando los precios del catálogo, nunca se toma de la pantalla.
- Se debe seleccionar al menos un servicio.
- El flujo es en dos pasos: primero se crea la orden con vehículo y servicios (estado pendiente, sin empleado), y al terminar se finaliza indicando el empleado responsable.

Backend construido y probado en un entorno de pruebas:

- `datos/servicios_datos.py`: operaciones sobre el catálogo de servicios.
- `datos/empleados_datos.py`: registro, consulta y desactivación de empleados, y conteo de servicios realizados.
- `datos/ordenes_datos.py`: creación transaccional de la orden con su detalle, consultas con nombre de vehículo y empleado, y finalización.
- `logica/servicios_logica.py`: catálogo con servicios por defecto (Lavado básico, Lavado completo, Encerado, Aspirado de interiores), asignación de servicios con todas las validaciones, y finalización de órdenes.
- `logica/empleados_logica.py`: registro y consulta de empleados y de sus servicios realizados.

Validaciones ya cubiertas y probadas:

- No se puede asignar servicio sin seleccionar al menos uno.
- No se puede asignar servicio a un vehículo inexistente.
- El total se calcula correctamente (por ejemplo, Lavado básico más Encerado da 35.000).
- No se puede finalizar una orden que ya está finalizada.
- No se puede finalizar sin un empleado válido y activo.

## 8. Reparto de trabajo

- **Backend (esta parte):** tablas, repositorios de datos y lógica de negocio de login, clientes, vehículos, servicios, empleados y órdenes.
- **Otro desarrollador:** el flujo de cambio de estado del servicio (espera, proceso, terminado, entregado) con validación de que no se salten estados. Es un concepto distinto del estado actual pendiente o finalizado, que solo indica si la orden ya tiene empleado asignado.
- **Frontend:** pantallas de asignar servicio, finalizar servicio y empleados.

Punto de coordinación importante: el flujo de cuatro estados probablemente agregará una columna a `ordenes_servicio`. Conviene avisar antes de tocar `db/conexion.py` o `datos/ordenes_datos.py`, y acordar entre todos si la columna va en la misma tabla o en una aparte, para no repetir el problema de esquemas paralelos.

## 9. Pendiente y próximos pasos

- Confirmar que los archivos del Sprint 2 ya estén integrados en el repositorio real y que la aplicación arranque sin errores con la base de datos regenerada.
- Pantalla de asignar servicio (lista de servicios con selección múltiple y total visible).
- Pantalla de finalizar servicio (órdenes pendientes y selector de empleado).
- Pantalla de empleados.
- Agregar el botón de volver al dashboard en la pantalla de vehículos, para que la navegación sea consistente con la de clientes.
- Flujo de cuatro estados del servicio (responsable: otro desarrollador).
- Módulos que aún no se han empezado: inventario con descuento automático y alertas de stock bajo, facturación con método de pago, y reportes de ingresos, servicios más solicitados y consumo de insumos.
- Documentar y presentar el diagrama entidad-relación actualizado con las tablas del Sprint 2.

## 10. Cómo ejecutar el proyecto

1. Abrir la carpeta raíz `AutoWash-System` en el editor.
2. Activar el entorno virtual e instalar dependencias con `pip install -r requirements.txt`.
3. Si hubo cambios de esquema, borrar el archivo `db/autowash.db` local para que se regenere.
4. Ejecutar siempre `main.py` desde la raíz del proyecto.
5. Ingresar con el usuario `admin` y la contraseña `admin123`.