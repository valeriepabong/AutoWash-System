from datos.clientes_datos import (
    insertar_cliente,
    obtener_cliente_por_id,
    listar_clientes,
    buscar_clientes_por_nombre,
    actualizar_cliente,
    desactivar_cliente,
)


def registrar_cliente(nombre, telefono=None):
    """
    Registra un nuevo cliente.
    Lanza ValueError si el nombre es inválido.
    Devuelve el id del cliente creado.
    """
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    telefono = (telefono or "").strip() or None

    return insertar_cliente(nombre, telefono)


def obtener_cliente(cliente_id):
    """Devuelve un cliente por su id, o None si no existe."""
    return obtener_cliente_por_id(cliente_id)


def listar_todos_los_clientes():
    """Devuelve el listado de clientes activos."""
    return listar_clientes(solo_activos=True)


def buscar_clientes(texto_busqueda):
    """
    Busca clientes por nombre (parcial). Si el texto de búsqueda está vacío,
    devuelve el listado completo.
    """
    texto_busqueda = (texto_busqueda or "").strip()
    if not texto_busqueda:
        return listar_clientes(solo_activos=True)
    return buscar_clientes_por_nombre(texto_busqueda)


def editar_cliente(cliente_id, nombre, telefono=None):
    """
    Edita nombre y teléfono de un cliente existente.
    Lanza ValueError si el nombre es inválido o si el cliente no existe.
    """
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    telefono = (telefono or "").strip() or None

    if obtener_cliente_por_id(cliente_id) is None:
        raise ValueError("El cliente no existe.")

    actualizar_cliente(cliente_id, nombre, telefono)


def eliminar_cliente(cliente_id):
    """
    Elimina (lógicamente) un cliente.
    Lanza ValueError si el cliente no existe.
    """
    if obtener_cliente_por_id(cliente_id) is None:
        raise ValueError("El cliente no existe.")

    desactivar_cliente(cliente_id)
