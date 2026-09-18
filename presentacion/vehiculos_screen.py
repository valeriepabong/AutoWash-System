import customtkinter as ctk
from tkinter import messagebox

from logica.vehiculos_logica import VehiculosLogica
from logica.clientes_logica import ClientesLogica


class VehiculosScreen(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.clientes_disponibles = []  # guarda los dicts de clientes cargados

        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.crear_interfaz()
        self.cargar_clientes_en_combo()
        self.mostrar_vehiculos()

    def crear_interfaz(self):

        titulo = ctk.CTkLabel(
            self,
            text="Gestión de Vehículos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=15)

        # Cliente asociado (desplegable)
        self.combo_cliente = ctk.CTkOptionMenu(self, values=["Sin clientes registrados"])
        self.combo_cliente.pack(pady=8, fill="x", padx=40)

        # Marca
        self.entry_marca = ctk.CTkEntry(self, placeholder_text="Marca del vehículo (opcional)")
        self.entry_marca.pack(pady=5, fill="x", padx=40)

        # Modelo
        self.entry_modelo = ctk.CTkEntry(self, placeholder_text="Modelo del vehículo (opcional)")
        self.entry_modelo.pack(pady=5, fill="x", padx=40)

        # Placa
        self.entry_placa = ctk.CTkEntry(self, placeholder_text="Placa del vehículo")
        self.entry_placa.pack(pady=5, fill="x", padx=40)

        # Tipo de vehículo
        self.combo_tipo = ctk.CTkOptionMenu(
            self, values=["Automóvil", "Camioneta", "Moto"]
        )
        self.combo_tipo.pack(pady=8)

        # Botón registrar
        boton_registrar = ctk.CTkButton(
            self, text="Registrar vehículo", command=self.registrar_vehiculo
        )
        boton_registrar.pack(pady=10)

        # Área para mostrar vehículos
        self.lista = ctk.CTkTextbox(self, width=500, height=200)
        self.lista.pack(pady=10, padx=40, fill="both", expand=True)

    def cargar_clientes_en_combo(self):
        self.clientes_disponibles = ClientesLogica.listar_todos_los_clientes()

        if not self.clientes_disponibles:
            self.combo_cliente.configure(values=["Sin clientes registrados"])
            self.combo_cliente.set("Sin clientes registrados")
            return

        opciones = [
            f"{c['id']} - {c['nombre']}" for c in self.clientes_disponibles
        ]
        self.combo_cliente.configure(values=opciones)
        self.combo_cliente.set(opciones[0])

    def obtener_cliente_id_seleccionado(self):
        seleccion = self.combo_cliente.get()
        if not self.clientes_disponibles or seleccion == "Sin clientes registrados":
            return None
        # La opción tiene formato "3 - Juan Pérez", tomamos el id antes del " - "
        id_texto = seleccion.split(" - ")[0]
        return int(id_texto)

    def registrar_vehiculo(self):

        cliente_id = self.obtener_cliente_id_seleccionado()
        marca = self.entry_marca.get()
        modelo = self.entry_modelo.get()
        placa = self.entry_placa.get()
        tipo = self.combo_tipo.get()

        if cliente_id is None:
            messagebox.showerror(
                "Error",
                "Debe registrar al menos un cliente antes de asociar un vehículo."
            )
            return

        try:
            VehiculosLogica.registrar_vehiculo(
                placa=placa,
                tipo_vehiculo=tipo,
                cliente_id=cliente_id,
                marca=marca,
                modelo=modelo,
            )

            messagebox.showinfo(
                "Registro exitoso", "El vehículo fue registrado correctamente."
            )

            self.limpiar_campos()
            self.mostrar_vehiculos()

        except ValueError as error:
            messagebox.showerror(
                "Error", f"No se pudo registrar el vehículo.\n\n{error}"
            )

    def mostrar_vehiculos(self):

        self.lista.delete("1.0", "end")

        vehiculos = VehiculosLogica.obtener_vehiculos()

        if not vehiculos:
            self.lista.insert("end", "No hay vehículos registrados.")
            return

        for vehiculo in vehiculos:
            texto = (
                f"ID: {vehiculo['id']}\n"
                f"Placa: {vehiculo['placa']}\n"
                f"Tipo: {vehiculo['tipo_vehiculo']}\n"
                f"Marca: {vehiculo['marca'] or '-'}\n"
                f"Modelo: {vehiculo['modelo'] or '-'}\n"
                f"Cliente: {vehiculo['nombre_cliente']}\n"
                f"{'-' * 40}\n"
            )
            self.lista.insert("end", texto)

    def limpiar_campos(self):
        self.entry_marca.delete(0, "end")
        self.entry_modelo.delete(0, "end")
        self.entry_placa.delete(0, "end")