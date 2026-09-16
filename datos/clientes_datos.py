from db.conexion import obtener_conexion


def insertar_cliente(nombre, telefono):
    """Inserta un nuevo cliente y devuelve el id generado."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO clientes (nombre, telefono, activo)
        VALUES (?, ?, 1)
        """,
        (nombre, telefono),
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()
    return nuevo_id


def obtener_cliente_por_id(cliente_id):
    """Devuelve un dict con los datos del cliente, o None si no existe."""
    conexion = obtener_conexion()
    conexion.row_factory = _dict_factory
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, telefono, activo FROM clientes WHERE id = ?",
        (cliente_id,),
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def listar_clientes(solo_activos=True):
    """Devuelve la lista completa de clientes (activos por defecto)."""
    conexion = obtener_conexion()
    conexion.row_factory = _dict_factory
    cursor = conexion.cursor()
    if solo_activos:
        cursor.execute(
            "SELECT id, nombre, telefono, activo FROM clientes WHERE activo = 1 ORDER BY nombre"
        )
    else:
        cursor.execute(
            "SELECT id, nombre, telefono, activo FROM clientes ORDER BY nombre"
        )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def buscar_clientes_por_nombre(texto_busqueda):
    """Busca clientes activos cuyo nombre contenga el texto dado (parcial, sin importar mayúsculas)."""
    conexion = obtener_conexion()
    conexion.row_factory = _dict_factory
    cursor = conexion.cursor()
    patron = f"%{texto_busqueda}%"
    cursor.execute(
        """
        SELECT id, nombre, telefono, activo
        FROM clientes
        WHERE activo = 1 AND nombre LIKE ? COLLATE NOCASE
        ORDER BY nombre
        """,
        (patron,),
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def actualizar_cliente(cliente_id, nombre, telefono):
    """Actualiza nombre y teléfono de un cliente existente."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?",
        (nombre, telefono, cliente_id),
    )
    filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0


def desactivar_cliente(cliente_id):
    """Borrado lógico: marca al cliente como inactivo en vez de eliminarlo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE clientes SET activo = 0 WHERE id = ?",
        (cliente_id,),
    )
    filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0


def _dict_factory(cursor, fila):
    columnas = [descripcion[0] for descripcion in cursor.description]
    return dict(zip(columnas, fila))
