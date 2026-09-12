from tkinter import messagebox, ttk
import customtkinter as ctk
from logica.gestion_servicios import ServicioLavado


class DashboardView(ctk.CTkFrame):

  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()
    self._cargar_tabla()  

  def _crear_interfaz(self):
    
    self.label_titulo = ctk.CTkLabel(
        self,
        text="Registro de Lavado de Vehículos",
        font=ctk.CTkFont(size=20, weight="bold"),
    )
    self.label_titulo.pack(pady=10)

    # Entradas de datos
    self.entry_placa = ctk.CTkEntry(
        self, placeholder_text="Ingrese la placa (Ej: ABC123)"
    )
    self.entry_placa.pack(pady=5, fill="x", padx=40)

    self.combo_vehiculo = ctk.CTkOptionMenu(
        self, values=["Automóvil", "Camioneta", "Moto"]
    )
    self.combo_vehiculo.pack(pady=5)

    self.combo_lavado = ctk.CTkOptionMenu(
        self, values=["Sencillo", "General", "Especial (Polichado)"]
    )
    self.combo_lavado.pack(pady=5)

    self.btn_registrar = ctk.CTkButton(
        self,
        text="Registrar Servicio",
        command=self._evento_registrar,
        fg_color="green",
    )
    self.btn_registrar.pack(pady=10)

    columnas = ("id", "placa", "vehiculo", "lavado", "precio")
    self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)

    self.tabla.heading("id", text="ID")
    self.tabla.heading("placa", text="Placa")
    self.tabla.heading("vehiculo", text="Vehículo")
    self.tabla.heading("lavado", text="Tipo de Lavado")
    self.tabla.heading("precio", text="Precio ($)")

    # Anchos de columnas
    self.tabla.column("id", width=40, anchor="center")
    self.tabla.column("placa", width=100, anchor="center")
    self.tabla.column("vehiculo", width=120, anchor="center")
    self.tabla.column("lavado", width=150, anchor="center")
    self.tabla.column("precio", width=100, anchor="center")

    self.tabla.pack(pady=15, fill="both", expand=True, padx=20)

  def _cargar_tabla(self):
    """Llama a la capa de Lógica para obtener el historial y refrescar la tabla."""
    for item in self.tabla.get_children():
      self.tabla.delete(item)


    registros = ServicioLavado.obtener_historial()
    for reg in registros:
      self.tabla.insert("", "end", values=reg)

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

      # Refrescar la tabla automáticamente al registrar
      self._cargar_tabla()

    except ValueError as err:
      messagebox.showerror("Error de Validación", str(err))
      