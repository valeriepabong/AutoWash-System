import os
from datetime import date, datetime

from datos.dashboard_datos import DashboardDatos
from datos.ordenes_datos import OrdenesDatos
from logica.empleados_logica import EmpleadosLogica
from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura
from logica.servicios_logica import ServiciosLogica

_FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


class DashboardLogica:
    """Reglas de presentacion de datos del Panel de Control (la vista no toca SQL)."""

    # ---------- Formato ----------

    @staticmethod
    def formatear_moneda(valor):
        """645000 -> '$645.000'. Cero se queda como '$0'."""
        return f"${float(valor or 0):,.0f}".replace(",", ".")

    @staticmethod
    def formatear_duracion(minutos):
        """25 -> '25 min', 65 -> '1 h 05 min', 1500 -> '1 d 1 h'. Negativo/None -> '—'."""
        if minutos is None or minutos < 0:
            return "—"
        minutos = int(minutos)
        if minutos < 1:
            return "1 min"
        if minutos < 60:
            return f"{minutos} min"
        horas, resto = divmod(minutos, 60)
        if horas < 24:
            return f"{horas} h {resto:02d} min"
        dias, horas = divmod(horas, 24)
        return f"{dias} d {horas} h"

    @staticmethod
    def _parsear(texto):
        try:
            return datetime.strptime(str(texto), _FORMATO_FECHA)
        except (TypeError, ValueError):
            return None

    # ---------- KPIs ----------

    @staticmethod
    def obtener_kpis():
        """
        Devuelve {'en_proceso': int, 'finalizados_hoy': int,
                  'ingresos_dia': str, 'pendientes': int}.
        Con la BD vacia (o ante un error) todo queda en 0 / '$0'.
        """
        hoy = date.today().isoformat()
        try:
            por_estado = DashboardDatos.contar_ordenes_por_estado()
            return {
                "en_proceso": por_estado.get("proceso", 0),
                "finalizados_hoy": DashboardDatos.contar_finalizados_del_dia(hoy),
                "ingresos_dia": DashboardLogica.formatear_moneda(
                    DashboardDatos.sumar_ingresos_del_dia(hoy)
                ),
                "pendientes": por_estado.get("espera", 0),
            }
        except Exception as err:
            print(f"[Dashboard] Error al calcular KPIs: {err}")
            return {
                "en_proceso": 0,
                "finalizados_hoy": 0,
                "ingresos_dia": "$0",
                "pendientes": 0,
            }

    # ---------- Tabla ----------

    @staticmethod
    def obtener_filas_servicio_activo():
        """
        Filas listas para pintar. Claves: id, placa, cliente, tipo, servicio,
        estado ('En Espera' | 'En Proceso' | 'Completado'), estado_bd, tiempo,
        accion_clave y acciones [(etiqueta, clave, peligro)].
        Lista vacia si no hay ordenes.
        """
        try:
            ordenes = DashboardDatos.listar_ordenes_panel(date.today().isoformat())
        except Exception as err:
            print(f"[Dashboard] Error al cargar ordenes: {err}")
            return []

        ahora = datetime.now()
        filas = []
        for o in ordenes:
            estado_bd = o["estado"]
            inicio = DashboardLogica._parsear(o["fecha_hora"])

            # Tiempo: transcurrido si sigue en curso; duracion hasta la factura si ya se entrego.
            minutos = None
            if inicio is not None:
                if estado_bd == "entregado":
                    fin = DashboardLogica._parsear(o.get("fecha_factura"))
                else:
                    fin = ahora
                if fin is not None:
                    minutos = int((fin - inicio).total_seconds() // 60)

            if estado_bd == "espera":
                badge = "En Espera"
                acciones = [("Editar", "editar", False), ("Iniciar", "iniciar", False)]
            elif estado_bd == "proceso":
                badge = "En Proceso"
                acciones = [("Editar", "editar", False), ("Finalizar", "finalizar", False)]
            elif estado_bd == "terminado":
                badge = "Completado"
                acciones = [("Entregar", "entregar", False)]
            else:  # entregado
                badge = "Completado"
                if o.get("factura_id"):
                    acciones = [("Ver Recibo", "recibo", False)]
                else:
                    acciones = [("Facturar", "facturar", False)]

            filas.append({
                "id": o["id"],
                "placa": o["placa"] or "—",
                "cliente": o["nombre_cliente"] or "—",
                "tipo": o["tipo_vehiculo"] or "—",
                "servicio": o["servicios"] or "—",
                "estado": badge,
                "estado_bd": estado_bd,
                "tiempo": DashboardLogica.formatear_duracion(minutos),
                "empleado_id": o["empleado_id"],
                "acciones": acciones,
            })
        return filas

    # ---------- Acciones ----------

    @staticmethod
    def orden_requiere_empleado(orden_id):
        """True si la orden aun no tiene empleado responsable (hay que pedirlo para avanzar)."""
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")
        return orden["empleado_id"] is None

    @staticmethod
    def listar_empleados_activos():
        """[(id, nombre)] de empleados activos."""
        return [(e["id"], e["nombre"]) for e in EmpleadosLogica.listar_empleados()]

    @staticmethod
    def avanzar_orden(orden_id, empleado_id=None):
        """Pasa la orden al siguiente estado valido del flujo. Devuelve el nuevo estado."""
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden de servicio no existe.")
        nuevo = ServiciosLogica.siguiente_estado(orden["estado"])
        if nuevo is None:
            raise ValueError("Esta orden ya fue entregada.")
        ServiciosLogica.cambiar_estado_orden(orden_id, nuevo, empleado_id)
        return nuevo

    @staticmethod
    def generar_recibo_pdf(orden_id):
        """Genera (o regenera) el PDF de la factura de la orden y devuelve su ruta."""
        factura_orden = FacturacionLogica.obtener_factura_por_orden(orden_id)
        if factura_orden is None:
            raise ValueError("Esta orden todavia no tiene factura.")
        factura = FacturacionLogica.obtener_factura(factura_orden["id"])
        if factura is None:
            raise ValueError("La factura ya no existe.")

        carpeta = os.path.join(os.path.expanduser("~"), "Documents", "AutoWash_Facturas")
        os.makedirs(carpeta, exist_ok=True)
        ruta_pdf = os.path.join(carpeta, f"factura_{factura['id']}.pdf")
        generar_pdf_factura(factura, ruta_pdf)
        return ruta_pdf