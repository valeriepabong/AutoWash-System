from tkinter import messagebox, ttk
import customtkinter as ctk
from logica.clientes_logica import ClienteServicio


class ClientesScreen(ctk.CTkFrame):

  def __init__(self, master, al_volver):
    super().__init__(master)
    self.master = master
    self.al_volver = al_volver
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()
    self._cargar_tabla()

  def _crear_interfaz(self):
  
    header_frame = ctk.CTkFrame(self, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        header_frame,
        text="Gestión de Clientes Frecuentes",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(side="left")

    btn_volver = ctk.CTkButton(
        header_frame,
        text="Volver al Dashboard",
        fg_color="gray",
        hover_color="#505050",
        width=140,
        command=self.al_volver,
    )
    btn_volver.pack(side="right")

    self.entry_nombre = ctk.CTkEntry(
        self, placeholder_text="Nombre completo del cliente"
    )
    self.entry_nombre.pack(pady=5, fill="x", padx=40)

    self.entry_telefono = ctk.CTkEntry(
        self, placeholder_text="Teléfono / WhatsApp"
    )
    self.entry_telefono.pack(pady=5, fill="x", padx=40)

    self.entry_placa = ctk.CTkEntry(
        self, placeholder_text="Placa del vehículo asociado (Ej: ABC123)"
    )
    self.entry_placa.pack(pady=5, fill="x", padx=40)

    btn_registrar = ctk.CTkButton(
        self,
        text="Registrar Cliente",
        command=self._evento_registrar,
        fg_color="green",
    )
    btn_registrar.pack(pady=10)

    columnas = ("id", "nombre", "telefono", "placa")
    self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)

    self.tabla.heading("id", text="ID")
    self.tabla.heading("nombre", text="Nombre")
    self.tabla.heading("telefono", text="Teléfono")
    self.tabla.heading("placa", text="Placa Vehículo")

    self.tabla.column("id", width=40, anchor="center")
    self.tabla.column("nombre", width=180, anchor="center")
    self.tabla.column("telefono", width=120, anchor="center")
    self.tabla.column("placa", width=100, anchor="center")

    self.tabla.pack(pady=10, fill="both", expand=True, padx=20)

  
    btn_eliminar = ctk.CTkButton(
        self,
        text="Eliminar Cliente Seleccionado",
        command=self._evento_eliminar,
        fg_color="darkred",
        hover_color="#500000",
    )
    btn_eliminar.pack(pady=5)

  def _cargar_tabla(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    registros = ClienteServicio.obtener_clientes()
    for reg in registros:
      self.tabla.insert("", "end", values=reg)

  def _limpiar_formulario(self):
    self.entry_nombre.delete(0, "end")
    self.entry_telefono.delete(0, "end")
    self.entry_placa.delete(0, "end")

  def _evento_registrar(self):
    nombre = self.entry_nombre.get()
    telefono = self.entry_telefono.get()
    placa = self.entry_placa.get()

    try:
      ClienteServicio.registrar_cliente(nombre, telefono, placa)
      messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
      self._limpiar_formulario()
      self._cargar_tabla()
    except ValueError as err:
      messagebox.showerror("Error de Validación", str(err))

  def _evento_eliminar(self):
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning(
          "Atención", "Por favor seleccione un cliente de la tabla."
      )
      return

    item = self.tabla.item(seleccion[0])
    id_cliente = item["values"][0]

    confirmar = messagebox.askyesno(
        "Confirmar", f"¿Desea eliminar al cliente ID {id_cliente}?"
    )
    if confirmar:
      try:
        ClienteServicio.eliminar_cliente(id_cliente)
        messagebox.showinfo(
            "Éxito", "El cliente ha sido eliminado correctamente."
        )
        self._cargar_tabla()
      except ValueError as err:
        messagebox.showerror("Error", str(err))