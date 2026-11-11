from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.servicios_logica import ServiciosLogica
from logica.inventario_logica import InventarioLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class CatalogoServiciosScreen(ctk.CTkFrame):
    """
    Pantalla de Catálogo de servicios y recetas fiel al diseño Figma (Imagen 3 derecha):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Catálogo'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Tarjeta blanca superior 'Registrar servicio' (2 columnas de inputs + fila de botones).
    - Tabla de servicios y sección inferior de Receta con tablas Autowash.Treeview (#BCE3F0)
      y controles en #F68B2E / #F27878.
    """

    def __init__(self, parent, al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_servicios=None, al_ir_empleados=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(parent, fg_color="#E7F9FF", corner_radius=0)
        self.al_volver = al_volver or al_ir_dashboard
        self.al_ir_dashboard = al_ir_dashboard or al_volver
        self.al_ir_clientes = al_ir_clientes
        self.al_ir_vehiculos = al_ir_vehiculos
        self.al_ir_servicios = al_ir_servicios
        self.al_ir_empleados = al_ir_empleados
        self.al_ir_inventario = al_ir_inventario
        self.al_ir_facturacion = al_ir_facturacion
        self.al_ir_reportes = al_ir_reportes
        self.al_ir_catalogo = al_ir_catalogo
        self.al_ir_facturas = al_ir_facturas
        self.al_cerrar_sesion = al_cerrar_sesion

        self.servicio_seleccionado = None
        self.insumos_disponibles = []

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_servicios()
        self._cargar_insumos_en_combo()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Catálogo",
            al_volver=self.al_volver,
            al_ir_dashboard=self.al_ir_dashboard,
            al_ir_clientes=self.al_ir_clientes,
            al_ir_vehiculos=self.al_ir_vehiculos,
            al_ir_servicios=self.al_ir_servicios,
            al_ir_empleados=self.al_ir_empleados,
            al_ir_inventario=self.al_ir_inventario,
            al_ir_facturacion=self.al_ir_facturacion,
            al_ir_reportes=self.al_ir_reportes,
            al_ir_catalogo=self.al_ir_catalogo,
            al_ir_facturas=self.al_ir_facturas,
            al_cerrar_sesion=self.al_cerrar_sesion,
        )

        # ------------------------------------------------------------------ #
        # 2. CONTENEDOR PRINCIPAL DERECHO                                    #
        # ------------------------------------------------------------------ #
        self.main_container = ctk.CTkFrame(self, fg_color="#E7F9FF", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.scroll_body = ctk.CTkScrollableFrame(self.main_container, fg_color="#E7F9FF")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=20)

        # ————— ENCABEZADO Y NAVEGACIÓN —————
        header_nav = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_nav.pack(fill="x", pady=(0, 6))

        btn_volver_dash = ctk.CTkButton(
            header_nav,
            text="← volver al panel principal",
            command=self.al_volver,
            fg_color="transparent",
            hover_color="#D5EFF7",
            text_color="#0B4F66",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            height=28
        )
        btn_volver_dash.pack(side="left")

        ctk.CTkLabel(
            self.scroll_body,
            text="Catálogo de servicios y recetas",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Precios de cada servicio y los insumos que consume",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 16))

        # ————— TARJETA BLANCA SUPERIOR: Registrar servicio —————
        card_servicio = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_servicio.pack(fill="x", pady=(0, 16))

        inner_serv = ctk.CTkFrame(card_servicio, fg_color="transparent")
        inner_serv.pack(fill="both", expand=True, padx=24, pady=18)

        ctk.CTkLabel(
            inner_serv,
            text="Registrar servicio",
            font=("Georgia", 18),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 12))

        # Fila 1: Inputs (2 columnas)
        fila_inputs = ctk.CTkFrame(inner_serv, fg_color="transparent")
        fila_inputs.pack(fill="x", pady=(0, 14))
        fila_inputs.grid_columnconfigure(0, weight=2)
        fila_inputs.grid_columnconfigure(1, weight=1)

        col_nom = ctk.CTkFrame(fila_inputs, fg_color="transparent")
        col_nom.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(
            col_nom,
            text="Nombre del servicio",
            font=("Segoe UI", 11, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.entry_nombre = ctk.CTkEntry(
            col_nom,
            placeholder_text="Nombre del servicio",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=40,
            font=("Segoe UI", 12)
        )
        self.entry_nombre.pack(fill="x")

        col_pre = ctk.CTkFrame(fila_inputs, fg_color="transparent")
        col_pre.grid(row=0, column=1, sticky="ew", padx=(12, 0))

        ctk.CTkLabel(
            col_pre,
            text="Precio",
            font=("Segoe UI", 11, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.entry_precio = ctk.CTkEntry(
            col_pre,
            placeholder_text="Precio",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=40,
            font=("Segoe UI", 12)
        )
        self.entry_precio.pack(fill="x")

        # Fila 2: Botones alineados a la izquierda
        fila_btns = ctk.CTkFrame(inner_serv, fg_color="transparent")
        fila_btns.pack(fill="x")

        ctk.CTkButton(
            fila_btns,
            text="Registrar",
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=12,
            height=36,
            width=120,
            command=self._evento_registrar_servicio,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_btns,
            text="Guardar cambios",
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=12,
            height=36,
            width=145,
            command=self._evento_editar_servicio,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_btns,
            text="Eliminar",
            fg_color="#F27878",
            hover_color="#E05A5A",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=12,
            height=36,
            width=110,
            command=self._evento_eliminar_servicio,
        ).pack(side="left")

        # ————— TABLA DE SERVICIOS —————
        card_tabla_serv = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla_serv.pack(fill="x", pady=(0, 18))

        inner_ts = ctk.CTkFrame(card_tabla_serv, fg_color="transparent")
        inner_ts.pack(fill="both", expand=True, padx=16, pady=14)

        columnas = ("id", "nombre", "precio")
        self.tabla_servicios = ttk.Treeview(
            inner_ts,
            columns=columnas,
            show="headings",
            height=5,
            selectmode="browse",
            style="Autowash.Treeview"
        )
        self.tabla_servicios.heading("id", text="ID")
        self.tabla_servicios.heading("nombre", text="Servicio")
        self.tabla_servicios.heading("precio", text="Precio")
        self.tabla_servicios.column("id", width=70, anchor="center")
        self.tabla_servicios.column("nombre", width=340, anchor="center")
        self.tabla_servicios.column("precio", width=150, anchor="center")
        self.tabla_servicios.pack(fill="x")
        self.tabla_servicios.bind("<<TreeviewSelect>>", self._al_seleccionar_servicio)

        # ————— SECCIÓN DE RECETA DEBAJO —————
        self.label_receta = ctk.CTkLabel(
            self.scroll_body,
            text="Receta: seleccione un servicio",
            font=("Georgia", 16),
            text_color="#3C3B3B",
            anchor="w"
        )
        self.label_receta.pack(fill="x", pady=(0, 8))

        card_receta = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_receta.pack(fill="both", expand=True, pady=(0, 14))

        inner_rec = ctk.CTkFrame(card_receta, fg_color="transparent")
        inner_rec.pack(fill="both", expand=True, padx=16, pady=14)

        columnas_receta = ("insumo_id", "insumo", "cantidad", "unidad")
        self.tabla_receta = ttk.Treeview(
            inner_rec,
            columns=columnas_receta,
            show="headings",
            height=4,
            selectmode="browse",
            style="Autowash.Treeview"
        )
        self.tabla_receta.heading("insumo_id", text="ID")
        self.tabla_receta.heading("insumo", text="Insumo")
        self.tabla_receta.heading("cantidad", text="Cantidad por servicio")
        self.tabla_receta.heading("unidad", text="Unidad")

        self.tabla_receta.column("insumo_id", width=70, anchor="center")
        self.tabla_receta.column("insumo", width=260, anchor="center")
        self.tabla_receta.column("cantidad", width=160, anchor="center")
        self.tabla_receta.column("unidad", width=120, anchor="center")
        self.tabla_receta.pack(fill="both", expand=True)

        # Fila inferior de controles de receta
        fila_receta = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        fila_receta.pack(fill="x", pady=(0, 6))

        self.combo_insumo = ctk.CTkComboBox(
            fila_receta,
            values=["Sin insumos registrados"],
            state="readonly",
            height=38,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            button_color="#FFFFFF",
            button_hover_color="#E7F9FF",
            text_color="#111111",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#111111",
            dropdown_hover_color="#D9F0F9",
            width=260,
            font=("Segoe UI", 11)
        )
        self.combo_insumo.pack(side="left", padx=(0, 10))

        self.entry_cantidad = ctk.CTkEntry(
            fila_receta,
            placeholder_text="Cantidad",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            width=120,
            font=("Segoe UI", 11)
        )
        self.entry_cantidad.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_receta,
            text="Agregar / Actualizar",
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 11, "bold"),
            corner_radius=12,
            height=38,
            width=165,
            command=self._evento_agregar_insumo,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_receta,
            text="Quitar de la receta",
            fg_color="#F27878",
            hover_color="#E05A5A",
            text_color="#000000",
            font=("Segoe UI", 11, "bold"),
            corner_radius=12,
            height=38,
            width=155,
            command=self._evento_quitar_insumo,
        ).pack(side="left")

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
