import customtkinter as ctk
from db.conexion import inicializar_db
from presentacion.dashboard_view import DashboardView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("AutoWash System - Gestión de Lavadero")
    self.geometry("500x450")

    inicializar_db()

    self.dashboard = DashboardView(self)


if __name__ == "__main__":
  app = MainApp()
  app.mainloop()