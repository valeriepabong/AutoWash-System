from tkinter import ttk
import customtkinter as ctk


def configurar_estilo_tabla():
    """Configura el estilo visual personalizado de ttk.Treeview según el diseño Figma (AutowashLayout)."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Autowash.Treeview",
        background="#FFFFFF",
        foreground="#111111",
        fieldbackground="#FFFFFF",
        rowheight=42,
        font=("Segoe UI", 11),
        borderwidth=0,
    )
    style.map(
        "Autowash.Treeview",
        background=[("selected", "#BCE3F0")],
        foreground=[("selected", "#111111")],
    )

    style.configure(
        "Autowash.Treeview.Heading",
        background="#BCE3F0",
        foreground="#333333",
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(8, 8),
    )
    style.map(
        "Autowash.Treeview.Heading",
        background=[("active", "#A6D8E8")],
    )


def _normalizar_clave(texto):
    """Normaliza tildes y mayúsculas para comparar nombres de sección activa."""
    norm = (
        (texto or "")
        .strip()
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    if norm == "panel":
        return "panel principal"
    return norm


class SidebarComponent(ctk.CTkFrame):
    """
    Barra lateral unificada de AutoWash System.
    Mismo diseño en el Dashboard y en todas las pantallas secundarias:
    - Ancho fijo 215px, fondo #0B4F66, logo 🚘 AUTOWASH SYSTEM.
    - 3 secciones guiadas paso a paso con encabezados en #F68B2E.
    - Ítem activo resaltado en #3F8FA9.
    - Botón inferior fijo '⎋  Cerrar sesión' en #F16262.
    """

    def __init__(self, parent, seccion_activa="",
                 al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_servicios=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(parent, fg_color="#0B4F66", width=215, corner_radius=0)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)

        self.seccion_activa = seccion_activa
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

        self._construir()

    def _construir(self):
        # — Logotipo superior —
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(16, 0))

        ctk.CTkLabel(
            logo_frame,
            text="🚘",
            font=("Segoe UI Emoji", 28),
            text_color="#F68B2E",
            anchor="w"
        ).pack(anchor="w")

        brand_row = ctk.CTkFrame(logo_frame, fg_color="transparent")
        brand_row.pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            brand_row,
            text="AUTOWASH ",
            font=("Segoe UI", 15, "bold"),
            text_color="#FFFFFF"
        ).pack(side="left")

        ctk.CTkLabel(
            brand_row,
            text="SYSTEM",
            font=("Segoe UI", 15, "bold"),
            text_color="#F68B2E"
        ).pack(side="left")

        # — Botón inferior fijo: Cerrar sesión —
        btn_logout = ctk.CTkButton(
            self,
            text="⎋  Cerrar sesión",
            command=self.al_cerrar_sesion if self.al_cerrar_sesion else (lambda: None),
            fg_color="transparent",
            hover_color="#1A1111",
            text_color="#F16262",
            font=("Segoe UI", 12),
            anchor="w",
            height=36,
            corner_radius=12
        )
        btn_logout.pack(side="bottom", fill="x", padx=10, pady=10)

        # — Menú de navegación organizado en 3 secciones guiadas —
        nav_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color="#0A4358",
            scrollbar_button_color="#F68B2E",
            scrollbar_button_hover_color="#F79D4F"
        )
        nav_scroll.pack(fill="both", expand=True, padx=(6, 4), pady=(12, 4))

        secciones = [
            ("RECEPCIÓN Y FLUJO", [
                ("⊞  Panel principal",     self.al_ir_dashboard,   "Panel principal"),
                ("👥  1. Clientes",         self.al_ir_clientes,    "Clientes"),
                ("🚗  2. Vehículos",        self.al_ir_vehiculos,   "Vehiculos"),
                ("💧  3. Asignar Servicio", self.al_ir_servicios,   "Servicios"),
            ]),
            ("INVENTARIO Y CATÁLOGO", [
                ("📦  Inventario",          self.al_ir_inventario,  "Inventario"),
                ("📖  Catálogo y Recetas",  self.al_ir_catalogo,    "Catálogo"),
                ("👷  Empleados",           self.al_ir_empleados,   "Empleados"),
            ]),
            ("VENTAS Y REPORTES", [
                ("🧾  Facturación",         self.al_ir_facturacion, "Facturacion"),
                ("📑  Ventas y Facturas",   self.al_ir_facturas,    "Facturas"),
                ("📊  Reportes del Día",    self.al_ir_reportes,    "Reportes"),
            ]),
        ]

        clave_activa = _normalizar_clave(self.seccion_activa)

        for s_idx, (titulo_seccion, items) in enumerate(secciones):
            ctk.CTkLabel(
                nav_scroll,
                text=titulo_seccion,
                font=("Segoe UI", 9, "bold"),
                text_color="#F68B2E",
                anchor="w"
            ).pack(fill="x", padx=10, pady=(12, 3) if s_idx > 0 else (4, 3))

            for texto, cmd, clave in items:
                activo = (clave_activa == _normalizar_clave(clave))
                btn = ctk.CTkButton(
                    nav_scroll,
                    text=texto,
                    command=cmd if cmd else (lambda: None),
                    fg_color="#3F8FA9" if activo else "transparent",
                    hover_color="#336E84",
                    text_color="#FFFFFF",
                    font=("Segoe UI", 12, "bold") if activo else ("Segoe UI", 12),
                    anchor="w",
                    height=34,
                    corner_radius=10
                )
                btn.pack(fill="x", pady=1)
