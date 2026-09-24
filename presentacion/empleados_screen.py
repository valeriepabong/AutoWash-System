from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.empleados_logica import EmpleadosLogica


class EmpleadosScreen(ctk.CTkFrame):

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
            text="Gestión de Empleados",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="Volver al Dashboard",
            fg_color="gray",
            hover_color="#505050",
            width=140,
            command=self.al_volver,
        ).pack(side="right")

        self.entry_nombre = ctk.CTkEntry(
            self, placeholder_text="Nombre completo del empleado"
        )
        self.entry_nombre.pack(pady=5, fill="x", padx=40)

        ctk.CTkButton(
            self,
            text="Registrar Empleado",
            command=self._evento_registrar,
            fg_color="green",
        ).pack(pady=10)

        columnas = ("id", "nombre")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")

        self.tabla.column("id", width=40, anchor="center")
        self.tabla.column("nombre", width=300, anchor="center")

        self.tabla.pack(pady=10, fill="both", expand=True, padx=20)

        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(pady=5)

        ctk.CTkButton(
            botones_frame,
            text="Editar Seleccionado",
            command=self._evento_editar,
            fg_color="#1f538d",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botones_frame,
            text="Eliminar Seleccionado",
            command=self._evento_eliminar,
            fg_color="darkred",
            hover_color="#500000",
        ).pack(side="left", padx=5)

    def _cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for empleado in EmpleadosLogica.listar_empleados():
            self.tabla.insert(
                "", "end", values=(empleado["id"], empleado["nombre"])
            )

    def _evento_registrar(self):
        nombre = self.entry_nombre.get()

        try:
            EmpleadosLogica.registrar_empleado(nombre)
            messagebox.showinfo("Éxito", "Empleado registrado correctamente.")
            self.entry_nombre.delete(0, "end")
            self._cargar_tabla()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Por favor seleccione un empleado de la tabla."
            )
            return

        id_empleado, nombre_actual = self.tabla.item(seleccion[0])["values"]

        dialogo = ctk.CTkInputDialog(
            text=f"Nuevo nombre para '{nombre_actual}':",
            title="Editar Empleado",
        )
        nuevo_nombre = dialogo.get_input()

        # Si cerró la ventana sin escribir nada, no se hace nada
        if nuevo_nombre is None:
            return

        try:
            EmpleadosLogica.editar_empleado(id_empleado, nuevo_nombre)
            messagebox.showinfo("Éxito", "Empleado actualizado correctamente.")
            self._cargar_tabla()
        except ValueError as err:
            messagebox.showerror("Error", str(err))

    def _evento_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Por favor seleccione un empleado de la tabla."
            )
            return

        id_empleado = self.tabla.item(seleccion[0])["values"][0]

        if messagebox.askyesno(
            "Confirmar", f"¿Desea eliminar al empleado ID {id_empleado}?"
        ):
            try:
                EmpleadosLogica.eliminar_empleado(id_empleado)
                messagebox.showinfo(
                    "Éxito", "El empleado ha sido eliminado correctamente."
                )
                self._cargar_tabla()
            except ValueError as err:
                messagebox.showerror("Error", str(err))