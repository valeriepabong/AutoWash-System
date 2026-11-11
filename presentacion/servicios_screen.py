from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.servicios_logica import ServiciosLogica
from logica.vehiculos_logica import VehiculosLogica
from logica.empleados_logica import EmpleadosLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class ServiciosScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión y Asignación de Servicios fiel al diseño Figma (Imagen 1):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Servicios'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Barra de 'Flujo de la orden' con badges de estado [Espera -> Proceso -> Terminado -> Entregado].
    - Tarjeta blanca 'Asignar servicios' con combos borde negro, grilla horizontal de servicios, total y botón #F68B2E.
    - Contenedor blanco inferior 'Órdenes en curso' con tabla Autowash.Treeview de cabecera #BCE3F0.
    """

    def __init__(self, parent, al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_servicios=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(parent, fg_color="#E7F9FF", corner_radius=0)
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

        self.vehiculos_disponibles = []
        self.empleados_disponibles = []
        self.ordenes = {}  # id de orden -> datos de la orden
        self.checks = []  # lista de tuplas (servicio, variable del checkbox)

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_vehiculos()
        self._cargar_servicios()
        self._cargar_empleados()
        self._cargar_ordenes()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Servicios",
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

        if self.al_ir_catalogo:
            ctk.CTkButton(
                header_nav,
                text="📖 Catálogo y Recetas",
                command=self.al_ir_catalogo,
                fg_color="#0B4F66",
                hover_color="#336E84",
                text_color="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
                height=32,
                corner_radius=12
            ).pack(side="right")

        if self.al_ir_vehiculos:
            ctk.CTkButton(
                header_nav,
                text="← 2. Vehículos",
                command=self.al_ir_vehiculos,
                fg_color="#555555",
                hover_color="#333333",
                text_color="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
                height=32,
                corner_radius=12
            ).pack(side="right", padx=(0, 10))

        # Título y subtítulo
        ctk.CTkLabel(
            self.scroll_body,
            text="Gestión de servicios",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Asignacion de servicios y ordenes en curso",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        # ————— BARRA DE FLUJO DE LA ORDEN —————
        flujo_bar = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        flujo_bar.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            flujo_bar,
            text="Flujo de la orden :",
            font=("Segoe UI", 12, "bold"),
            text_color="#333333"
        ).pack(side="left", padx=(0, 10))

        badges = [
            ("Espera", "#FFECAF"),
            ("Proceso", "#85CDE5"),
            ("Terminado", "#A2EDA2"),
            ("Entregado", "#C4C4C4"),
        ]
        for idx, (texto_badge, color_bg) in enumerate(badges):
            if idx > 0:
                ctk.CTkLabel(
                    flujo_bar,
                    text="→",
                    font=("Segoe UI", 13, "bold"),
                    text_color="#333333"
                ).pack(side="left", padx=6)

            pill = ctk.CTkFrame(
                flujo_bar,
                fg_color=color_bg,
                corner_radius=12,
                height=26
            )
            pill.pack(side="left")
            ctk.CTkLabel(
                pill,
                text=texto_badge,
                font=("Segoe UI", 11, "bold"),
                text_color="#111111"
            ).pack(padx=14, pady=3)

        # ————— TARJETA BLANCA: ASIGNAR SERVICIOS —————
        card_form = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_form.pack(fill="x", pady=(0, 18))

        inner_form = ctk.CTkFrame(card_form, fg_color="transparent")
        inner_form.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            inner_form,
            text="Asignar servicios",
            font=("Georgia", 22),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 14))

        # Fila de 2 columnas: Vehiculo | Empleado responsable
        fila_selectores = ctk.CTkFrame(inner_form, fg_color="transparent")
        fila_selectores.pack(fill="x", pady=(0, 14))
        fila_selectores.grid_columnconfigure(0, weight=1)
        fila_selectores.grid_columnconfigure(1, weight=1)

        # Columna 0: Vehiculo
        col_veh = ctk.CTkFrame(fila_selectores, fg_color="transparent")
        col_veh.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(
            col_veh,
            text="Vehiculo",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.combo_vehiculo = ctk.CTkComboBox(
            col_veh,
            values=["Sin vehículos registrados"],
            state="readonly",
            height=40,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            button_color="#FFFFFF",
            button_hover_color="#E7F9FF",
            text_color="#111111",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#111111",
            dropdown_hover_color="#D9F0F9",
            font=("Segoe UI", 12)
        )
        self.combo_vehiculo.pack(fill="x")

        # Columna 1: Empleado responsable
        col_emp = ctk.CTkFrame(fila_selectores, fg_color="transparent")
        col_emp.grid(row=0, column=1, sticky="ew", padx=(12, 0))

        ctk.CTkLabel(
            col_emp,
            text="Empleado responsable",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.combo_empleado = ctk.CTkComboBox(
            col_emp,
            values=["Sin empleados registrados"],
            state="readonly",
            height=40,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            button_color="#FFFFFF",
            button_hover_color="#E7F9FF",
            text_color="#111111",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#111111",
            dropdown_hover_color="#D9F0F9",
            font=("Segoe UI", 12)
        )
        self.combo_empleado.pack(fill="x")

        # Servicios (Marque uno o mas)
        ctk.CTkLabel(
            inner_form,
            text="Servicios ( Marque uno o mas)",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(2, 6))

        self.frame_servicios = ctk.CTkScrollableFrame(
            inner_form,
            height=90,
            fg_color="#F8FAFC",
            corner_radius=14,
            border_color="#CCE5F0",
            border_width=1
        )
        self.frame_servicios.pack(fill="x", pady=(0, 16))
        for col_idx in range(3):
            self.frame_servicios.grid_columnconfigure(col_idx, weight=1)

        # Fila inferior de la tarjeta: Total | Botón Asignar servicios
        fila_total = ctk.CTkFrame(inner_form, fg_color="transparent")
        fila_total.pack(fill="x")

        self.label_total = ctk.CTkLabel(
            fila_total,
            text="Total : $ 0",
            font=("Segoe UI", 16, "bold"),
            text_color="#111111"
        )
        self.label_total.pack(side="left")

        btn_asignar = ctk.CTkButton(
            fila_total,
            text="Asignar servicios",
            command=self._evento_asignar,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            height=40,
            corner_radius=14,
            width=190
        )
        btn_asignar.pack(side="right")

        # ————— SECCIÓN INFERIOR: ÓRDENES EN CURSO —————
        head_ordenes = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        head_ordenes.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            head_ordenes,
            text="Órdenes en curso",
            font=("Georgia", 18),
            text_color="#111111",
            anchor="w"
        ).pack(side="left")

        ctk.CTkButton(
            head_ordenes,
            text="Avanzar estado →",
            command=self._evento_avanzar,
            fg_color="#3F8FA9",
            hover_color="#336E84",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            height=32,
            corner_radius=12
        ).pack(side="right")

        card_tabla = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla.pack(fill="both", expand=True)

        inner_tabla = ctk.CTkFrame(card_tabla, fg_color="transparent")
        inner_tabla.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("id", "placa", "empleado", "estado", "total")
        self.tabla = ttk.Treeview(
            inner_tabla,
            columns=columnas,
            show="headings",
            height=6,
            style="Autowash.Treeview"
        )

        self.tabla.heading("id", text="Orden")
        self.tabla.heading("placa", text="Placa")
        self.tabla.heading("empleado", text="Empleado")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("total", text="Total")

        self.tabla.column("id", width=70, anchor="center")
        self.tabla.column("placa", width=110, anchor="center")
        self.tabla.column("empleado", width=160, anchor="center")
        self.tabla.column("estado", width=120, anchor="center")
        self.tabla.column("total", width=120, anchor="center")

        self.tabla.pack(fill="both", expand=True)

    # ---------- Carga de datos ----------

    def _cargar_vehiculos(self):
        self.vehiculos_disponibles = VehiculosLogica.obtener_vehiculos()

        if not self.vehiculos_disponibles:
            self.combo_vehiculo.configure(values=["Sin vehículos registrados"])
            self.combo_vehiculo.set("Sin vehículos registrados")
            return

        opciones = [
            f"{v['id']} - {v['placa']} ({v['nombre_cliente']})"
            for v in self.vehiculos_disponibles
        ]
        self.combo_vehiculo.configure(values=opciones)
        self.combo_vehiculo.set(opciones[0])

    def _cargar_servicios(self):
        self.checks.clear()
        for widget in self.frame_servicios.winfo_children():
            widget.destroy()

        for idx, servicio in enumerate(ServiciosLogica.listar_servicios()):
            variable = ctk.IntVar(value=0)
            chk = ctk.CTkCheckBox(
                self.frame_servicios,
                text=f"{servicio['nombre']} * ${servicio['precio']:,.0f}",
                variable=variable,
                onvalue=1,
                offvalue=0,
                command=self._actualizar_total,
                text_color="#111111",
                fg_color="#F68B2E",
                hover_color="#E0781E",
                font=("Segoe UI", 11)
            )
            chk.grid(row=idx // 3, column=idx % 3, sticky="w", padx=12, pady=6)
            self.checks.append((servicio, variable))

    def _cargar_empleados(self):
        self.empleados_disponibles = EmpleadosLogica.listar_empleados()

        if not self.empleados_disponibles:
            self.combo_empleado.configure(values=["Sin empleados registrados"])
            self.combo_empleado.set("Sin empleados registrados")
            return

        opciones = [f"{e['id']} - {e['nombre']}" for e in self.empleados_disponibles]
        self.combo_empleado.configure(values=opciones)
        self.combo_empleado.set(opciones[0])

    def _cargar_ordenes(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.ordenes = {}
        for orden in ServiciosLogica.listar_ordenes():
            # Las entregadas ya terminaron su ciclo: no se muestran aquí
            if orden["estado"] == "entregado":
                continue
            self.ordenes[orden["id"]] = orden
            self.tabla.insert(
                "", "end",
                values=(
                    orden["id"],
                    orden["placa"],
                    orden["nombre_empleado"] or "Sin asignar",
                    orden["estado"].capitalize(),
                    f"${orden['total']:,.0f}",
                ),
            )

    # ---------- Utilidades ----------

    def _actualizar_total(self):
        total = sum(s["precio"] for s, var in self.checks if var.get() == 1)
        self.label_total.configure(text=f"Total : $ {total:,.0f}")

    def _limpiar_seleccion(self):
        for _, variable in self.checks:
            variable.set(0)
        self._actualizar_total()

    def _obtener_vehiculo_id(self):
        if not self.vehiculos_disponibles:
            return None
        return int(self.combo_vehiculo.get().split(" - ")[0])

    def _obtener_empleado_id(self):
        if not self.empleados_disponibles:
            return None
        return int(self.combo_empleado.get().split(" - ")[0])

    # ---------- Eventos ----------

    def _evento_asignar(self):
        vehiculo_id = self._obtener_vehiculo_id()
        if vehiculo_id is None:
            messagebox.showerror(
                "Error", "Debe registrar al menos un vehículo antes de asignar servicios."
            )
            return

        servicio_ids = [s["id"] for s, var in self.checks if var.get() == 1]

        try:
            orden_id = ServiciosLogica.asignar_servicios(
                vehiculo_id, servicio_ids, empleado_id=self._obtener_empleado_id()
            )
            messagebox.showinfo(
                "Éxito", f"Orden #{orden_id} creada en estado 'Espera'."
            )
            self._limpiar_seleccion()
            self._cargar_ordenes()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_avanzar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Por favor seleccione una orden de la tabla."
            )
            return

        orden_id = int(self.tabla.item(seleccion[0])["values"][0])
        orden = self.ordenes[orden_id]

        siguiente = ServiciosLogica.siguiente_estado(orden["estado"])
        if siguiente is None:
            messagebox.showinfo("Atención", "Esta orden ya fue entregada.")
            return

        # Si la orden no tiene empleado, se usa el elegido en el desplegable
        empleado_id = None
        if orden["empleado_id"] is None:
            empleado_id = self._obtener_empleado_id()

        try:
            ServiciosLogica.cambiar_estado_orden(
                orden_id, siguiente, empleado_id=empleado_id
            )
            messagebox.showinfo(
                "Éxito", f"Orden #{orden_id} pasó a '{siguiente.capitalize()}'."
            )
            self._cargar_ordenes()
        except ValueError as err:
            messagebox.showerror("Error", str(err))
