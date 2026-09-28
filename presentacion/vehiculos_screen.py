import customtkinter as ctk
from tkinter import ttk, messagebox
from logica.vehiculos_logica import VehiculosLogica
from logica.clientes_logica import ClientesLogica

class VehiculosScreen(ctk.CTkFrame):
    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        titulo = ctk.CTkLabel(header_frame, text="Gestión de Vehículos", font=("Roboto", 24, "bold"))
        titulo.pack(side="left")

        if self.al_volver:
            btn_volver = ctk.CTkButton(header_frame, text="Volver al Dashboard", command=self.al_volver, fg_color="#555555", hover_color="#333333")
            btn_volver.pack(side="right")

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10, padx=10)

        self.cb_clientes = ctk.CTkComboBox(form_frame, width=300)
        self.cb_clientes.pack(pady=5)

        self.txt_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca del vehículo (opcional)", width=300)
        self.txt_marca.pack(pady=5)

        self.txt_modelo = ctk.CTkEntry(form_frame, placeholder_text="Modelo del vehículo (opcional)", width=300)
        self.txt_modelo.pack(pady=5)

        self.txt_placa = ctk.CTkEntry(form_frame, placeholder_text="Placa del vehículo", width=300)
        self.txt_placa.pack(pady=5)

        self.cb_tipo = ctk.CTkComboBox(form_frame, values=["Automóvil", "Motocicleta", "Camioneta", "Camión"])
        self.cb_tipo.pack(pady=5)

        btn_registrar = ctk.CTkButton(form_frame, text="Registrar vehículo", command=self._registrar)
        btn_registrar.pack(pady=10)

        self.tabla = ttk.Treeview(self, columns=("ID", "Placa", "Marca", "Modelo", "Tipo", "Cliente"), show="headings", height=8)
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Placa", text="Placa")
        self.tabla.heading("Marca", text="Marca")
        self.tabla.heading("Modelo", text="Modelo")
        self.tabla.heading("Tipo", text="Tipo")
        self.tabla.heading("Cliente", text="Cliente")

        self.tabla.column("ID", width=40, anchor="center")
        self.tabla.column("Placa", width=100, anchor="center")
        self.tabla.column("Marca", width=120, anchor="center")
        self.tabla.column("Modelo", width=120, anchor="center")
        self.tabla.column("Tipo", width=100, anchor="center")
        self.tabla.column("Cliente", width=180, anchor="center")

        self.tabla.pack(fill="both", expand=True, pady=10)

        self._cargar_clientes()
        self._cargar_vehiculos()

    def _cargar_clientes(self):
        try:
            clientes = ClientesLogica.obtener_vehiculos()
            if clientes:
                opciones = [f"{c['id']} - {c['nombre']}" for c in clientes]
                self.cb_clientes.configure(values=opciones)
                self.cb_clientes.set(opciones[0])
            else:
                self.cb_clientes.configure(values=["Sin clientes registrados"])
                self.cb_clientes.set("Sin clientes registrados")
        except Exception:
            self.cb_clientes.configure(values=["Sin clientes registrados"])

    def _cargar_vehiculos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            vehiculos = VehiculosLogica.obtener_vehiculos()
            for v in vehiculos:
                self.tabla.insert("", "end", values=(v.get("id"), v.get("placa"), v.get("marca", ""), v.get("modelo", ""), v.get("tipo_vehiculo"), v.get("cliente_nombre", "")))
        except Exception as e:
            print(f"Error al cargar vehículos: {e}")

    def _registrar(self):
        cliente_sel = self.cb_clientes.get()
        if not cliente_sel or cliente_sel == "Sin clientes registrados":
            messagebox.showwarning("Advertencia", "Debe seleccionar un cliente válido.")
            return

        placa = self.txt_placa.get().strip()
        if not placa:
            messagebox.showwarning("Advertencia", "La placa es obligatoria.")
            return

        cliente_id = int(cliente_sel.split(" - ")[0])
        marca = self.txt_marca.get().strip()
        modelo = self.txt_modelo.get().strip()
        tipo = self.cb_tipo.get()

        exito, msg = VehiculosLogica.crear_vehiculo(placa, marca, modelo, tipo, cliente_id)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.txt_placa.delete(0, "end")
            self.txt_marca.delete(0, "end")
            self.txt_modelo.delete(0, "end")
            self._cargar_vehiculos()
        else:
            messagebox.showerror("Error", msg)