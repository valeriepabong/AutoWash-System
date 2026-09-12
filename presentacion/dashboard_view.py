from tkinter import messagebox, ttk
import customtkinter as ctk
from logica.gestion_servicios import ServicioLavado


class DashboardView(ctk.CTkFrame):

  def __init__(self, master, al_cerrar_sesion, al_abrir_clientes):
    super().__init__(master) 
    self.master = master
    self.al_cerrar_sesion = al_cerrar_sesion
    self.al_abrir_clientes = al_abrir_clientes
    self.id_seleccionado = None 
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()
    self._cargar_tabla()

  def _crear_interfaz(self):

    header_frame = ctk.CTkFrame(self, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 10))

    self.label_titulo = ctk.CTkLabel(
        header_frame,
        text="Registro de Lavado de Vehículos",
        font=ctk.CTkFont(size=20, weight="bold"),
    )
    self.label_titulo.pack(side="left")

    self.btn_logout = ctk.CTkButton(
        header_frame,
        text="Cerrar Sesión",
        fg_color="red",
        hover_color="#8B0000",
        width=100,
        command=self.al_cerrar_sesion,
    )
    self.btn_logout.pack(side="right", padx=5)

    self.btn_clientes = ctk.CTkButton(
        header_frame,
        text="Clientes",
        fg_color="#1f538d",
        width=100,
        command=self.al_abrir_clientes,
    )
    self.btn_clientes.pack(side="right", padx=5)

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

    frame_botones = ctk.CTkFrame(self, fg_color="transparent")
    frame_botones.pack(pady=10)

    self.btn_registrar = ctk.CTkButton(
        frame_botones,
        text="Registrar Servicio",
        command=self._evento_registrar,
        fg_color="green",
    )
    self.btn_registrar.pack(side="left", padx=5)

    self.btn_guardar_edicion = ctk.CTkButton(
        frame_botones,
        text="Guardar Cambios",
        command=self._evento_guardar_edicion,
        fg_color="orange",
        state="disabled",
    )
    self.btn_guardar_edicion.pack(side="left", padx=5)

    columnas = ("id", "placa", "vehiculo", "lavado", "precio")
    self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)

    self.tabla.heading("id", text="ID")
    self.tabla.heading("placa", text="Placa")
    self.tabla.heading("vehiculo", text="Vehículo")
    self.tabla.heading("lavado", text="Tipo de Lavado")
    self.tabla.heading("precio", text="Precio ($)")

    self.tabla.column("id", width=40, anchor="center")
    self.tabla.column("placa", width=100, anchor="center")
    self.tabla.column("vehiculo", width=120, anchor="center")
    self.tabla.column("lavado", width=150, anchor="center")
    self.tabla.column("precio", width=100, anchor="center")

    self.tabla.pack(pady=10, fill="both", expand=True, padx=20)

    frame_tabla_acciones = ctk.CTkFrame(self, fg_color="transparent")
    frame_tabla_acciones.pack(pady=5)

    self.btn_cargar_editar = ctk.CTkButton(
        frame_tabla_acciones,
        text="Editar Seleccionado",
        command=self._evento_cargar_para_editar,
        fg_color="#1f538d",
    )
    self.btn_cargar_editar.pack(side="left", padx=10)

    self.btn_eliminar = ctk.CTkButton(
        frame_tabla_acciones,
        text="Eliminar Seleccionado",
        command=self._evento_eliminar,
        fg_color="darkred",
        hover_color="#500000",
    )
    self.btn_eliminar.pack(side="left", padx=10)

  def _cargar_tabla(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    registros = ServicioLavado.obtener_historial()
    for reg in registros:
      self.tabla.insert("", "end", values=reg)

  def _limpiar_formulario(self):
    self.entry_placa.delete(0, "end")
    self.id_seleccionado = None
    self.btn_guardar_edicion.configure(state="disabled")
    self.btn_registrar.configure(state="normal")

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
      self._limpiar_formulario()
      self._cargar_tabla()
    except ValueError as err:
      messagebox.showerror("Error de Validación", str(err))

  def _evento_eliminar(self):
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning(
          "Atención", "Por favor seleccione un registro de la tabla."
      )
      return

    item = self.tabla.item(seleccion[0])
    id_registro = item["values"][0]

    confirmar = messagebox.askyesno(
        "Confirmar Eliminación",
        f"¿Está seguro de eliminar el registro ID {id_registro}?",
    )
    if confirmar:
      try:
        ServicioLavado.eliminar_servicio(id_registro)
        messagebox.showinfo(
            "Éxito", "El registro ha sido eliminado correctamente."
        )
        self._cargar_tabla()
        self._limpiar_formulario()
      except ValueError as err:
        messagebox.showerror("Error", str(err))

  def _evento_cargar_para_editar(self):
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning(
          "Atención", "Por favor seleccione un registro de la tabla para editar."
      )
      return

    item = self.tabla.item(seleccion[0])
    valores = item["values"]

    self.id_seleccionado = valores[0]
    self.entry_placa.delete(0, "end")
    self.entry_placa.insert(0, valores[1])
    self.combo_vehiculo.set(valores[2])
    self.combo_lavado.set(valores[3])

    # Habilitar botón de guardar cambios
    self.btn_guardar_edicion.configure(state="normal")
    self.btn_registrar.configure(state="disabled")

  def _evento_guardar_edicion(self):
    if not self.id_seleccionado:
      return

    placa = self.entry_placa.get()
    vehiculo = self.combo_vehiculo.get()
    lavado = self.combo_lavado.get()

    try:
      precio = ServicioLavado.actualizar_servicio(
          self.id_seleccionado, placa, vehiculo, lavado
      )
      messagebox.showinfo(
          "Actualización Exitosa",
          f"Servicio actualizado correctamente.\nNuevo Total: ${precio:,.0f}",
      )
      self._limpiar_formulario()
      self._cargar_tabla()
    except ValueError as err:
      messagebox.showerror("Error de Validación", str(err))