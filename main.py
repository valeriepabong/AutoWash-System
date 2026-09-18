import customtkinter as ctk

from db.conexion import inicializar_db
from presentacion.login_view import LoginView
from presentacion.dashboard_view import DashboardView
from presentacion.clientes_screen import ClientesScreen
from presentacion.vehiculos_screen import VehiculosScreen


class AplicacionPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AutoWash System")
        self.geometry("800x600")

        inicializar_db()

        self.mostrar_login()

    def _limpiar_pantalla(self):
        """Destruye cualquier pantalla (frame) actualmente visible."""
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self._limpiar_pantalla()
        LoginView(self, al_ingresar_exitoso=self.mostrar_dashboard)

    def mostrar_dashboard(self):
        self._limpiar_pantalla()
        DashboardView(
            self,
            al_cerrar_sesion=self.mostrar_login,
            al_abrir_clientes=self.mostrar_clientes,
            al_abrir_vehiculos=self.mostrar_vehiculos,
        )

    def mostrar_clientes(self):
        self._limpiar_pantalla()
        ClientesScreen(self, al_volver=self.mostrar_dashboard)

    def mostrar_vehiculos(self):
        self._limpiar_pantalla()
        VehiculosScreen(self)  # más abajo explico el detalle de esta pantalla


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = AplicacionPrincipal()
    app.mainloop()