"""
Pantalla de Catálogo de servicios y recetas (S5-10).

Usa la lógica que ya existe, sin tocar SQL:
    ServiciosLogica.listar_servicios()            -> [{id, nombre, precio, activo}]
    ServiciosLogica.registrar_servicio(nombre, precio)
    ServiciosLogica.editar_servicio(servicio_id, nombre, precio)
    ServiciosLogica.eliminar_servicio(servicio_id)          (lo desactiva)

    InventarioLogica.listar_insumos()             -> [{id, nombre, unidad_medida, ...}]
    InventarioLogica.listar_insumos_de_servicio(servicio_id)
        -> [{servicio_id, insumo_id, cantidad_consumida, nombre_insumo, unidad_medida}]
    InventarioLogica.asignar_insumo_a_servicio(servicio_id, insumo_id, cantidad)
        (si ya existía la receta, la actualiza)
    InventarioLogica.quitar_insumo_de_servicio(servicio_id, insumo_id)
"""

from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.servicios_logica import ServiciosLogica
from logica.inventario_logica import InventarioLogica


class CatalogoServiciosScreen(ctk.CTkFrame):

    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver

        self.servicio_seleccionado = None  # dict del servicio elegido en la tabla
        self.insumos_disponibles = []

        self.pack(fill="both", expand=True, padx=20, pady=20)

        self._crear_interfaz()
        self._cargar_servicios()
        self._cargar_insumos_en_combo()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header, text="Catálogo de Servicios y Recetas",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        if self.al_volver:
            ctk.CTkButton(
                header, text="Volver al Dashboard", fg_color="gray",
                hover_color="#505050", width=140, command=self.al_volver,
            ).pack(side="right")

        # --- Formulario del servicio ---
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)

        self.entry_nombre = ctk.CTkEntry(form, placeholder_text="Nombre del servicio", width=260)
        self.entry_nombre.pack(side="left", padx=(0, 8))

        self.entry_precio = ctk.CTkEntry(form, placeholder_text="Precio", width=110)
        self.entry_precio.pack(side="left", padx=8)

        ctk.CTkButton(
            form, text="Registrar", fg_color="green", width=90,
            command=self._evento_registrar_servicio,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            form, text="Guardar cambios", width=120,
            command=self._evento_editar_servicio,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            form, text="Eliminar", fg_color="darkred", hover_color="#500000", width=80,
            command=self._evento_eliminar_servicio,
        ).pack(side="left", padx=4)

        # --- Tabla de servicios ---
        columnas = ("id", "nombre", "precio")
        self.tabla_servicios = ttk.Treeview(
            self, columns=columnas, show="headings", height=5, selectmode="browse"
        )
        self.tabla_servicios.heading("id", text="ID")
        self.tabla_servicios.heading("nombre", text="Servicio")
        self.tabla_servicios.heading("precio", text="Precio")
        self.tabla_servicios.column("id", width=50, anchor="center")
        self.tabla_servicios.column("nombre", width=320, anchor="w")
        self.tabla_servicios.column("precio", width=120, anchor="e")
        self.tabla_servicios.pack(fill="x", padx=10, pady=8)
        self.tabla_servicios.bind("<<TreeviewSelect>>", self._al_seleccionar_servicio)

        # --- Receta del servicio seleccionado ---
        self.label_receta = ctk.CTkLabel(
            self, text="Receta: seleccione un servicio",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        )
        self.label_receta.pack(fill="x", padx=10, pady=(8, 2))

        columnas_receta = ("insumo_id", "insumo", "cantidad", "unidad")
        self.tabla_receta = ttk.Treeview(
            self, columns=columnas_receta, show="headings", height=4, selectmode="browse"
        )
        self.tabla_receta.heading("insumo_id", text="ID")
        self.tabla_receta.heading("insumo", text="Insumo")
        self.tabla_receta.heading("cantidad", text="Cantidad por servicio")
        self.tabla_receta.heading("unidad", text="Unidad")
        self.tabla_receta.column("insumo_id", width=50, anchor="center")
        self.tabla_receta.column("insumo", width=260, anchor="w")
        self.tabla_receta.column("cantidad", width=150, anchor="center")
        self.tabla_receta.column("unidad", width=100, anchor="center")
        self.tabla_receta.pack(fill="x", padx=10, pady=4)

        fila_receta = ctk.CTkFrame(self, fg_color="transparent")
        fila_receta.pack(fill="x", padx=10, pady=8)

        self.combo_insumo = ctk.CTkComboBox(
            fila_receta, values=["Sin insumos registrados"], state="readonly", width=260
        )
        self.combo_insumo.pack(side="left", padx=(0, 8))

        self.entry_cantidad = ctk.CTkEntry(fila_receta, placeholder_text="Cantidad", width=100)
        self.entry_cantidad.pack(side="left", padx=8)

        ctk.CTkButton(
            fila_receta, text="Agregar / Actualizar", fg_color="green", width=150,
            command=self._evento_agregar_insumo,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            fila_receta, text="Quitar de la receta", fg_color="darkred",
            hover_color="#500000", width=140, command=self._evento_quitar_insumo,
        ).pack(side="left", padx=4)

    # ---------- Carga de datos ----------

    def _cargar_servicios(self, seleccionar_id=None):
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        for servicio in ServiciosLogica.listar_servicios():
            iid = str(servicio["id"])
            self.tabla_servicios.insert(
                "", "end", iid=iid,
                values=(servicio["id"], servicio["nombre"], f"${servicio['precio']:,.0f}"),
            )

        if seleccionar_id is not None and self.tabla_servicios.exists(str(seleccionar_id)):
            self.tabla_servicios.selection_set(str(seleccionar_id))
        else:
            self.servicio_seleccionado = None
            self._cargar_receta()

    def _cargar_insumos_en_combo(self):
        self.insumos_disponibles = InventarioLogica.listar_insumos()

        if not self.insumos_disponibles:
            self.combo_insumo.configure(values=["Sin insumos registrados"])
            self.combo_insumo.set("Sin insumos registrados")
            return

        opciones = [
            f"{i['id']} - {i['nombre']} ({i['unidad_medida']})"
            for i in self.insumos_disponibles
        ]
        self.combo_insumo.configure(values=opciones)
        self.combo_insumo.set(opciones[0])

    def _cargar_receta(self):
        for item in self.tabla_receta.get_children():
            self.tabla_receta.delete(item)

        if self.servicio_seleccionado is None:
            self.label_receta.configure(text="Receta: seleccione un servicio")
            return

        self.label_receta.configure(
            text=f"Receta de: {self.servicio_seleccionado['nombre']}"
        )

        receta = InventarioLogica.listar_insumos_de_servicio(self.servicio_seleccionado["id"])
        if not receta:
            self.tabla_receta.insert(
                "", "end", iid="vacio",
                values=("", "Este servicio todavía no consume insumos", "", ""),
            )
            return

        for ingrediente in receta:
            cantidad = ingrediente["cantidad_consumida"]
            texto_cantidad = f"{cantidad:g}"
            self.tabla_receta.insert(
                "", "end", iid=str(ingrediente["insumo_id"]),
                values=(
                    ingrediente["insumo_id"], ingrediente["nombre_insumo"],
                    texto_cantidad, ingrediente["unidad_medida"],
                ),
            )

    # ---------- Utilidades ----------

    def _servicio_de_la_tabla(self):
        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            return None
        return int(seleccion[0])

    def _obtener_insumo_id(self):
        if not self.insumos_disponibles:
            return None
        return int(self.combo_insumo.get().split(" - ")[0])

    # ---------- Eventos: servicios ----------

    def _al_seleccionar_servicio(self, _evento=None):
        servicio_id = self._servicio_de_la_tabla()
        if servicio_id is None:
            return

        for servicio in ServiciosLogica.listar_servicios():
            if servicio["id"] == servicio_id:
                self.servicio_seleccionado = servicio
                break

        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, self.servicio_seleccionado["nombre"])
        self.entry_precio.delete(0, "end")
        self.entry_precio.insert(0, f"{self.servicio_seleccionado['precio']:g}")
        self._cargar_receta()

    def _evento_registrar_servicio(self):
        try:
            nuevo_id = ServiciosLogica.registrar_servicio(
                self.entry_nombre.get(), self.entry_precio.get()
            )
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        messagebox.showinfo("Éxito", "Servicio registrado. Ahora puede armar su receta.")
        self._cargar_servicios(seleccionar_id=nuevo_id)

    def _evento_editar_servicio(self):
        servicio_id = self._servicio_de_la_tabla()
        if servicio_id is None:
            messagebox.showwarning("Atención", "Seleccione un servicio de la tabla.")
            return

        try:
            ServiciosLogica.editar_servicio(
                servicio_id, self.entry_nombre.get(), self.entry_precio.get()
            )
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
        self._cargar_servicios(seleccionar_id=servicio_id)

    def _evento_eliminar_servicio(self):
        servicio_id = self._servicio_de_la_tabla()
        if servicio_id is None:
            messagebox.showwarning("Atención", "Seleccione un servicio de la tabla.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Desea eliminar el servicio ID {servicio_id}?"):
            return

        try:
            ServiciosLogica.eliminar_servicio(servicio_id)
        except ValueError as err:
            messagebox.showerror("Error", str(err))
            return

        self.entry_nombre.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self._cargar_servicios()

    # ---------- Eventos: receta ----------

    def _evento_agregar_insumo(self):
        if self.servicio_seleccionado is None:
            messagebox.showwarning("Atención", "Seleccione primero un servicio de la tabla.")
            return

        insumo_id = self._obtener_insumo_id()
        if insumo_id is None:
            messagebox.showerror("Error", "No hay insumos registrados. Créelos en Inventario.")
            return

        try:
            cantidad = float(self.entry_cantidad.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error de Validación", "La cantidad debe ser un número.")
            return

        try:
            InventarioLogica.asignar_insumo_a_servicio(
                self.servicio_seleccionado["id"], insumo_id, cantidad
            )
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
            return

        self.entry_cantidad.delete(0, "end")
        self._cargar_receta()

    def _evento_quitar_insumo(self):
        if self.servicio_seleccionado is None:
            messagebox.showwarning("Atención", "Seleccione primero un servicio de la tabla.")
            return

        seleccion = self.tabla_receta.selection()
        if not seleccion or seleccion[0] == "vacio":
            messagebox.showwarning("Atención", "Seleccione un insumo de la receta.")
            return

        InventarioLogica.quitar_insumo_de_servicio(
            self.servicio_seleccionado["id"], int(seleccion[0])
        )
        self._cargar_receta()