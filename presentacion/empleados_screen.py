from tkinter import ttk, messagebox
import customtkinter as ctk

from logica.empleados_logica import EmpleadosLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class EmpleadosScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión de Empleados fiel al diseño Figma (Imagen 2):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Empleados'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Tarjeta blanca 'Registrar empleado' con campo Nombre completo (borde negro) y botón #F68B2E.
    - Contenedor blanco inferior con tabla Autowash.Treeview (ID y NOMBRE centrados).
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

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_empleados()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Empleados",
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
            text="Gestión de empleados",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Registro y consulta de empleados",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 18))

        # ————— TARJETA BLANCA: REGISTRAR EMPLEADO —————
        card_form = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_form.pack(fill="x", pady=(0, 20))

        inner_form = ctk.CTkFrame(card_form, fg_color="transparent")
        inner_form.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            inner_form,
            text="Registrar empleado",
            font=("Georgia", 22),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 14))

        # Fila con 2 columnas: Izquierda (Label + Entry) | Derecha (Botón alineado abajo)
        fila_form = ctk.CTkFrame(inner_form, fg_color="transparent")
        fila_form.pack(fill="x")
        fila_form.grid_columnconfigure(0, weight=1)
        fila_form.grid_columnconfigure(1, weight=0)

        col_izq = ctk.CTkFrame(fila_form, fg_color="transparent")
        col_izq.grid(row=0, column=0, sticky="ew", padx=(0, 16))

        ctk.CTkLabel(
            col_izq,
            text="Nombre completo",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.txt_nombre = ctk.CTkEntry(
            col_izq,
            placeholder_text="Nombre completo del empleado",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=42,
            font=("Segoe UI", 12)
        )
        self.txt_nombre.pack(fill="x")

        btn_registrar = ctk.CTkButton(
            fila_form,
            text="Registrar empleado",
            command=self._registrar,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            height=42,
            corner_radius=14,
            width=200
        )
        btn_registrar.grid(row=0, column=1, sticky="s")

        # ————— TABLA INFERIOR EN CONTENEDOR BLANCO —————
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

        self.tabla = ttk.Treeview(
            inner_tabla,
            columns=("ID", "Nombre"),
            show="headings",
            height=9,
            style="Autowash.Treeview"
        )
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="NOMBRE")

        self.tabla.column("ID", width=100, anchor="center")
        self.tabla.column("Nombre", width=450, anchor="center")

        self.tabla.pack(fill="both", expand=True)

    def _cargar_empleados(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            empleados = EmpleadosLogica.listar_empleados()
            for emp in empleados:
                self.tabla.insert("", "end", values=(emp.get("id"), emp.get("nombre")))
        except Exception as e:
            print(f"Error al cargar empleados: {e}")

    def _registrar(self):
        nombre = self.txt_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del empleado es obligatorio.")
            return

        try:
            EmpleadosLogica.registrar_empleado(nombre)
            messagebox.showinfo("Éxito", "Empleado registrado correctamente.")
            self.txt_nombre.delete(0, "end")
            self._cargar_empleados()
        except ValueError as err:
            messagebox.showerror("Error", str(err))
