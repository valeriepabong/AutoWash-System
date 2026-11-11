from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.clientes_logica import ClientesLogica
from logica.vehiculos_logica import VehiculosLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class VehiculosScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión de Vehículos.
    Diseño fiel al prototipo Figma/React (AutowashLayout):
    - Barra lateral #0B4F66 con logo AUTOWASH SYSTEM y sección activa 'Vehículos' en #3F8FA9.
    - Área principal #E7F9FF con tarjeta de formulario de 3 columnas y tarjeta para la tabla.
    - Campos con altura 42, bordes redondeados (14px) y botón primario #F68B2E.
    - Tabla estilizada con cabecera #BCE3F0 y filas blancas #FFFFFF.
    """

    def __init__(self, parent, al_volver=None, al_ir_dashboard=None,
                 al_ir_servicios=None, al_ir_clientes=None,
                 al_ir_vehiculos=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(parent, fg_color="#E7F9FF", corner_radius=0)
        self.al_volver = al_volver
        self.al_ir_dashboard = al_ir_dashboard or al_volver
        self.al_ir_servicios = al_ir_servicios
        self.al_ir_clientes = al_ir_clientes
        self.al_ir_vehiculos = al_ir_vehiculos
        self.al_ir_empleados = al_ir_empleados
        self.al_ir_inventario = al_ir_inventario
        self.al_ir_facturacion = al_ir_facturacion
        self.al_ir_reportes = al_ir_reportes
        self.al_ir_catalogo = al_ir_catalogo
        self.al_ir_facturas = al_ir_facturas
        self.al_cerrar_sesion = al_cerrar_sesion

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_clientes()
        self._cargar_vehiculos()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Vehículos",
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

        # ————— ENCABEZADO Y NAVEGACIÓN RÁPIDA —————
        header_nav = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_nav.pack(fill="x", pady=(0, 6))

        if self.al_volver:
            btn_volver_panel = ctk.CTkButton(
                header_nav,
                text="← volver al panel principal",
                command=self.al_volver,
                text_color="#0B4F66",
                fg_color="transparent",
                hover_color="#D0EDF8",
                font=("Segoe UI", 12, "bold"),
                anchor="w",
                height=32,
            )
            btn_volver_panel.pack(side="left")

        if self.al_ir_servicios:
            btn_servicios = ctk.CTkButton(
                header_nav,
                text="Ir a 3. Asignar Servicio →",
                command=self.al_ir_servicios,
                fg_color="#1f538d",
                hover_color="#163f6b",
                text_color="#FFFFFF",
                font=("Segoe UI", 12, "bold"),
                corner_radius=12,
                height=34,
            )
            btn_servicios.pack(side="right")

        if self.al_ir_clientes:
            btn_clientes = ctk.CTkButton(
                header_nav,
                text="← 1. Clientes",
                command=self.al_ir_clientes,
                fg_color="#555555",
                hover_color="#333333",
                text_color="#FFFFFF",
                font=("Segoe UI", 12),
                corner_radius=12,
                height=34,
            )
            btn_clientes.pack(side="right", padx=(0, 10))

        # — Título y subtítulo —
        title_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        title_box.pack(fill="x", pady=(6, 16))

        ctk.CTkLabel(
            title_box,
            text="Gestión de vehículos",
            font=("Segoe UI", 28, "bold"),
            text_color="#111111",
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            title_box,
            text="Vehículos asociados a cada cliente",
            font=("Segoe UI", 14),
            text_color="#555555",
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # ————— TARJETA: REGISTRAR VEHÍCULO —————
        card_registro = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_color="#CCE5F0",
            border_width=1,
        )
        card_registro.pack(fill="x", pady=(0, 20))

        inner_form = ctk.CTkFrame(card_registro, fg_color="transparent")
        inner_form.pack(fill="both", expand=True, padx=24, pady=22)

        ctk.CTkLabel(
            inner_form,
            text="Registrar vehículo",
            font=("Segoe UI", 20, "bold"),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 16))

        grid_inputs = ctk.CTkFrame(inner_form, fg_color="transparent")
        grid_inputs.pack(fill="x")
        grid_inputs.grid_columnconfigure(0, weight=1)
        grid_inputs.grid_columnconfigure(1, weight=1)
        grid_inputs.grid_columnconfigure(2, weight=1)

        # Fila 0, Col 0: Placa
        ctk.CTkLabel(
            grid_inputs,
            text="Placa",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))

        self.txt_placa = ctk.CTkEntry(
            grid_inputs,
            placeholder_text="Placa del vehículo",
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            placeholder_text_color="#666666",
            font=("Segoe UI", 12),
        )
        self.txt_placa.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        # Fila 0, Col 1: Marca
        ctk.CTkLabel(
            grid_inputs,
            text="Marca",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=8, pady=(0, 4))

        self.txt_marca = ctk.CTkEntry(
            grid_inputs,
            placeholder_text="Marca del vehículo",
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            placeholder_text_color="#666666",
            font=("Segoe UI", 12),
        )
        self.txt_marca.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 12))

        # Fila 0, Col 2: Modelo
        ctk.CTkLabel(
            grid_inputs,
            text="Modelo",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=(8, 0), pady=(0, 4))

        self.txt_modelo = ctk.CTkEntry(
            grid_inputs,
            placeholder_text="Modelo del vehículo",
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            placeholder_text_color="#666666",
            font=("Segoe UI", 12),
        )
        self.txt_modelo.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(0, 12))

        # Fila 2, Col 0: Tipo
        ctk.CTkLabel(
            grid_inputs,
            text="Tipo",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 4))

        tipos_vehiculo = ["Sedán", "SUV", "Camioneta", "Hatchback", "Moto", "Automóvil"]
        self.cb_tipo = ctk.CTkComboBox(
            grid_inputs,
            values=tipos_vehiculo,
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            font=("Segoe UI", 12),
            state="readonly",
        )
        self.cb_tipo.set("Sedán")
        self.cb_tipo.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        # Fila 2, Col 1: Cliente
        ctk.CTkLabel(
            grid_inputs,
            text="Cliente",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=2, column=1, sticky="w", padx=8, pady=(0, 4))

        self.cb_clientes = ctk.CTkComboBox(
            grid_inputs,
            values=["Sin clientes registrados"],
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            font=("Segoe UI", 12),
            state="readonly",
        )
        self.cb_clientes.grid(row=3, column=1, sticky="ew", padx=8, pady=(0, 12))

        # Fila 2, Col 2: Botón Registrar vehículo (alineado abajo)
        btn_registrar = ctk.CTkButton(
            grid_inputs,
            text="Registrar vehículo",
            command=self._registrar,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            height=42,
            corner_radius=14,
            width=218,
            font=("Segoe UI", 12, "bold"),
        )
        btn_registrar.grid(row=3, column=2, sticky="se", padx=(8, 0), pady=(0, 12))

        # ————— TARJETA: TABLA DE VEHÍCULOS —————
        card_tabla = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_color="#CCE5F0",
            border_width=1,
        )
        card_tabla.pack(fill="both", expand=True, pady=(0, 20))

        inner_tabla = ctk.CTkFrame(card_tabla, fg_color="transparent")
        inner_tabla.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("ID", "Placa", "Marca", "Modelo", "Tipo", "Cliente")
        self.tabla = ttk.Treeview(
            inner_tabla,
            columns=columnas,
            show="headings",
            style="Autowash.Treeview",
            height=8,
        )

        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Placa", text="PLACA")
        self.tabla.heading("Marca", text="MARCA")
        self.tabla.heading("Modelo", text="MODELO")
        self.tabla.heading("Tipo", text="TIPO")
        self.tabla.heading("Cliente", text="CLIENTE")

        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Placa", width=110, anchor="center")
        self.tabla.column("Marca", width=130, anchor="center")
        self.tabla.column("Modelo", width=130, anchor="center")
        self.tabla.column("Tipo", width=110, anchor="center")
        self.tabla.column("Cliente", width=200, anchor="center")

        scroll_y = ttk.Scrollbar(inner_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True)

    def _cargar_clientes(self):
        try:
            clientes = ClientesLogica.listar_todos_los_clientes()
            if clientes:
                opciones = [f"{c['id']} - {c['nombre']}" for c in clientes]
                self.cb_clientes.configure(values=opciones)
                self.cb_clientes.set(opciones[0])
            else:
                self.cb_clientes.configure(values=["Sin clientes registrados"])
                self.cb_clientes.set("Sin clientes registrados")
        except Exception:
            self.cb_clientes.configure(values=["Sin clientes registrados"])

    def _cargar_vehiculos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            vehiculos = VehiculosLogica.obtener_vehiculos()
            for v in vehiculos:
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        v.get("id"),
                        v.get("placa"),
                        v.get("marca", ""),
                        v.get("modelo", ""),
                        v.get("tipo_vehiculo"),
                        v.get("nombre_cliente", ""),
                    ),
                )
        except Exception as e:
            print(f"[Vehículos] Error al cargar vehículos: {e}")

    def _registrar(self):
        cliente_sel = self.cb_clientes.get()
        if not cliente_sel or cliente_sel == "Sin clientes registrados":
            messagebox.showwarning("Advertencia", "Debe seleccionar un cliente válido.")
            return

        placa = self.txt_placa.get().strip()
        if not placa:
            messagebox.showwarning("Advertencia", "La placa es obligatoria.")
            return

        cliente_id = int(cliente_sel.split(" - ")[0])
        marca = self.txt_marca.get().strip()
        modelo = self.txt_modelo.get().strip()
        tipo = self.cb_tipo.get()

        try:
            VehiculosLogica.registrar_vehiculo(placa, tipo, cliente_id, marca, modelo)
            messagebox.showinfo("Éxito", "Vehículo registrado correctamente.")
            self.txt_placa.delete(0, "end")
            self.txt_marca.delete(0, "end")
            self.txt_modelo.delete(0, "end")
            self._cargar_vehiculos()
        except ValueError as err:
            messagebox.showerror("Error", str(err))
