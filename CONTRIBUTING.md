# Guía de Contribución - AutoWash System

¡Gracias por contribuir a **AutoWash System**! Para mantener un código limpio, robusto y mantenible, todos los colaboradores deben seguir estas pautas.

---

## 1. Convención de Ramas Git

El flujo de trabajo se basa en ramas temáticas organizadas por sprints o características:

* Rama principal: `main` (código de producción probado y estable).
* Ramas de trabajo:
  * Sprints y módulos: `sprint<N>/<modulo>` (ej. `sprint5/backend`, `sprint5/frontend`).
  * Tareas específicas o correcciones: `feature/<nombre-tarea>` o `bugfix/<nombre-error>`.

```bash
# Crear y cambiarse a una nueva rama
git checkout -b sprint5/mi-tarea
```

---

## 2. Convención de Mensajes de Commit

Los mensajes de commit deben ser descriptivos y, cuando aplique, comenzar con el identificador del backlog (ej. `S5-XX`):

* `S5-08: Orquestar creación de orden y descuento de inventario en una sola transacción`
* `S5-15: Actualizar DER a 11 tablas y completar ejemplo de arquitectura`
* `docs: Actualizar README con guía de instalación y pruebas`
* `fix: Corregir cálculo de totales en pantalla de facturación`

---

## 3. Reglas de Arquitectura y Estilo de Código

El proyecto implementa una **Arquitectura en 3 Capas Estricta**:
`Presentación (UI)` $\to$ `Lógica de Negocio` $\to$ `Datos (DAO)` $\to$ `Base de Datos`

1. **Separación de responsabilidades:**
   * **Presentación (`presentacion/`):** Solo componentes de UI (CustomTkinter) y eventos. **Queda estrictamente prohibido importar SQLite o ejecutar SQL desde la vista.**
   * **Lógica (`logica/`):** Valida reglas de negocio, coordina llamadas a la capa de datos y devuelve tuplas `(exito: bool, mensaje: str, ...)`.
   * **Datos (`datos/`):** Único lugar donde residen las consultas SQL. Siempre usar parámetros parametrizados `?` para evitar inyecciones SQL.
2. **Atomicidad Transaccional:**
   * Operaciones compuestas (ej. crear orden + registrar detalles + descontar insumos) deben ejecutarse dentro de un bloque `try...except` con `conexion.commit()` y `conexion.rollback()`.
3. **Manejo de Rutas:**
   * Usar siempre `db.conexion.obtener_ruta_db()` para acceder al archivo de la base de datos, garantizando compatibilidad con entornos de prueba y empaquetado PyInstaller.

---

## 4. Ejecución de Pruebas Unitarias

Antes de realizar `commit` o abrir un Pull Request, es **obligatorio** verificar que la suite completa de pruebas unitarias pase satisfactoriamente:

```bash
# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ejecutar todas las pruebas unitarias
python -m unittest discover -s tests
```

Todas las pruebas deben concluir con `OK`. Si agregas una nueva funcionalidad o servicio, debes incluir su respectivo archivo de pruebas en la carpeta `tests/`.

---

## 5. Proceso de Pull Request (PR)

1. Asegúrate de tener tu rama actualizada con los últimos cambios de `main`:
   ```bash
   git fetch origin
   git merge origin/main
   ```
2. Ejecuta las pruebas unitarias (`python -m unittest discover -s tests`).
3. Sube tu rama al repositorio remoto:
   ```bash
   git push origin sprint<N>/tu-rama
   ```
4. Abre un Pull Request hacia `main` describiendo:
   * Qué cambios se introdujeron.
   * Qué tarea o requerimiento del backlog resuelve.
   * Evidencia de las pruebas ejecutadas.
