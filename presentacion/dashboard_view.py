import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_empleados=None, al_ir_servicios=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_cerrar_sesion=None):  # ← Se agregó al_ir_reportes=None
        super().__init__(parent)
        self.al_ir_clientes = al_ir_clientes
        self.al_ir_vehiculos = al_ir_vehiculos
        self.al_ir_empleados = al_ir_empleados
        self.al_ir_servicios = al_ir_servicios
        self.al_ir_inventario = al_ir_inventario
        self.al_ir_facturacion = al_ir_facturacion
        self.al_ir_reportes = al_ir_reportes  # ← Guardado de la referencia
        self.al_cerrar_sesion = al_cerrar_sesion

        self.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        titulo = ctk.CTkLabel(header_frame, text="Panel Principal", font=("Roboto", 26, "bold"))
        titulo.pack(side="left")

        if self.al_cerrar_sesion:
            btn_salir = ctk.CTkButton(
                header_frame, text="Cerrar Sesión", command=self.al_cerrar_sesion,
                fg_color="#d32f2f", hover_color="#b71c1c"
            )
            btn_salir.pack(side="right")

        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(fill="both", expand=True, pady=10)

        self._crear_boton(menu_frame, "Gestión de Clientes", self.al_ir_clientes)
        self._crear_boton(menu_frame, "Gestión de Vehículos", self.al_ir_vehiculos)
        self._crear_boton(menu_frame, "Gestión de Empleados", self.al_ir_empleados)
        self._crear_boton(menu_frame, "Gestión de Servicios", self.al_ir_servicios)
        self._crear_boton(menu_frame, "Gestión de Inventario", self.al_ir_inventario)
        self._crear_boton(menu_frame, "Gestión de Facturación", self.al_ir_facturacion)
        self._crear_boton(menu_frame, "Reportes y Estadísticas", self.al_ir_reportes)  # ← Se creó el botón de Reportes

    def _crear_boton(self, parent, texto, comando):
        if comando is None:
            return
        btn = ctk.CTkButton(parent, text=texto, command=comando, font=("Roboto", 16), height=50)
        btn.pack(pady=10, padx=50, fill="x")