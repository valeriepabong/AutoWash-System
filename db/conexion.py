import os
import sqlite3


def obtener_conexion():
    db_path = os.path.join(os.path.dirname(__file__), "autowash.db")
    conexion = sqlite3.connect(db_path)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def _crear_insumos_por_defecto():
    pass


def inicializar_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL UNIQUE,
            marca TEXT,
            modelo TEXT,
            tipo_vehiculo TEXT NOT NULL,
            cliente_id INTEGER NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            precio REAL NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehiculo_id INTEGER NOT NULL,
            empleado_id INTEGER,
            fecha_hora TEXT NOT NULL,
            total REAL NOT NULL DEFAULT 0,
            estado TEXT NOT NULL DEFAULT 'espera',
            FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
            FOREIGN KEY (empleado_id) REFERENCES empleados(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden_servicio_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            servicio_id INTEGER NOT NULL,
            precio_aplicado REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id),
            FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            unidad_medida TEXT NOT NULL,
            stock_actual REAL NOT NULL DEFAULT 0,
            stock_minimo REAL NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id INTEGER NOT NULL,
            tipo_movimiento TEXT NOT NULL,
            cantidad REAL NOT NULL,
            fecha_hora TEXT NOT NULL,
            orden_id INTEGER,
            motivo TEXT,
            FOREIGN KEY (insumo_id) REFERENCES insumos(id),
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicio_insumo (
            servicio_id INTEGER NOT NULL,
            insumo_id INTEGER NOT NULL,
            cantidad_consumida REAL NOT NULL,
            PRIMARY KEY (servicio_id, insumo_id),
            FOREIGN KEY (servicio_id) REFERENCES servicios(id),
            FOREIGN KEY (insumo_id) REFERENCES insumos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL UNIQUE,
            metodo_pago TEXT NOT NULL,
            total REAL NOT NULL,
            fecha_hora TEXT NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id)
        )
    """)

    conexion.commit()
    conexion.close()

    _migrar_estados_legacy()
    _crear_admin_por_defecto()
    _crear_servicios_por_defecto()
    _crear_insumos_por_defecto()


def _migrar_estados_legacy():
    """
    Compatibilidad con bases de datos creadas antes de este sprint, cuando
    'ordenes_servicio.estado' solo tenía 'pendiente' / 'finalizado'.
    Si alguien ya tiene un autowash.db con esos valores, los actualiza a la
    nueva nomenclatura de 4 estados en vez de dejarlos "atascados".
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE ordenes_servicio SET estado = 'espera' WHERE estado = 'pendiente'")
    cursor.execute("UPDATE ordenes_servicio SET estado = 'entregado' WHERE estado = 'finalizado'")
    conexion.commit()
    conexion.close()


def _crear_admin_por_defecto():
    """Crea un usuario admin/admin123 si la tabla usuarios está vacía."""
    from logica.login_logica import LoginLogica
    LoginLogica.crear_usuario_admin_si_no_existe()


def _crear_servicios_por_defecto():
    """Crea un catálogo básico de servicios si la tabla está vacía."""
    from logica.servicios_logica import ServiciosLogica
    ServiciosLogica.crear_catalogo_por_defecto_si_no_existe()

    def _crear_insumos_por_defecto(InventarioLogica=None):
        """Crea un catálogo básico de insumos y sus recetas por servicio, si la tabla está vacía."""
        from logica.inventario_logica import InventarioLogica
        InventarioLogica.crear_catalogo_por_defecto_si_no_existe()