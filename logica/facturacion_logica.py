from datetime import datetime

from datos.facturacion_datos import FacturacionDatos
from datos.ordenes_datos import OrdenesDatos


class FacturacionLogica:

    METODOS_PAGO = ["efectivo", "tarjeta", "transferencia"]

    @staticmethod
    def generar_factura(orden_id, metodo_pago):
        """
        Genera el comprobante de pago de una orden que YA fue entregada.
        - La orden debe existir y estar en estado 'entregado'.
        - El método de pago debe ser uno de los permitidos.
        - Una orden solo puede facturarse una vez.
        El total se toma directamente de la orden (no se vuelve a calcular
        aquí, para no desincronizarse si el total de la orden cambiara).
        Devuelve el id de la factura creada.
        """
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")

        if orden["estado"] != "entregado":
            raise ValueError(
                f"Solo se puede facturar una orden que ya fue entregada. "
                f"Esta orden está en estado '{orden['estado']}'."
            )

        metodo_pago = (metodo_pago or "").strip().lower()
        if metodo_pago not in FacturacionLogica.METODOS_PAGO:
            raise ValueError(
                f"Método de pago inválido. Los métodos válidos son: "
                f"{', '.join(FacturacionLogica.METODOS_PAGO)}."
            )

        if FacturacionDatos.obtener_factura_por_orden(orden_id) is not None:
            raise ValueError("Esta orden ya tiene una factura generada.")

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return FacturacionDatos.insertar_factura(orden_id, metodo_pago, orden["total"], fecha_hora)

    @staticmethod
    def obtener_factura(factura_id):
        """Devuelve la factura con sus datos de cliente/vehículo, más el detalle de servicios."""
        factura = FacturacionDatos.obtener_factura_por_id(factura_id)
        if factura is None:
            return None
        factura["detalle"] = OrdenesDatos.obtener_detalle_de_orden(factura["orden_id"])
        return factura

    @staticmethod
    def obtener_factura_por_orden(orden_id):
        return FacturacionDatos.obtener_factura_por_orden(orden_id)

    @staticmethod
    def listar_facturas():
        return FacturacionDatos.listar_facturas()