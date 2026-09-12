import customtkinter as ctk
from db.conexion import inicializar_db
from presentacion.dashboard_view import DashboardView
from presentacion.login_view import LoginView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("AutoWash System - Acceso")
    self.geometry("500x550")

    inicializar_db()

    self.vista_login = LoginView(
        self, al_ingresar_exitoso=self.mostrar_dashboard
    )

  def mostrar_dashboard(self):
    self.title("AutoWash System - Gestión de Lavadero")
    self.dashboard = DashboardView(self)


if __name__ == "__main__":
  app = MainApp()
  app.mainloop()