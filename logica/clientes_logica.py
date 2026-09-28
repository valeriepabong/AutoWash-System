from datos.clientes_datos import ClientesDatos


class ClientesLogica:

    @staticmethod
    def registrar_cliente(nombre, telefono=None):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del cliente es obligatorio.")

        telefono = (telefono or "").strip() or None
        return ClientesDatos.insertar_cliente(nombre, telefono)

    @staticmethod
    def obtener_cliente(cliente_id):
        return ClientesDatos.obtener_cliente_por_id(cliente_id)

    @staticmethod
    def listar_todos_los_clientes():
        return ClientesDatos.listar_clientes(solo_activos=True)

    @staticmethod
    def buscar_clientes(texto_busqueda):
        texto_busqueda = (texto_busqueda or "").strip()
        if not texto_busqueda:
            return ClientesDatos.listar_clientes(solo_activos=True)
        return ClientesDatos.buscar_clientes_por_nombre(texto_busqueda)

    @staticmethod
    def editar_cliente(cliente_id, nombre, telefono=None):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del cliente es obligatorio.")

        telefono = (telefono or "").strip() or None

        if ClientesDatos.obtener_cliente_por_id(cliente_id) is None:
            raise ValueError("El cliente no existe.")

        ClientesDatos.actualizar_cliente(cliente_id, nombre, telefono)

    @staticmethod
    def eliminar_cliente(cliente_id):
        if ClientesDatos.obtener_cliente_por_id(cliente_id) is None:
            raise ValueError("El cliente no existe.")
        ClientesDatos.desactivar_cliente(cliente_id)
