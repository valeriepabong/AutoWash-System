"""
Pantalla de Reportes.

CONTRATO REAL de logica/reportes_logica.py (ReportesLogica), confirmado
con el backend:
    reporte_ingresos(fecha_desde=None, fecha_hasta=None) -> dict
        {"rango": {"desde", "hasta"},
         "filas": [{"fecha", "cantidad_facturas", "total_ingresos", "total_ingresos_texto"}],
         "resumen": {"total_ingresos", "total_ingresos_texto", "cantidad_facturas",
                     "promedio_por_factura", "promedio_por_factura_texto"},
         "grafica": {"etiquetas": [...], "valores": [...]}}

    reporte_servicios_mas_solicitados(fecha_desde=None, fecha_hasta=None, limite=None) -> dict
        {"rango": {...},
         "filas": [{"posicion", "nombre_servicio", "cantidad_vendida",
                    "ingreso_generado", "ingreso_generado_texto"}],
         "resumen": {"total_servicios_vendidos", "servicio_top"},
         "grafica": {"etiquetas": [...], "valores": [...]}}  (ya vienen invertidas
         para que la barra horizontal quede con el más vendido arriba)

    reporte_consumo_insumos(fecha_desde=None, fecha_hasta=None) -> dict
        {"rango": {...},
         "filas": [{"nombre_insumo", "unidad_medida", "cantidad_consumida",
                    "cantidad_consumida_texto"}],
         "resumen": {"insumos_con_consumo", "insumo_top"},
         "grafica": None}  (esta sección es solo tabla, sin gráfica)

Las fechas van en formato "AAAA-MM-DD". Si se dejan vacías, ReportesLogica
usa los últimos 30 días por defecto. Las tres funciones lanzan ValueError
si el rango no es válido (fecha mal escrita, "desde" > "hasta", rango
mayor a 366 días).

Si por algún motivo logica/reportes_logica.py no está disponible todavía,
esta pantalla cae en una versión de prueba (_ReportesLogicaMock) con el
mismo contrato, para que la interfaz se pueda seguir probando.
"""

from tkinter import messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from logica.reportes_logica import ReportesLogica
except ImportError:

    class _ReportesLogicaMock:
        """Datos de prueba. Se usa solo si logica/reportes_logica.py no existe."""

        @staticmethod
        def reporte_ingresos(fecha_desde=None, fecha_hasta=None):
            etiquetas = ["2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23", "2026-10-24"]
            valores = [120000, 150000, 0, 200000, 310000]
            filas = [
                {"fecha": f, "cantidad_facturas": 1 if v else 0,
                 "total_ingresos": v, "total_ingresos_texto": f"${v:,.0f}".replace(",", ".")}
                for f, v in zip(etiquetas, valores)
            ]
            total = sum(valores)
            return {
                "rango": {"desde": etiquetas[0], "hasta": etiquetas[-1]},
                "filas": filas,
                "resumen": {
                    "total_ingresos": total,
                    "total_ingresos_texto": f"${total:,.0f}".replace(",", "."),
                    "cantidad_facturas": 4,
                    "promedio_por_factura": total / 4,
                    "promedio_por_factura_texto": f"${total/4:,.0f}".replace(",", "."),
                },
                "grafica": {"etiquetas": etiquetas, "valores": valores},
            }

        @staticmethod
        def reporte_servicios_mas_solicitados(fecha_desde=None, fecha_hasta=None, limite=None):
            nombres = ["Lavado básico", "Encerado", "Lavado completo"]
            cantidades = [40, 18, 12]
            filas = [
                {"posicion": i + 1, "nombre_servicio": n, "cantidad_vendida": c,
                 "ingreso_generado": c * 15000,
                 "ingreso_generado_texto": f"${c*15000:,.0f}".replace(",", ".")}
                for i, (n, c) in enumerate(zip(nombres, cantidades))
            ]
            return {
                "rango": {"desde": "2026-09-27", "hasta": "2026-10-27"},
                "filas": filas,
                "resumen": {"total_servicios_vendidos": sum(cantidades), "servicio_top": nombres[0]},
                "grafica": {"etiquetas": list(reversed(nombres)), "valores": list(reversed(cantidades))},
            }

        @staticmethod
        def reporte_consumo_insumos(fecha_desde=None, fecha_hasta=None):
            filas = [
                {"nombre_insumo": "Shampoo automotriz", "unidad_medida": "litros",
                 "cantidad_consumida": 25.5, "cantidad_consumida_texto": "25.5 litros"},
                {"nombre_insumo": "Cera líquida", "unidad_medida": "litros",
                 "cantidad_consumida": 12, "cantidad_consumida_texto": "12 litros"},
            ]
            return {
                "rango": {"desde": "2026-09-27", "hasta": "2026-10-27"},
                "filas": filas,
                "resumen": {"insumos_con_consumo": len(filas), "insumo_top": filas[0]["nombre_insumo"]},
                "grafica": None,
            }

    ReportesLogica = _ReportesLogicaMock


COLOR_FONDO = "#2b2b2b"
COLOR_BARRA_INGRESOS = "#1f538d"
COLOR_BARRA_SERVICIOS = "#2fa572"


def _estilizar_eje(ax):
    ax.set_facecolor(COLOR_FONDO)
    ax.tick_params(colors="white", labelsize=8)
    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.title.set_color("white")


class ReportesScreen(ctk.CTkFrame):

    def __init__(self, master, al_volver=None):
        super().__init__(master)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self._crear_encabezado()
        self._crear_pestanas()

        # Primera carga con el rango por defecto (últimos 30 días)
        self._filtrar_ingresos()
        self._filtrar_servicios()
        self._filtrar_insumos()

    # ---------- Encabezado ----------

    def _crear_encabezado(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header, text="Módulo de Reportes", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        if self.al_volver:
            ctk.CTkButton(
                header, text="Volver al Dashboard", command=self.al_volver, width=150
            ).pack(side="right")

    def _crear_pestanas(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True)

        self.tab_ingresos = self.tabs.add("Ingresos por Período")
        self.tab_servicios = self.tabs.add("Servicios más Solicitados")
        self.tab_insumos = self.tabs.add("Consumo de Insumos")

        self._construir_tab_ingresos()
        self._construir_tab_servicios()
        self._construir_tab_insumos()

    # ---------- TAB 1: Ingresos por periodo ----------

    def _construir_tab_ingresos(self):
        frame_top = ctk.CTkFrame(self.tab_ingresos, fg_color="transparent")
        frame_top.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_top, text="Desde:").pack(side="left", padx=5)
        self.entry_ingresos_desde = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_ingresos_desde.pack(side="left", padx=5)

        ctk.CTkLabel(frame_top, text="Hasta:").pack(side="left", padx=5)
        self.entry_ingresos_hasta = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_ingresos_hasta.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_top, text="Filtrar", width=90, command=self._filtrar_ingresos
        ).pack(side="left", padx=10)

        self.label_total_ingresos = ctk.CTkLabel(
            frame_top, text="Total acumulado: $0", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_total_ingresos.pack(side="right", padx=10)

        self.frame_grafica_ingresos = ctk.CTkFrame(self.tab_ingresos, fg_color="transparent")
        self.frame_grafica_ingresos.pack(fill="both", expand=True, pady=10)

    def _filtrar_ingresos(self):
        desde = self.entry_ingresos_desde.get().strip() or None
        hasta = self.entry_ingresos_hasta.get().strip() or None

        try:
            reporte = ReportesLogica.reporte_ingresos(desde, hasta)
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        self.label_total_ingresos.configure(
            text=f"Total acumulado: {reporte['resumen']['total_ingresos_texto']}"
        )

        for widget in self.frame_grafica_ingresos.winfo_children():
            widget.destroy()

        etiquetas = reporte["grafica"]["etiquetas"]
        valores = reporte["grafica"]["valores"]

        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=100)
        fig.patch.set_facecolor(COLOR_FONDO)
        _estilizar_eje(ax)
        ax.bar(etiquetas, valores, color=COLOR_BARRA_INGRESOS)
        ax.set_title("Ingresos por día", fontsize=11)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_ingresos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ---------- TAB 2: Servicios más solicitados ----------

    def _construir_tab_servicios(self):
        frame_top = ctk.CTkFrame(self.tab_servicios, fg_color="transparent")
        frame_top.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_top, text="Desde:").pack(side="left", padx=5)
        self.entry_servicios_desde = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_servicios_desde.pack(side="left", padx=5)

        ctk.CTkLabel(frame_top, text="Hasta:").pack(side="left", padx=5)
        self.entry_servicios_hasta = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_servicios_hasta.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_top, text="Filtrar", width=90, command=self._filtrar_servicios
        ).pack(side="left", padx=10)

        self.label_servicio_top = ctk.CTkLabel(
            frame_top, text="Más vendido: -", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_servicio_top.pack(side="right", padx=10)

        self.frame_grafica_servicios = ctk.CTkFrame(self.tab_servicios, fg_color="transparent")
        self.frame_grafica_servicios.pack(fill="both", expand=True, pady=10)

    def _filtrar_servicios(self):
        desde = self.entry_servicios_desde.get().strip() or None
        hasta = self.entry_servicios_hasta.get().strip() or None

        try:
            reporte = ReportesLogica.reporte_servicios_mas_solicitados(desde, hasta)
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        top = reporte["resumen"]["servicio_top"] or "Sin datos en este periodo"
        self.label_servicio_top.configure(text=f"Más vendido: {top}")

        for widget in self.frame_grafica_servicios.winfo_children():
            widget.destroy()

        etiquetas = reporte["grafica"]["etiquetas"]
        valores = reporte["grafica"]["valores"]

        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=100)
        fig.patch.set_facecolor(COLOR_FONDO)
        _estilizar_eje(ax)
        if etiquetas:
            ax.barh(etiquetas, valores, color=COLOR_BARRA_SERVICIOS)
        ax.set_title("Cantidad de servicios vendidos", fontsize=11)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_servicios)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ---------- TAB 3: Consumo de insumos (solo tabla) ----------

    def _construir_tab_insumos(self):
        frame_top = ctk.CTkFrame(self.tab_insumos, fg_color="transparent")
        frame_top.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_top, text="Desde:").pack(side="left", padx=5)
        self.entry_insumos_desde = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_insumos_desde.pack(side="left", padx=5)

        ctk.CTkLabel(frame_top, text="Hasta:").pack(side="left", padx=5)
        self.entry_insumos_hasta = ctk.CTkEntry(frame_top, placeholder_text="AAAA-MM-DD", width=110)
        self.entry_insumos_hasta.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_top, text="Filtrar", width=90, command=self._filtrar_insumos
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            self.tab_insumos,
            text="Resumen de insumos consumidos en el período",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        self.frame_tabla_insumos = ctk.CTkScrollableFrame(self.tab_insumos)
        self.frame_tabla_insumos.pack(fill="both", expand=True, pady=5)

    def _filtrar_insumos(self):
        desde = self.entry_insumos_desde.get().strip() or None
        hasta = self.entry_insumos_hasta.get().strip() or None

        try:
            reporte = ReportesLogica.reporte_consumo_insumos(desde, hasta)
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        for widget in self.frame_tabla_insumos.winfo_children():
            widget.destroy()

        encabezados = ["Insumo", "Cantidad consumida", "Unidad de medida"]
        for col, texto in enumerate(encabezados):
            ctk.CTkLabel(
                self.frame_tabla_insumos, text=texto, font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=20, pady=5, sticky="w")

        filas = reporte["filas"]
        if not filas:
            ctk.CTkLabel(
                self.frame_tabla_insumos, text="Sin consumo de insumos en este periodo."
            ).grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="w")
            return

        for fila_idx, insumo in enumerate(filas, start=1):
            ctk.CTkLabel(self.frame_tabla_insumos, text=insumo["nombre_insumo"]).grid(
                row=fila_idx, column=0, padx=20, pady=5, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla_insumos, text=insumo["cantidad_consumida_texto"]).grid(
                row=fila_idx, column=1, padx=20, pady=5, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla_insumos, text=insumo["unidad_medida"]).grid(
                row=fila_idx, column=2, padx=20, pady=5, sticky="w"
            )