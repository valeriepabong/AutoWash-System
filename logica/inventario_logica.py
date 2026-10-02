from datetime import datetime

from datos.inventario_datos import InventarioDatos
from datos.servicios_datos import ServiciosDatos


class InventarioLogica:

    TIPOS_MOVIMIENTO = ["entrada", "salida"]

    # ---------- CRUD de insumos ----------

    @staticmethod
    def registrar_insumo(nombre, unidad_medida, stock_inicial=0, stock_minimo=0):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del insumo es obligatorio.")

        unidad_medida = (unidad_medida or "").strip()
        if not unidad_medida:
            raise ValueError("La unidad de medida es obligatoria (ej. litros, unidades).")

        try:
            stock_inicial = float(stock_inicial)
            stock_minimo = float(stock_minimo)
        except (TypeError, ValueError):
            raise ValueError("El stock inicial y el stock mínimo deben ser números válidos.")

        if stock_inicial < 0 or stock_minimo < 0:
            raise ValueError("El stock no puede ser negativo.")

        if InventarioDatos.obtener_insumo_por_nombre(nombre) is not None:
            raise ValueError("Ya existe un insumo con ese nombre.")

        insumo_id = InventarioDatos.insertar_insumo(nombre, unidad_medida, stock_minimo)

        if stock_inicial > 0:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            InventarioDatos.registrar_movimiento(
                insumo_id, "entrada", stock_inicial, fecha_hora, motivo="Carga inicial de inventario"
            )

        return insumo_id

    @staticmethod
    def editar_insumo(insumo_id, nombre, unidad_medida, stock_minimo):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del insumo es obligatorio.")

        unidad_medida = (unidad_medida or "").strip()
        if not unidad_medida:
            raise ValueError("La unidad de medida es obligatoria.")

        try:
            stock_minimo = float(stock_minimo)
        except (TypeError, ValueError):
            raise ValueError("El stock mínimo debe ser un número válido.")

        if stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")

        if InventarioDatos.obtener_insumo_por_id(insumo_id) is None:
            raise ValueError("El insumo no existe.")

        existente = InventarioDatos.obtener_insumo_por_nombre(nombre)
        if existente is not None and existente["id"] != insumo_id:
            raise ValueError("Ya existe otro insumo con ese nombre.")

        InventarioDatos.actualizar_insumo(insumo_id, nombre, unidad_medida, stock_minimo)

    @staticmethod
    def listar_insumos():
        return InventarioDatos.listar_insumos(solo_activos=True)

    @staticmethod
    def eliminar_insumo(insumo_id):
        if InventarioDatos.obtener_insumo_por_id(insumo_id) is None:
            raise ValueError("El insumo no existe.")
        InventarioDatos.desactivar_insumo(insumo_id)

    # ---------- Movimientos manuales (ej. llegó un pedido del proveedor) ----------

    @staticmethod
    def registrar_entrada(insumo_id, cantidad, motivo=None):
        insumo = InventarioDatos.obtener_insumo_por_id(insumo_id)
        if insumo is None or insumo["activo"] != 1:
            raise ValueError("El insumo no existe o no está activo.")

        try:
            cantidad = float(cantidad)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un número válido.")

        if cantidad <= 0:
            raise ValueError("La cantidad a ingresar debe ser mayor a cero.")

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return InventarioDatos.registrar_movimiento(insumo_id, "entrada", cantidad, fecha_hora, motivo=motivo)

    @staticmethod
    def listar_movimientos(insumo_id=None):
        return InventarioDatos.listar_movimientos(insumo_id=insumo_id)

    # ---------- Alerta de stock bajo ----------

    @staticmethod
    def listar_alertas_stock_bajo():
        return InventarioDatos.listar_insumos_bajo_stock()

    # ---------- Receta: qué insumos gasta cada servicio ----------

    @staticmethod
    def asignar_insumo_a_servicio(servicio_id, insumo_id, cantidad_consumida):
        if ServiciosDatos.obtener_servicio_por_id(servicio_id) is None:
            raise ValueError("El servicio no existe.")

        insumo = InventarioDatos.obtener_insumo_por_id(insumo_id)
        if insumo is None or insumo["activo"] != 1:
            raise ValueError("El insumo no existe o no está activo.")

        try:
            cantidad_consumida = float(cantidad_consumida)
        except (TypeError, ValueError):
            raise ValueError("La cantidad consumida debe ser un número válido.")

        if cantidad_consumida <= 0:
            raise ValueError("La cantidad consumida debe ser mayor a cero.")

        InventarioDatos.asociar_insumo_a_servicio(servicio_id, insumo_id, cantidad_consumida)

    @staticmethod
    def listar_insumos_de_servicio(servicio_id):
        return InventarioDatos.listar_insumos_de_servicio(servicio_id)

    @staticmethod
    def quitar_insumo_de_servicio(servicio_id, insumo_id):
        InventarioDatos.quitar_insumo_de_servicio(servicio_id, insumo_id)

    # ---------- Descuento automático al asignar servicios ----------

    @staticmethod
    def _calcular_consumo_total(servicio_ids):
        """
        Suma cuánto se necesita de cada insumo entre TODOS los servicios de
        la lista (si dos servicios usan el mismo insumo, se suman).
        Devuelve {insumo_id: cantidad_total}.
        """
        consumo_total = {}
        for servicio_id in servicio_ids:
            receta = InventarioDatos.listar_insumos_de_servicio(servicio_id)
            for ingrediente in receta:
                insumo_id = ingrediente["insumo_id"]
                cantidad = ingrediente["cantidad_consumida"]
                consumo_total[insumo_id] = consumo_total.get(insumo_id, 0) + cantidad
        return consumo_total

    @staticmethod
    def validar_stock_suficiente(servicio_ids):
        """
        Verifica que haya stock suficiente de TODOS los insumos que requieren
        los servicios seleccionados. Se debe llamar ANTES de crear la orden,
        para no crear una orden que luego no se pueda cumplir por falta de insumos.
        Lanza ValueError indicando el insumo y cuánto falta si no alcanza.
        """
        consumo_total = InventarioLogica._calcular_consumo_total(servicio_ids)

        for insumo_id, cantidad_requerida in consumo_total.items():
            insumo = InventarioDatos.obtener_insumo_por_id(insumo_id)
            if insumo is None:
                continue
            if insumo["stock_actual"] < cantidad_requerida:
                raise ValueError(
                    f"Stock insuficiente de '{insumo['nombre']}': se necesitan "
                    f"{cantidad_requerida} {insumo['unidad_medida']} y solo hay "
                    f"{insumo['stock_actual']} {insumo['unidad_medida']} disponibles."
                )

    @staticmethod
    def descontar_insumos_de_servicios(servicio_ids, orden_id, fecha_hora):
        """
        Descuenta del stock los insumos que consumen los servicios seleccionados
        y deja el rastro en movimientos_inventario ligado a la orden.
        Se debe llamar DESPUÉS de crear la orden exitosamente (y después de
        haber pasado validar_stock_suficiente).
        """
        consumo_total = InventarioLogica._calcular_consumo_total(servicio_ids)

        for insumo_id, cantidad_requerida in consumo_total.items():
            InventarioDatos.registrar_movimiento(
                insumo_id,
                "salida",
                cantidad_requerida,
                fecha_hora,
                orden_id=orden_id,
                motivo=f"Consumo automático de la orden #{orden_id}",
            )

    # ---------- Catálogo de ejemplo ----------

    @staticmethod
    def crear_catalogo_por_defecto_si_no_existe():
        """Crea insumos de ejemplo y los conecta con el catálogo de servicios por defecto."""
        if InventarioDatos.contar_insumos() > 0:
            return

        id_shampoo = InventarioLogica.registrar_insumo("Shampoo automotriz", "litros", 20, 5)
        id_cera = InventarioLogica.registrar_insumo("Cera líquida", "litros", 10, 3)
        id_toalla = InventarioLogica.registrar_insumo("Toalla de microfibra", "unidades", 30, 10)
        id_agua = InventarioLogica.registrar_insumo("Agua", "litros", 500, 100)

        servicio_basico = ServiciosDatos.obtener_servicio_por_nombre("Lavado básico")
        servicio_completo = ServiciosDatos.obtener_servicio_por_nombre("Lavado completo")
        servicio_encerado = ServiciosDatos.obtener_servicio_por_nombre("Encerado")
        servicio_aspirado = ServiciosDatos.obtener_servicio_por_nombre("Aspirado de interiores")

        if servicio_basico is not None:
            InventarioLogica.asignar_insumo_a_servicio(servicio_basico["id"], id_shampoo, 1)
            InventarioLogica.asignar_insumo_a_servicio(servicio_basico["id"], id_agua, 40)

        if servicio_completo is not None:
            InventarioLogica.asignar_insumo_a_servicio(servicio_completo["id"], id_shampoo, 2)
            InventarioLogica.asignar_insumo_a_servicio(servicio_completo["id"], id_toalla, 2)
            InventarioLogica.asignar_insumo_a_servicio(servicio_completo["id"], id_agua, 60)

        if servicio_encerado is not None:
            InventarioLogica.asignar_insumo_a_servicio(servicio_encerado["id"], id_cera, 1)
            InventarioLogica.asignar_insumo_a_servicio(servicio_encerado["id"], id_toalla, 1)

        if servicio_aspirado is not None:
            InventarioLogica.asignar_insumo_a_servicio(servicio_aspirado["id"], id_toalla, 1)