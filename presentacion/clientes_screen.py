from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.clientes_logica import ClientesLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class ClientesScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión de Clientes.
    Diseño fiel al prototipo Figma/React (AutowashLayout):
    - Barra lateral #0B4F66 con logo AUTOWASH SYSTEM y sección activa 'Clientes' en #3F8FA9.
    - Área principal #E7F9FF con tarjeta blanca para el formulario y tarjeta para la tabla.
    - Campos de entrada con altura 42, bordes redondeados (14px) y botón primario #F68B2E.
    - Tabla con cabecera #BCE3F0 y filas estilizadas en blanco.
    """

    def __init__(self, master, al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_servicios=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(master, fg_color="#E7F9FF", corner_radius=0)
        self.master = master
        self.al_volver = al_volver
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

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_tabla()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Clientes",
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

        if self.al_ir_vehiculos:
            btn_ir_vehiculos = ctk.CTkButton(
                header_nav,
                text="Ir a 2. Vehículos →",
                command=self.al_ir_vehiculos,
                fg_color="#1f538d",
                hover_color="#163f6b",
                text_color="#FFFFFF",
                font=("Segoe UI", 12, "bold"),
                corner_radius=12,
                height=34,
            )
            btn_ir_vehiculos.pack(side="right")

        # — Título y subtítulo —
        title_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        title_box.pack(fill="x", pady=(6, 16))

        ctk.CTkLabel(
            title_box,
            text="Gestión de clientes",
            font=("Segoe UI", 28, "bold"),
            text_color="#111111",
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            title_box,
            text="Registro y consulta de clientes",
            font=("Segoe UI", 14),
            text_color="#555555",
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # ————— TARJETA: REGISTRAR CLIENTE —————
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
            text="Registrar cliente",
            font=("Segoe UI", 20, "bold"),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 16))

        grid_inputs = ctk.CTkFrame(inner_form, fg_color="transparent")
        grid_inputs.pack(fill="x")
        grid_inputs.grid_columnconfigure(0, weight=1)
        grid_inputs.grid_columnconfigure(1, weight=1)

        # Nombre completo
        ctk.CTkLabel(
            grid_inputs,
            text="Nombre completo",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 4))

        self.entry_nombre = ctk.CTkEntry(
            grid_inputs,
            placeholder_text="Nombre completo del cliente",
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            placeholder_text_color="#666666",
            font=("Segoe UI", 12),
        )
        self.entry_nombre.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(0, 12))

        # Teléfono / WhatsApp
        ctk.CTkLabel(
            grid_inputs,
            text="Teléfono / WhatsApp",
            font=("Segoe UI", 11, "bold"),
            text_color="#555555",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 4))

        self.entry_telefono = ctk.CTkEntry(
            grid_inputs,
            placeholder_text="Teléfono / WhatsApp",
            height=42,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            text_color="#111111",
            placeholder_text_color="#666666",
            font=("Segoe UI", 12),
        )
        self.entry_telefono.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 12))

        # Botón Registrar cliente (alineado a la derecha)
        btn_registrar = ctk.CTkButton(
            grid_inputs,
            text="Registrar cliente",
            command=self._evento_registrar,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            height=42,
            corner_radius=14,
            width=218,
            font=("Segoe UI", 12, "bold"),
        )
        btn_registrar.grid(row=2, column=1, sticky="e", padx=(12, 0), pady=(4, 0))

        # ————— TARJETA: TABLA DE CLIENTES —————
        card_tabla = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_color="#CCE5F0",
            border_width=1,
        )
        card_tabla.pack(fill="both", expand=True, pady=(0, 16))

        inner_tabla = ctk.CTkFrame(card_tabla, fg_color="transparent")
        inner_tabla.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("id", "nombre", "telefono")
        self.tabla = ttk.Treeview(
            inner_tabla,
            columns=columnas,
            show="headings",
            style="Autowash.Treeview",
            height=8,
        )

        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="NOMBRE")
        self.tabla.heading("telefono", text="TELÉFONO")

        self.tabla.column("id", width=60, anchor="center")
        self.tabla.column("nombre", width=340, anchor="center")
        self.tabla.column("telefono", width=220, anchor="center")

        scroll_y = ttk.Scrollbar(inner_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True)

        # ————— BOTÓN ELIMINAR (debajo de la tabla, a la izquierda) —————
        btn_eliminar = ctk.CTkButton(
            self.scroll_body,
            text="Eliminar cliente seleccionado",
            command=self._evento_eliminar,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#EF4444",
            text_color="#B91C1C",
            hover_color="#FEE2E2",
            corner_radius=14,
            height=46,
            font=("Segoe UI", 12, "bold"),
        )
        btn_eliminar.pack(anchor="w", pady=(0, 20))

    def _cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = ClientesLogica.listar_todos_los_clientes()
        for cliente in registros:
            self.tabla.insert(
                "",
                "end",
                values=(cliente["id"], cliente["nombre"], cliente["telefono"] or ""),
            )

    def _limpiar_formulario(self):
        self.entry_nombre.delete(0, "end")
        self.entry_telefono.delete(0, "end")

    def _evento_registrar(self):
        nombre = self.entry_nombre.get()
        telefono = self.entry_telefono.get()

        try:
            ClientesLogica.registrar_cliente(nombre, telefono)
            messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            self._limpiar_formulario()
            self._cargar_tabla()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor seleccione un cliente de la tabla.")
            return

        item = self.tabla.item(seleccion[0])
        id_cliente = item["values"][0]

        confirmar = messagebox.askyesno("Confirmar", f"¿Desea eliminar al cliente ID {id_cliente}?")
        if confirmar:
            try:
                ClientesLogica.eliminar_cliente(id_cliente)
                messagebox.showinfo("Éxito", "El cliente ha sido eliminado correctamente.")
                self._cargar_tabla()
            except ValueError as err:
                messagebox.showerror("Error", str(err))
