"""
Pantalla de Reportes y estadísticas.

CONTRATO REAL de logica/reportes_logica.py (ReportesLogica):
    reporte_ingresos(fecha_desde=None, fecha_hasta=None) -> dict
    reporte_servicios_mas_solicitados(fecha_desde=None, fecha_hasta=None, limite=None) -> dict
    reporte_consumo_insumos(fecha_desde=None, fecha_hasta=None) -> dict
"""

from tkinter import messagebox, ttk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla

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


COLOR_FONDO = "#FFFFFF"
COLOR_BARRA = "#589EB5"
COLOR_GRILLA = "#D9EEF5"


class ReportesScreen(ctk.CTkFrame):
    """
    Pantalla de Reportes y estadísticas fiel al diseño Figma:
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Reportes'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Selector de 3 botones tipo píldora:
      [Ingresos por período], [Servicios más solicitados], [Consumo de insumos].
    - Filtros blancos redondeados, gráficas Matplotlib limpias sobre fondo #FFFFFF
      y tablas Autowash.Treeview con cabecera #BCE3F0.
    """

    def __init__(self, master, al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_servicios=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(master, fg_color="#E7F9FF", corner_radius=0)
        self.al_volver = al_volver or al_ir_dashboard
        self.al_ir_dashboard = al_ir_dashboard or al_volver
        self.al_ir_clientes = al_ir_clientes
        self.al_ir_vehiculos = al_ir_vehiculos
        self.al_ir_servicios = al_ir_servicios
        self.al_ir_empleados = al_ir_empleados
        self.al_ir_inventario = al_ir_inventario
        self.al_ir_facturacion = al_ir_facturacion
        self.al_ir_reportes = al_ir_reportes
        self.al_ir_catalogo = al_ir_catalogo
        self.al_ir_facturas = al_ir_facturas
        self.al_cerrar_sesion = al_cerrar_sesion

        self._vista_actual = "ingresos"
        self._tab_buttons = {}
        self._vistas = {}

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()

        # Primera carga con el rango por defecto (últimos 30 días)
        self._filtrar_ingresos()
        self._filtrar_servicios()
        self._filtrar_insumos()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Reportes",
            al_volver=self.al_volver,
            al_ir_dashboard=self.al_ir_dashboard,
            al_ir_clientes=self.al_ir_clientes,
            al_ir_vehiculos=self.al_ir_vehiculos,
            al_ir_servicios=self.al_ir_servicios,
            al_ir_empleados=self.al_ir_empleados,
            al_ir_inventario=self.al_ir_inventario,
            al_ir_facturacion=self.al_ir_facturacion,
            al_ir_reportes=self.al_ir_reportes,
            al_ir_catalogo=self.al_ir_catalogo,
            al_ir_facturas=self.al_ir_facturas,
            al_cerrar_sesion=self.al_cerrar_sesion,
        )

        # ------------------------------------------------------------------ #
        # 2. CONTENEDOR PRINCIPAL DERECHO                                    #
        # ------------------------------------------------------------------ #
        self.main_container = ctk.CTkFrame(self, fg_color="#E7F9FF", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.scroll_body = ctk.CTkScrollableFrame(self.main_container, fg_color="#E7F9FF")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=20)

        # ————— ENCABEZADO Y NAVEGACIÓN —————
        header_nav = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_nav.pack(fill="x", pady=(0, 6))

        btn_volver_dash = ctk.CTkButton(
            header_nav,
            text="← volver al panel principal",
            command=self.al_volver,
            fg_color="transparent",
            hover_color="#D5EFF7",
            text_color="#0B4F66",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            height=28
        )
        btn_volver_dash.pack(side="left")

        ctk.CTkLabel(
            self.scroll_body,
            text="Reportes y estadísticas",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Ingresos, servicios más solicitados y consumo de insumos",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 14))

        # ————— SELECTOR DE 3 BOTONES TIPO PÍLDORA —————
        pills_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        pills_frame.pack(fill="x", pady=(0, 16))

        definicion_tabs = [
            ("ingresos",  "Ingresos por período"),
            ("servicios", "Servicios más solicitados"),
            ("insumos",   "Consumo de insumos"),
        ]

        for clave, titulo in definicion_tabs:
            btn = ctk.CTkButton(
                pills_frame,
                text=titulo,
                command=lambda c=clave: self._seleccionar_vista(c),
                height=36,
                corner_radius=16,
                border_width=1,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(side="left", padx=(0, 10))
            self._tab_buttons[clave] = btn

        # ————— CONTENEDOR DE VISTAS —————
        self.contenedor_vistas = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        self.contenedor_vistas.pack(fill="both", expand=True)

        self.vista_ingresos = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        self.vista_servicios = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        self.vista_insumos = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")

        self._vistas = {
            "ingresos":  self.vista_ingresos,
            "servicios": self.vista_servicios,
            "insumos":   self.vista_insumos,
        }

        self._construir_vista_ingresos()
        self._construir_vista_servicios()
        self._construir_vista_insumos()

        self._seleccionar_vista("ingresos")

    def _seleccionar_vista(self, clave):
        self._vista_actual = clave
        for k, btn in self._tab_buttons.items():
            if k == clave:
                btn.configure(
                    fg_color="#7BB6C9",
                    hover_color="#69A7BC",
                    text_color="#FFFFFF",
                    border_color="#589EB5",
                )
            else:
                btn.configure(
                    fg_color="#FFFFFF",
                    hover_color="#EBF7FB",
                    text_color="#111111",
                    border_color="#7BB6C9",
                )

        for k, frame in self._vistas.items():
            if k == clave:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def _crear_barra_filtro(self, parent, cmd_filtrar):
        """Crea la barra blanca redondeada de filtro de fechas reutilizable."""
        barra = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#CCE5F0"
        )
        barra.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(barra, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner, text="Desde:", font=("Segoe UI", 12, "bold"), text_color="#111111").pack(side="left", padx=(0, 6))
        entry_desde = ctk.CTkEntry(
            inner,
            placeholder_text="AAAA-MM-DD",
            placeholder_text_color="#666666",
            width=125,
            height=36,
            corner_radius=12,
            border_color="#000000",
            border_width=1,
            fg_color="#FFFFFF",
            text_color="#111111",
            font=("Segoe UI", 11)
        )
        entry_desde.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(inner, text="Hasta:", font=("Segoe UI", 12, "bold"), text_color="#111111").pack(side="left", padx=(0, 6))
        entry_hasta = ctk.CTkEntry(
            inner,
            placeholder_text="AAAA-MM-DD",
            placeholder_text_color="#666666",
            width=125,
            height=36,
            corner_radius=12,
            border_color="#000000",
            border_width=1,
            fg_color="#FFFFFF",
            text_color="#111111",
            font=("Segoe UI", 11)
        )
        entry_hasta.pack(side="left", padx=(0, 14))

        ctk.CTkButton(
            inner,
            text="Filtrar",
            width=95,
            height=36,
            corner_radius=12,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            command=cmd_filtrar
        ).pack(side="left")

        return inner, entry_desde, entry_hasta

    # ---------- VISTA 1: Ingresos por período ----------

    def _construir_vista_ingresos(self):
        inner_barra, self.entry_ingresos_desde, self.entry_ingresos_hasta = self._crear_barra_filtro(
            self.vista_ingresos, self._filtrar_ingresos
        )

        self.label_total_ingresos = ctk.CTkLabel(
            inner_barra,
            text="Total acumulado: $0",
            font=("Georgia", 14, "bold"),
            text_color="#3C3B3B"
        )
        self.label_total_ingresos.pack(side="right", padx=(10, 4))

        # Tarjeta blanca de la gráfica
        card_grafica = ctk.CTkFrame(
            self.vista_ingresos,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_grafica.pack(fill="x", pady=(0, 16))

        inner_graf = ctk.CTkFrame(card_grafica, fg_color="transparent")
        inner_graf.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            inner_graf,
            text="Ingresos por día",
            font=("Georgia", 18),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self.frame_grafica_ingresos = ctk.CTkFrame(inner_graf, fg_color="#FFFFFF")
        self.frame_grafica_ingresos.pack(fill="both", expand=True)

        # Tabla de detalle por día debajo de la gráfica (mantiene compatibilidad con test_reportes_screen_muestra_tabla_filas)
        card_tabla = ctk.CTkFrame(
            self.vista_ingresos,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla.pack(fill="both", expand=True)

        inner_tab = ctk.CTkFrame(card_tabla, fg_color="transparent")
        inner_tab.pack(fill="both", expand=True, padx=18, pady=14)

        ctk.CTkLabel(
            inner_tab,
            text="Detalle de ventas por día",
            font=("Georgia", 15),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        columnas_ingresos = ("fecha", "cantidad_facturas", "total_ingresos")
        self.tabla_ingresos = ttk.Treeview(
            inner_tab,
            columns=columnas_ingresos,
            show="headings",
            height=6,
            style="Autowash.Treeview"
        )
        self.tabla_ingresos.heading("fecha", text="Fecha")
        self.tabla_ingresos.heading("cantidad_facturas", text="Facturas Emitidas")
        self.tabla_ingresos.heading("total_ingresos", text="Total Vendido")

        self.tabla_ingresos.column("fecha", width=130, anchor="center")
        self.tabla_ingresos.column("cantidad_facturas", width=130, anchor="center")
        self.tabla_ingresos.column("total_ingresos", width=150, anchor="center")

        self.tabla_ingresos.pack(fill="both", expand=True)

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

        fig, ax = plt.subplots(figsize=(6.8, 3.4), dpi=100)
        fig.patch.set_facecolor(COLOR_FONDO)
        ax.set_facecolor(COLOR_FONDO)

        # Grilla horizontal suave y estética limpia
        ax.yaxis.grid(True, color=COLOR_GRILLA, linestyle="-", linewidth=0.9)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#D9EEF5")
        ax.spines["bottom"].set_color("#D9EEF5")
        ax.tick_params(colors="#555555", labelsize=8)

        if etiquetas:
            bars = ax.bar(etiquetas, valores, color=COLOR_BARRA, width=0.55)
            max_val = max(valores) if valores else 0
            if max_val > 0:
                ax.set_ylim(0, max_val * 1.2)
            for bar, val in zip(bars, valores):
                if val > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        bar.get_height() + (max_val * 0.02 if max_val > 0 else 1),
                        f"${val:,.0f}".replace(",", "."),
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        color="#555555",
                        fontweight="bold",
                    )
            ax.tick_params(axis="x", rotation=35)
        else:
            ax.text(0.5, 0.5, "Sin datos en este período", ha="center", va="center", color="#666666", transform=ax.transAxes)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_ingresos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

        # Poblar la tabla de detalle por día
        for item in self.tabla_ingresos.get_children():
            self.tabla_ingresos.delete(item)

        for f in reporte.get("filas", []):
            self.tabla_ingresos.insert(
                "",
                "end",
                values=(
                    f.get("fecha", ""),
                    f.get("cantidad_facturas", 0),
                    f.get("total_ingresos_texto", "$0"),
                ),
            )

    # ---------- VISTA 2: Servicios más solicitados ----------

    def _construir_vista_servicios(self):
        inner_barra, self.entry_servicios_desde, self.entry_servicios_hasta = self._crear_barra_filtro(
            self.vista_servicios, self._filtrar_servicios
        )

        self.label_servicio_top = ctk.CTkLabel(
            inner_barra,
            text="Más vendido: -",
            font=("Georgia", 14, "bold"),
            text_color="#3C3B3B"
        )
        self.label_servicio_top.pack(side="right", padx=(10, 4))

        card_grafica = ctk.CTkFrame(
            self.vista_servicios,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_grafica.pack(fill="both", expand=True)

        inner_graf = ctk.CTkFrame(card_grafica, fg_color="transparent")
        inner_graf.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            inner_graf,
            text="Cantidad de servicios vendidos",
            font=("Georgia", 18),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self.frame_grafica_servicios = ctk.CTkFrame(inner_graf, fg_color="#FFFFFF")
        self.frame_grafica_servicios.pack(fill="both", expand=True)

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

        fig, ax = plt.subplots(figsize=(6.8, 3.6), dpi=100)
        fig.patch.set_facecolor(COLOR_FONDO)
        ax.set_facecolor(COLOR_FONDO)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_color("#D9EEF5")
        ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        ax.tick_params(axis="y", colors="#333333", labelsize=9)

        if etiquetas:
            bars = ax.barh(etiquetas, valores, color=COLOR_BARRA, height=0.55)
            max_val = max(valores) if valores else 0
            if max_val > 0:
                ax.set_xlim(0, max_val * 1.18)
            for bar, val in zip(bars, valores):
                txt_val = f"{int(val)}" if float(val).is_integer() else f"{val:g}"
                ax.text(
                    bar.get_width() + (max_val * 0.02 if max_val > 0 else 0.5),
                    bar.get_y() + bar.get_height() / 2.0,
                    txt_val,
                    va="center",
                    ha="left",
                    fontsize=9,
                    color="#333333",
                    fontweight="bold",
                )
        else:
            ax.text(0.5, 0.5, "Sin datos en este período", ha="center", va="center", color="#666666", transform=ax.transAxes)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_servicios)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ---------- VISTA 3: Consumo de insumos ----------

    def _construir_vista_insumos(self):
        _, self.entry_insumos_desde, self.entry_insumos_hasta = self._crear_barra_filtro(
            self.vista_insumos, self._filtrar_insumos
        )

        ctk.CTkLabel(
            self.vista_insumos,
            text="Resumen de insumos consumidos en el período",
            font=("Georgia", 16),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        card_insumos = ctk.CTkFrame(
            self.vista_insumos,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_color="#CCE5F0",
            border_width=1
        )
        card_insumos.pack(fill="both", expand=True)

        self.frame_tabla_insumos = ctk.CTkFrame(card_insumos, fg_color="#FFFFFF")
        self.frame_tabla_insumos.pack(fill="both", expand=True, padx=16, pady=16)

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

        columnas = ("insumo", "cantidad", "unidad")
        tabla_insumos = ttk.Treeview(
            self.frame_tabla_insumos,
            columns=columnas,
            show="headings",
            height=9,
            style="Autowash.Treeview"
        )
        tabla_insumos.heading("insumo", text="Insumo")
        tabla_insumos.heading("cantidad", text="Cantidad consumida")
        tabla_insumos.heading("unidad", text="Unidad")

        tabla_insumos.column("insumo", width=260, anchor="center")
        tabla_insumos.column("cantidad", width=180, anchor="center")
        tabla_insumos.column("unidad", width=140, anchor="center")
        tabla_insumos.pack(fill="both", expand=True)

        filas = reporte["filas"]
        if not filas:
            tabla_insumos.insert(
                "", "end", values=("Sin consumo de insumos en este período.", "—", "—")
            )
            return

        for insumo in filas:
            tabla_insumos.insert(
                "",
                "end",
                values=(
                    insumo["nombre_insumo"],
                    insumo["cantidad_consumida_texto"],
                    insumo["unidad_medida"],
                ),
            )
