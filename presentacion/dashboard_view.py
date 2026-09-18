import customtkinter as ctk


class DashboardView(ctk.CTkFrame):

  def __init__(self, master, al_cerrar_sesion, al_abrir_clientes, al_abrir_vehiculos):
    super().__init__(master)
    self.master = master
    self.al_cerrar_sesion = al_cerrar_sesion
    self.al_abrir_clientes = al_abrir_clientes
    self.al_abrir_vehiculos = al_abrir_vehiculos
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()

  def _crear_interfaz(self):

    header_frame = ctk.CTkFrame(self, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        header_frame,
        text="Sistema de Gestión - Lavadero de Vehículos",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(side="left")

    ctk.CTkButton(
        header_frame,
        text="Cerrar Sesión",
        fg_color="red",
        hover_color="#8B0000",
        width=110,
        command=self.al_cerrar_sesion,
    ).pack(side="right", padx=5)

    ctk.CTkLabel(
        self,
        text="Seleccione un módulo para continuar",
        font=ctk.CTkFont(size=14),
    ).pack(pady=(30, 20))

    menu_frame = ctk.CTkFrame(self, fg_color="transparent")
    menu_frame.pack(pady=10)

    ctk.CTkButton(
        menu_frame,
        text="Gestión de Clientes",
        width=220,
        height=45,
        fg_color="#1f538d",
        command=self.al_abrir_clientes,
    ).pack(pady=10)

    ctk.CTkButton(
        menu_frame,
        text="Gestión de Vehículos",
        width=220,
        height=45,
        fg_color="#1f538d",
        command=self.al_abrir_vehiculos,
    ).pack(pady=10)