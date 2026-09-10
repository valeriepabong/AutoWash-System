import customtkinter as ctk
from tkinter import messagebox
from logica.gestion_servicios import ServicioLavado


class DashboardView(ctk.CTkFrame):

  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()

  def _crear_interfaz(self):
    # Título
    self.label_titulo = ctk.CTkLabel(
        self,
        text="Registro de Lavado de Vehículos",
        font=ctk.CTkFont(size=20, weight="bold"),
    )
    self.label_titulo.pack(pady=10)

    # Campo de Placa
    self.entry_placa = ctk.CTkEntry(
        self, placeholder_text="Ingrese la placa (Ej: ABC123)"
    )
    self.entry_placa.pack(pady=10, fill="x", padx=40)

    # Selección de Tipo de Vehículo
    self.combo_vehiculo = ctk.CTkOptionMenu(
        self, values=["Automóvil", "Camioneta", "Moto"]
    )
    self.combo_vehiculo.pack(pady=10)

    # Selección de Tipo de Lavado
    self.combo_lavado = ctk.CTkOptionMenu(
        self, values=["Sencillo", "General", "Especial (Polichado)"]
    )
    self.combo_lavado.pack(pady=10)

    # Botón de Registrar
    self.btn_registrar = ctk.CTkButton(
        self,
        text="Registrar Servicio",
        command=self._evento_registrar,
        fg_color="green",
    )
    self.btn_registrar.pack(pady=15)

  def _evento_registrar(self):
    placa = self.entry_placa.get()
    vehiculo = self.combo_vehiculo.get()
    lavado = self.combo_lavado.get()

    try:
      precio = ServicioLavado.registrar_servicio(placa, vehiculo, lavado)
      messagebox.showinfo(
          "Registro Exitoso",
          f"Servicio registrado correctamente.\nTotal a pagar: ${precio:,.0f}",
      )
      self.entry_placa.delete(0, "end")
    except ValueError as err:
      messagebox.showerror("Error de Validación", str(err))
      