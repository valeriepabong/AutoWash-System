import customtkinter as ctk
from tkinter import messagebox

from logica.vehiculos_logica import VehiculoLogica


class VehiculosScreen(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.crear_interfaz()
        self.mostrar_vehiculos()


    def crear_interfaz(self):

        titulo = ctk.CTkLabel(
            self,
            text="Gestión de Vehículos",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        titulo.pack(pady=15)


        # Marca
        self.entry_marca = ctk.CTkEntry(
            self,
            placeholder_text="Marca del vehículo"
        )

        self.entry_marca.pack(
            pady=5,
            fill="x",
            padx=40
        )


        # Modelo
        self.entry_modelo = ctk.CTkEntry(
            self,
            placeholder_text="Modelo del vehículo"
        )

        self.entry_modelo.pack(
            pady=5,
            fill="x",
            padx=40
        )


        # Placa
        self.entry_placa = ctk.CTkEntry(
            self,
            placeholder_text="Placa del vehículo"
        )

        self.entry_placa.pack(
            pady=5,
            fill="x",
            padx=40
        )


        # Tipo de vehículo
        self.combo_tipo = ctk.CTkOptionMenu(
            self,
            values=[
                "Automóvil",
                "Camioneta",
                "Moto"
            ]
        )

        self.combo_tipo.pack(pady=8)


        # Botón registrar
        boton_registrar = ctk.CTkButton(
            self,
            text="Registrar vehículo",
            command=self.registrar_vehiculo
        )

        boton_registrar.pack(pady=10)


        # Área para mostrar vehículos
        self.lista = ctk.CTkTextbox(
            self,
            width=500,
            height=200
        )

        self.lista.pack(
            pady=10,
            padx=40,
            fill="both",
            expand=True
        )


    def registrar_vehiculo(self):

        marca = self.entry_marca.get()
        modelo = self.entry_modelo.get()
        placa = self.entry_placa.get()
        tipo = self.combo_tipo.get()

        try:

            VehiculoLogica.registrar_vehiculo(
                marca,
                modelo,
                placa,
                tipo
            )

            messagebox.showinfo(
                "Registro exitoso",
                "El vehículo fue registrado correctamente."
            )

            self.limpiar_campos()
            self.mostrar_vehiculos()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No se pudo registrar el vehículo.\n\n{error}"
            )


    def mostrar_vehiculos(self):

        self.lista.delete(
            "1.0",
            "end"
        )

        vehiculos = VehiculoLogica.obtener_vehiculos()

        if not vehiculos:

            self.lista.insert(
                "end",
                "No hay vehículos registrados."
            )

            return


        for vehiculo in vehiculos:

            id_vehiculo = vehiculo[0]
            marca = vehiculo[1]
            modelo = vehiculo[2]
            placa = vehiculo[3]
            tipo = vehiculo[4]

            texto = (
                f"ID: {id_vehiculo}\n"
                f"Marca: {marca}\n"
                f"Modelo: {modelo}\n"
                f"Placa: {placa}\n"
                f"Tipo: {tipo}\n"
                f"{'-' * 40}\n"
            )

            self.lista.insert(
                "end",
                texto
            )


    def limpiar_campos(self):

        self.entry_marca.delete(
            0,
            "end"
        )

        self.entry_modelo.delete(
            0,
            "end"
        )

        self.entry_placa.delete(
            0,
            "end"
        )
