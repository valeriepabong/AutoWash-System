import customtkinter as ctk
from tkinter import ttk, messagebox
from logica.empleados_logica import EmpleadosLogica

class EmpleadosScreen(ctk.CTkFrame):
    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        titulo = ctk.CTkLabel(header_frame, text="Gestión de Empleados", font=("Roboto", 24, "bold"))
        titulo.pack(side="left")

        if self.al_volver:
            btn_volver = ctk.CTkButton(header_frame, text="Volver al Dashboard", command=self.al_volver, fg_color="#555555", hover_color="#333333")
            btn_volver.pack(side="right")

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10, padx=10)

        self.txt_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre completo del empleado", width=300)
        self.txt_nombre.pack(pady=10)

        btn_registrar = ctk.CTkButton(form_frame, text="Registrar Empleado", command=self._registrar, fg_color="#1f538d")
        btn_registrar.pack(pady=5)

        self.tabla = ttk.Treeview(self, columns=("ID", "Nombre"), show="headings", height=8)
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre")

        self.tabla.column("ID", width=60, anchor="center")
        self.tabla.column("Nombre", width=300, anchor="w")

        self.tabla.pack(fill="both", expand=True, pady=10)

        self._cargar_empleados()

    def _cargar_empleados(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            empleados = EmpleadosLogica.listar_empleados()
            for emp in empleados:
                self.tabla.insert("", "end", values=(emp.get("id"), emp.get("nombre")))
        except Exception as e:
            print(f"Error al cargar empleados: {e}")

    def _registrar(self):
        nombre = self.txt_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del empleado es obligatorio.")
            return

        exito, msg = EmpleadosLogica.crear_empleado(nombre)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.txt_nombre.delete(0, "end")
            self._cargar_empleados()
        else:
            messagebox.showerror("Error", msg)