import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportesScreen(ctk.CTkFrame):
    def __init__(self, master, al_volver=None):
        super().__init__(master)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True)

        self._crear_encabezado()
        self._crear_pestanas()

    def _crear_encabezado(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        lbl_titulo = ctk.CTkLabel(header, text="Módulo de Reportes", font=ctk.CTkFont(size=22, weight="bold"))
        lbl_titulo.pack(side="left")

        if self.al_volver:
            btn_volver = ctk.CTkButton(header, text="Volver al Dashboard", command=self.al_volver, width=150)
            btn_volver.pack(side="right")

    def _crear_pestanas(self):
        # Tabview con las 3 secciones requeridas
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_ingresos = self.tabs.add("Ingresos por Período")
        self.tab_servicios = self.tabs.add("Servicios más Solicitados")
        self.tab_insumos = self.tabs.add("Consumo de Insumos")

        self._construir_tab_ingresos()
        self._construir_tab_servicios()
        self._construir_tab_insumos()

    # --- TAB 1: INGRESOS POR PERÍODO ---
    def _construir_tab_ingresos(self):
        frame_top = ctk.CTkFrame(self.tab_ingresos, fg_color="transparent")
        frame_top.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_top, text="Desde:").pack(side="left", padx=5)
        ent_desde = ctk.CTkEntry(frame_top, placeholder_text="YYYY-MM-DD", width=110)
        ent_desde.pack(side="left", padx=5)

        ctk.CTkLabel(frame_top, text="Hasta:").pack(side="left", padx=5)
        ent_hasta = ctk.CTkEntry(frame_top, placeholder_text="YYYY-MM-DD", width=110)
        ent_hasta.pack(side="left", padx=5)

        btn_filtrar = ctk.CTkButton(frame_top, text="Filtrar", width=90)
        btn_filtrar.pack(side="left", padx=10)

        lbl_total = ctk.CTkLabel(frame_top, text="Total Acumulado: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_total.pack(side="right", padx=10)

        # Gráfico de barras embebido (Ingresos por día)
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Fondo oscuro acorde a CustomTkinter
        ax.set_facecolor('#2b2b2b')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Ejemplo de datos (el Backend los reemplazará)
        dias = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        ingresos = [120, 150, 180, 200, 310, 450, 380]
        ax.bar(dias, ingresos, color='#1f538d')
        ax.set_title("Ingresos por Día ($)", color='white')

        canvas = FigureCanvasTkAgg(fig, master=self.tab_ingresos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # --- TAB 2: SERVICIOS MÁS SOLICITADOS ---
    def _construir_tab_servicios(self):
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Barras horizontales
        servicios = ['Lavado General', 'Polichado', 'Lavado Motor', 'Limpieza Cojinería']
        cantidades = [85, 42, 30, 18]
        ax.barh(servicios, cantidades, color='#2fa572')
        ax.set_title("Cantidad de Servicios Vendidos", color='white')
        ax.invert_yaxis()  # Ordenar de mayor a menor

        canvas = FigureCanvasTkAgg(fig, master=self.tab_servicios)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # --- TAB 3: CONSUMO DE INSUMOS (SOLO TABLA) ---
    def _construir_tab_insumos(self):
        lbl_info = ctk.CTkLabel(self.tab_insumos, text="Resumen de Insumos Consumidos en el Período", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_info.pack(anchor="w", pady=10)

        # Tabla simple en Tkinter (ScrollableFrame)
        scroll_frame = ctk.CTkScrollableFrame(self.tab_insumos)
        scroll_frame.pack(fill="both", expand=True, pady=5)

        # Cabecera
        headers = ["Insumo", "Cantidad Consumida", "Unidad de Medida"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(scroll_frame, text=text, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=20, pady=5, sticky="w")

        # Datos de ejemplo ( Backend lo llenará )
        insumos_ejemplo = [
            ("Champú de autos", "25.5", "Litros"),
            ("Cera líquida", "12.0", "Litros"),
            ("Desengrasante", "8.0", "Galones"),
            ("Paños de microfibra", "15", "Unidades")
        ]

        for row, data in enumerate(insumos_ejemplo, start=1):
            for col, text in enumerate(data):
                lbl = ctk.CTkLabel(scroll_frame, text=text)
                lbl.grid(row=row, column=col, padx=20, pady=5, sticky="w")