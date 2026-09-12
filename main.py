import customtkinter as ctk
from db.conexion import inicializar_db
from presentacion.clientes_screen import ClientesScreen
from presentacion.dashboard_view import DashboardView
from presentacion.login_view import LoginView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):

  def __init__(self):
    super().__init__()
    self.geometry("600x650")
    inicializar_db()

    self.dashboard = None
    self.vista_login = None
    self.vista_clientes = None
    self.mostrar_login()

  def mostrar_login(self):
    self._destruir_vistas()
    self.title("AutoWash System - Acceso")
    self.vista_login = LoginView(
        self, al_ingresar_exitoso=self.mostrar_dashboard
    )

  def mostrar_dashboard(self):
    self._destruir_vistas()
    self.title("AutoWash System - Gestión de Lavadero")
    self.dashboard = DashboardView(
        self,
        al_cerrar_sesion=self.mostrar_login,
        al_abrir_clientes=self.mostrar_clientes,
    )

  def mostrar_clientes(self):
    self._destruir_vistas()
    self.title("AutoWash System - Clientes Frecuentes")
    self.vista_clientes = ClientesScreen(
        self, al_volver=self.mostrar_dashboard
    )

  def _destruir_vistas(self):
    if self.vista_login:
      self.vista_login.destroy()
      self.vista_login = None
    if self.dashboard:
      self.dashboard.destroy()
      self.dashboard = None
    if self.vista_clientes:
      self.vista_clientes.destroy()
      self.vista_clientes = None


if __name__ == "__main__":
  app = MainApp()
  app.mainloop()