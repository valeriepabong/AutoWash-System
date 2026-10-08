from datetime import datetime, timedelta

from datos.Reportes_Datos import Reportes_Datos


class ReportesLogica:


    FORMATO_FECHA = "%Y-%m-%d"
    DIAS_POR_DEFECTO = 30
    MAX_DIAS_RANGO = 366

    # ---------- Utilidades de validacion y formato ----------

    @staticmethod
    def _parsear_fecha(texto, nombre_campo):
        try:
            return datetime.strptime(texto.strip(), ReportesLogica.FORMATO_FECHA).date()
        except (ValueError, AttributeError):
            raise ValueError(
                f"La fecha '{nombre_campo}' no es valida. Use el formato AAAA-MM-DD "
                f"(por ejemplo 2026-10-31)."
            )

    @staticmethod
    def validar_rango(fecha_desde=None, fecha_hasta=None):

        desde_txt = (fecha_desde or "").strip()
        hasta_txt = (fecha_hasta or "").strip()

        hoy = datetime.now().date()

        hasta = ReportesLogica._parsear_fecha(hasta_txt, "hasta") if hasta_txt else hoy
        if desde_txt:
            desde = ReportesLogica._parsear_fecha(desde_txt, "desde")
        else:
            desde = hasta - timedelta(days=ReportesLogica.DIAS_POR_DEFECTO - 1)

        if desde > hasta:
            raise ValueError("La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")

        if (hasta - desde).days + 1 > ReportesLogica.MAX_DIAS_RANGO:
            raise ValueError(
                f"El rango no puede superar {ReportesLogica.MAX_DIAS_RANGO} dias. "
                f"Reduzca el periodo a consultar."
            )

        return (
            desde.strftime(ReportesLogica.FORMATO_FECHA),
            hasta.strftime(ReportesLogica.FORMATO_FECHA),
        )

    @staticmethod
    def formatear_moneda(valor):
        """35000 -> '$35.000' (separador de miles con punto, estilo Colombia)."""
        return "$" + f"{float(valor or 0):,.0f}".replace(",", ".")

    @staticmethod
    def formatear_cantidad(valor):
        """Quita decimales innecesarios: 40.0 -> '40', 2.5 -> '2.5'."""
        valor = float(valor or 0)
        if valor == int(valor):
            return str(int(valor))
        return f"{valor:.2f}".rstrip("0").rstrip(".")

    # ---------- Reportes ----------

    @staticmethod
    def reporte_ingresos(fecha_desde=None, fecha_hasta=None):
        desde, hasta = ReportesLogica.validar_rango(fecha_desde, fecha_hasta)
        datos = Reportes_Datos.ingresos_por_dia(desde, hasta)

        filas = [
            {
                "fecha": d["fecha"],
                "cantidad_facturas": d["cantidad_facturas"],
                "total_ingresos": d["total_ingresos"],
                "total_ingresos_texto": ReportesLogica.formatear_moneda(d["total_ingresos"]),
            }
            for d in datos
        ]

        total = sum(d["total_ingresos"] for d in datos)
        cantidad_facturas = sum(d["cantidad_facturas"] for d in datos)
        promedio = total / cantidad_facturas if cantidad_facturas else 0


        por_fecha = {d["fecha"]: d["total_ingresos"] for d in datos}
        dia = datetime.strptime(desde, ReportesLogica.FORMATO_FECHA).date()
        ultimo = datetime.strptime(hasta, ReportesLogica.FORMATO_FECHA).date()
        etiquetas, valores = [], []
        while dia <= ultimo:
            clave = dia.strftime(ReportesLogica.FORMATO_FECHA)
            etiquetas.append(clave)
            valores.append(por_fecha.get(clave, 0))
            dia += timedelta(days=1)

        return {
            "rango": {"desde": desde, "hasta": hasta},
            "filas": filas,
            "resumen": {
                "total_ingresos": total,
                "total_ingresos_texto": ReportesLogica.formatear_moneda(total),
                "cantidad_facturas": cantidad_facturas,
                "promedio_por_factura": promedio,
                "promedio_por_factura_texto": ReportesLogica.formatear_moneda(promedio),
            },
            "grafica": {"etiquetas": etiquetas, "valores": valores},
        }

    @staticmethod
    def reporte_servicios_mas_solicitados(fecha_desde=None, fecha_hasta=None, limite=None):
        if limite is not None:
            try:
                limite = int(limite)
            except (TypeError, ValueError):
                raise ValueError("El limite debe ser un numero entero.")
            if limite <= 0:
                raise ValueError("El limite debe ser mayor a cero.")

        desde, hasta = ReportesLogica.validar_rango(fecha_desde, fecha_hasta)
        datos = Reportes_Datos.servicios_mas_solicitados(desde, hasta, limite)

        filas = [
            {
                "posicion": i,
                "nombre_servicio": d["nombre_servicio"],
                "cantidad_vendida": d["cantidad_vendida"],
                "ingreso_generado": d["ingreso_generado"],
                "ingreso_generado_texto": ReportesLogica.formatear_moneda(d["ingreso_generado"]),
            }
            for i, d in enumerate(datos, start=1)
        ]

        return {
            "rango": {"desde": desde, "hasta": hasta},
            "filas": filas,
            "resumen": {
                "total_servicios_vendidos": sum(d["cantidad_vendida"] for d in datos),
                "servicio_top": datos[0]["nombre_servicio"] if datos else None,
            },
            "grafica": {
                # Se invierte el orden porque las barras horizontales de
                # matplotlib dibujan el primer elemento abajo; asi el mas
                # vendido queda arriba.
                "etiquetas": [d["nombre_servicio"] for d in reversed(datos)],
                "valores": [d["cantidad_vendida"] for d in reversed(datos)],
            },
        }

    @staticmethod
    def reporte_consumo_insumos(fecha_desde=None, fecha_hasta=None):
        desde, hasta = ReportesLogica.validar_rango(fecha_desde, fecha_hasta)
        datos = Reportes_Datos.consumo_de_insumos(desde, hasta)

        filas = [
            {
                "nombre_insumo": d["nombre_insumo"],
                "unidad_medida": d["unidad_medida"],
                "cantidad_consumida": d["cantidad_consumida"],
                "cantidad_consumida_texto": (
                    f"{ReportesLogica.formatear_cantidad(d['cantidad_consumida'])} "
                    f"{d['unidad_medida']}"
                ),
            }
            for d in datos
        ]

        return {
            "rango": {"desde": desde, "hasta": hasta},
            "filas": filas,
            "resumen": {
                "insumos_con_consumo": len(datos),
                "insumo_top": datos[0]["nombre_insumo"] if datos else None,
            },
            "grafica": None,
        }