import customtkinter as ctk
from db.conexion import inicializar_db
from presentacion.login_view import LoginView
from presentacion.dashboard_view import DashboardView
from presentacion.clientes_screen import ClientesScreen
from presentacion.vehiculos_screen import VehiculosScreen
from presentacion.empleados_screen import EmpleadosScreen
from presentacion.servicios_screen import ServiciosScreen
from presentacion.inventario_screen import InventarioScreen
from presentacion.facturacion_screen import FacturacionScreen

class AplicacionPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoWash System")
        self.geometry("900x650")
        self.minsize(800, 600)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        inicializar_db()
        self.mostrar_login()

    def _limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self._limpiar_pantalla()
        self.vista_actual = LoginView(self, al_ingresar=self.mostrar_dashboard)
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_dashboard(self):
        self._limpiar_pantalla()
        self.vista_actual = DashboardView(
            self,
            al_ir_clientes=self.mostrar_clientes,
            al_ir_vehiculos=self.mostrar_vehiculos,
            al_ir_empleados=self.mostrar_empleados,
            al_ir_servicios=self.mostrar_servicios,
            al_ir_inventario=self.mostrar_inventario,
            al_ir_facturacion=self.mostrar_facturacion,
            al_cerrar_sesion=self.mostrar_login
        )
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_clientes(self):
        self._limpiar_pantalla()
        self.vista_actual = ClientesScreen(self, al_volver=self.mostrar_dashboard)

    def mostrar_vehiculos(self):
        self._limpiar_pantalla()
        self.vista_actual = VehiculosScreen(self, al_volver=self.mostrar_dashboard)

    def mostrar_empleados(self):
        self._limpiar_pantalla()
        self.vista_actual = EmpleadosScreen(self, al_volver=self.mostrar_dashboard)

    def mostrar_servicios(self):
        self._limpiar_pantalla()
        self.vista_actual = ServiciosScreen(self, al_volver=self.mostrar_dashboard)

    def mostrar_inventario(self):
        self._limpiar_pantalla()
        self.vista_actual = InventarioScreen(self)

    def mostrar_facturacion(self):
        self._limpiar_pantalla()
        self.vista_actual = FacturacionScreen(self)


if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()