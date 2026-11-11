from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.inventario_logica import InventarioLogica
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class InventarioScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión de Inventario fiel al diseño Figma (Imagen 3 izquierda):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Inventario'.
    - Área principal #E7F9FF con enlace '← volver al panel principal' y alerta a la derecha.
    - Dos tarjetas blancas lado a lado: 'Registrar insumo nuevo' (#F68B2E) y 'Registrar entrada de stock' (#0B4F66).
    - Tabla inferior de insumos con las 5 columnas (ID, Insumo, Stock actual, Stock minimo, Unidad)
      y resaltado en #FAD7A0 + ' (Stock bajo)' para existencias bajas.
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

        self._insumo_seleccionado_id = None
        self._insumos_cache = {}

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self.cargar_datos()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Inventario",
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

        self.lbl_alerta = ctk.CTkLabel(
            header_nav,
            text="",
            font=("Segoe UI", 12, "bold"),
            text_color="#D9534F",
            anchor="e"
        )
        self.lbl_alerta.pack(side="right")

        ctk.CTkLabel(
            self.scroll_body,
            text="Gestión de inventario",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Insumos, stock actual y stock minimo",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 18))

        # ————— CONTENEDOR SUPERIOR CON 2 TARJETAS LADO A LADO —————
        top_cards = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        top_cards.pack(fill="x", pady=(0, 20))
        top_cards.grid_columnconfigure(0, weight=1, uniform="cards")
        top_cards.grid_columnconfigure(1, weight=1, uniform="cards")

        # ————— TARJETA IZQUIERDA: Registrar insumo nuevo —————
        card_crud = ctk.CTkFrame(
            top_cards,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_crud.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        inner_crud = ctk.CTkFrame(card_crud, fg_color="transparent")
        inner_crud.pack(fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            inner_crud,
            text="Registrar insumo nuevo",
            font=("Georgia", 18),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        grid_crud = ctk.CTkFrame(inner_crud, fg_color="transparent")
        grid_crud.pack(fill="x")
        grid_crud.grid_columnconfigure(0, weight=1, uniform="crud_cols")
        grid_crud.grid_columnconfigure(1, weight=1, uniform="crud_cols")

        # Fila 1, Col 0: Nombre
        f1_c0 = ctk.CTkFrame(grid_crud, fg_color="transparent")
        f1_c0.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))
        ctk.CTkLabel(f1_c0, text="Nombre", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.entry_nombre = ctk.CTkEntry(
            f1_c0,
            placeholder_text="Nombre del insumo",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            font=("Segoe UI", 11)
        )
        self.entry_nombre.pack(fill="x")

        # Fila 1, Col 1: Unidad de medida
        f1_c1 = ctk.CTkFrame(grid_crud, fg_color="transparent")
        f1_c1.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))
        ctk.CTkLabel(f1_c1, text="Unidad de medida", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        unidades = ["litros", "unidades", "ml", "galones", "gramos", "paquetes"]
        self.combo_unidad = ctk.CTkComboBox(
            f1_c1,
            values=unidades,
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
            font=("Segoe UI", 11)
        )
        self.combo_unidad.set("litros")
        self.combo_unidad.pack(fill="x")

        # Fila 2, Col 0: Stock inicial
        f2_c0 = ctk.CTkFrame(grid_crud, fg_color="transparent")
        f2_c0.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 14))
        ctk.CTkLabel(f2_c0, text="Stock inicial", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.entry_stock_inicial = ctk.CTkEntry(
            f2_c0,
            placeholder_text="0",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            font=("Segoe UI", 11)
        )
        self.entry_stock_inicial.pack(fill="x")

        # Fila 2, Col 1: Stock minimo
        f2_c1 = ctk.CTkFrame(grid_crud, fg_color="transparent")
        f2_c1.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 14))
        ctk.CTkLabel(f2_c1, text="Stock minimo", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.entry_stock_minimo = ctk.CTkEntry(
            f2_c1,
            placeholder_text="0",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            font=("Segoe UI", 11)
        )
        self.entry_stock_minimo.pack(fill="x")

        # Botón Crear insumo centrado
        self.btn_crear = ctk.CTkButton(
            inner_crud,
            text="Crear insumo",
            command=self._evento_crear_insumo,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=14,
            height=38,
            width=170,
        )
        self.btn_crear.pack(pady=(2, 0))

        # ————— TARJETA DERECHA: Registrar entrada de stock —————
        card_entrada = ctk.CTkFrame(
            top_cards,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_entrada.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        inner_entrada = ctk.CTkFrame(card_entrada, fg_color="transparent")
        inner_entrada.pack(fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            inner_entrada,
            text="Registrar entrada de stock",
            font=("Georgia", 18),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        # Fila 1 (2 columnas): Insumo | Cantidad
        fila1_ent = ctk.CTkFrame(inner_entrada, fg_color="transparent")
        fila1_ent.pack(fill="x", pady=(0, 10))
        fila1_ent.grid_columnconfigure(0, weight=2)
        fila1_ent.grid_columnconfigure(1, weight=1)

        ent_c0 = ctk.CTkFrame(fila1_ent, fg_color="transparent")
        ent_c0.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(ent_c0, text="Insumo", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.combo_insumo_entrada = ctk.CTkComboBox(
            ent_c0,
            values=["Sin insumos registrados"],
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
            font=("Segoe UI", 11)
        )
        self.combo_insumo_entrada.pack(fill="x")

        ent_c1 = ctk.CTkFrame(fila1_ent, fg_color="transparent")
        ent_c1.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(ent_c1, text="Cantidad", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.entry_cantidad_entrada = ctk.CTkEntry(
            ent_c1,
            placeholder_text="0",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            font=("Segoe UI", 11)
        )
        self.entry_cantidad_entrada.pack(fill="x")

        # Fila 2 (ancho completo): Motivo
        ctk.CTkLabel(inner_entrada, text="Motivo", anchor="w", font=("Segoe UI", 11, "bold"), text_color="#111111").pack(fill="x", pady=(0, 3))
        self.entry_motivo_entrada = ctk.CTkEntry(
            inner_entrada,
            placeholder_text="Motivo de la entrada",
            placeholder_text_color="#666666",
            text_color="#111111",
            fg_color="#FFFFFF",
            border_color="#000000",
            border_width=1,
            corner_radius=14,
            height=38,
            font=("Segoe UI", 11)
        )
        self.entry_motivo_entrada.pack(fill="x", pady=(0, 14))

        # Botón Agregar stock centrado
        self.btn_entrada = ctk.CTkButton(
            inner_entrada,
            text="Agregar stock",
            command=self._evento_registrar_entrada,
            fg_color="#0B4F66",
            hover_color="#336E84",
            text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            corner_radius=14,
            height=38,
            width=170,
        )
        self.btn_entrada.pack(pady=(2, 0))

        # ————— TABLA INFERIOR DE INSUMOS (5 columnas de Figma) —————
        card_tabla_insumos = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla_insumos.pack(fill="x", pady=(0, 18))

        inner_ti = ctk.CTkFrame(card_tabla_insumos, fg_color="transparent")
        inner_ti.pack(fill="both", expand=True, padx=18, pady=16)

        head_ti = ctk.CTkFrame(inner_ti, fg_color="transparent")
        head_ti.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            head_ti,
            text="Insumos en inventario",
            font=("Georgia", 16),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(side="left")

        # Botones discretos para editar/eliminar insumo seleccionado
        acciones_ti = ctk.CTkFrame(head_ti, fg_color="transparent")
        acciones_ti.pack(side="right")

        self.btn_actualizar = ctk.CTkButton(
            acciones_ti,
            text="Actualizar seleccionado",
            command=self._evento_actualizar_insumo,
            fg_color="#3F8FA9",
            hover_color="#336E84",
            text_color="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            corner_radius=10,
            height=28,
            width=140
        )
        self.btn_actualizar.pack(side="left", padx=(0, 6))

        self.btn_eliminar = ctk.CTkButton(
            acciones_ti,
            text="Eliminar",
            command=self._evento_eliminar_insumo,
            fg_color="#F0524F",
            hover_color="#D03D3A",
            text_color="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            corner_radius=10,
            height=28,
            width=75
        )
        self.btn_eliminar.pack(side="left")

        columnas_insumos = ("id", "nombre", "stock_actual", "stock_minimo", "unidad")
        self.tree_insumos = ttk.Treeview(
            inner_ti,
            columns=columnas_insumos,
            show="headings",
            height=7,
            style="Autowash.Treeview"
        )
        self.tree_insumos.heading("id", text="ID")
        self.tree_insumos.heading("nombre", text="Insumo")
        self.tree_insumos.heading("stock_actual", text="Stock actual")
        self.tree_insumos.heading("stock_minimo", text="Stock minimo")
        self.tree_insumos.heading("unidad", text="Unidad")

        self.tree_insumos.column("id", width=60, anchor="center")
        self.tree_insumos.column("nombre", width=240, anchor="center")
        self.tree_insumos.column("stock_actual", width=180, anchor="center")
        self.tree_insumos.column("stock_minimo", width=120, anchor="center")
        self.tree_insumos.column("unidad", width=110, anchor="center")

        self.tree_insumos.tag_configure("bajo", background="#FAD7A0")
        self.tree_insumos.pack(fill="x")
        self.tree_insumos.bind("<<TreeviewSelect>>", self._al_seleccionar_insumo_tabla)

        # ————— MOVIMIENTOS (al final del scroll para mantener compatibilidad total) —————
        card_tabla_mov = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla_mov.pack(fill="both", expand=True)

        inner_tm = ctk.CTkFrame(card_tabla_mov, fg_color="transparent")
        inner_tm.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(
            inner_tm,
            text="Historial de movimientos",
            font=("Georgia", 15),
            text_color="#3C3B3B",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        columnas_mov = ("id", "fecha", "insumo", "tipo", "cantidad", "motivo")
        self.tree_movimientos = ttk.Treeview(
            inner_tm,
            columns=columnas_mov,
            show="headings",
            height=5,
            style="Autowash.Treeview"
        )
        self.tree_movimientos.heading("id", text="ID")
        self.tree_movimientos.heading("fecha", text="Fecha / Hora")
        self.tree_movimientos.heading("insumo", text="Insumo")
        self.tree_movimientos.heading("tipo", text="Tipo")
        self.tree_movimientos.heading("cantidad", text="Cantidad")
        self.tree_movimientos.heading("motivo", text="Motivo / Detalle")

        self.tree_movimientos.column("id", width=50, anchor="center")
        self.tree_movimientos.column("fecha", width=140, anchor="center")
        self.tree_movimientos.column("insumo", width=190, anchor="center")
        self.tree_movimientos.column("tipo", width=90, anchor="center")
        self.tree_movimientos.column("cantidad", width=110, anchor="center")
        self.tree_movimientos.column("motivo", width=220, anchor="center")

        self.tree_movimientos.pack(fill="both", expand=True)

    # ========================================================================
    # CARGA Y REFRESCO DE DATOS
    # ========================================================================

    def cargar_datos(self):
        """Carga insumos, alertas y movimientos desde InventarioLogica."""
        self._cargar_tabla_insumos()
        self._cargar_tabla_movimientos()

    def _cargar_tabla_insumos(self):
        for item in self.tree_insumos.get_children():
            self.tree_insumos.delete(item)

        self._insumos_cache.clear()
        try:
            insumos = InventarioLogica.listar_insumos()
            alertas = InventarioLogica.listar_alertas_stock_bajo()

            if alertas:
                self.lbl_alerta.configure(
                    text=f"⚠️ {len(alertas)} insumo(s) con stock bajo"
                )
            else:
                self.lbl_alerta.configure(text="")

            opciones_combo = []
            for ins in insumos:
                self._insumos_cache[ins["id"]] = ins
                es_bajo = ins["stock_actual"] <= ins["stock_minimo"]
                stock_txt = f"{ins['stock_actual']} (Stock bajo)" if es_bajo else f"{ins['stock_actual']}"
                tags = ("bajo",) if es_bajo else ()

                self.tree_insumos.insert(
                    "",
                    "end",
                    iid=str(ins["id"]),
                    values=(
                        ins["id"],
                        ins["nombre"],
                        stock_txt,
                        ins["stock_minimo"],
                        ins["unidad_medida"],
                    ),
                    tags=tags,
                )
                opciones_combo.append(f"{ins['id']} - {ins['nombre']} ({ins['stock_actual']} {ins['unidad_medida']})")

            if opciones_combo:
                self.combo_insumo_entrada.configure(values=opciones_combo)
                if not self.combo_insumo_entrada.get() or self.combo_insumo_entrada.get() == "Sin insumos registrados":
                    self.combo_insumo_entrada.set(opciones_combo[0])
            else:
                self.combo_insumo_entrada.configure(values=["Sin insumos registrados"])
                self.combo_insumo_entrada.set("Sin insumos registrados")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los insumos:\n{e}")

    def _cargar_tabla_movimientos(self):
        for item in self.tree_movimientos.get_children():
            self.tree_movimientos.delete(item)

        try:
            movimientos = InventarioLogica.listar_movimientos()
            for m in movimientos[:50]:
                tipo = m.get("tipo_movimiento", "")
                cant_txt = f"{'+' if tipo == 'entrada' else '-'}{m.get('cantidad', 0)} {m.get('unidad_medida', '')}"
                motivo_txt = m.get("motivo") or (f"Orden #{m.get('orden_id')}" if m.get("orden_id") else "—")

                self.tree_movimientos.insert(
                    "",
                    "end",
                    values=(
                        m.get("id"),
                        m.get("fecha_hora"),
                        m.get("nombre_insumo"),
                        tipo.capitalize(),
                        cant_txt,
                        motivo_txt,
                    ),
                    tags=(tipo,),
                )
        except Exception as e:
            print(f"[Inventario] Error al cargar movimientos: {e}")

    # ========================================================================
    # EVENTOS Y MANEJO DE FORMULARIOS
    # ========================================================================

    def _al_seleccionar_insumo_tabla(self, _event=None):
        seleccion = self.tree_insumos.selection()
        if not seleccion:
            return

        insumo_id = int(seleccion[0])
        ins = self._insumos_cache.get(insumo_id)
        if not ins:
            return

        self._insumo_seleccionado_id = insumo_id
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, ins.get("nombre", ""))

        if ins.get("unidad_medida") in self.combo_unidad.cget("values"):
            self.combo_unidad.set(ins.get("unidad_medida"))
        else:
            self.combo_unidad.set(ins.get("unidad_medida", "litros"))

        self.entry_stock_minimo.delete(0, "end")
        self.entry_stock_minimo.insert(0, str(ins.get("stock_minimo", 0)))

        self.entry_stock_inicial.delete(0, "end")
        self.entry_stock_inicial.insert(0, str(ins.get("stock_actual", 0)))

        # Sincronizar el selector de entrada
        for opcion in self.combo_insumo_entrada.cget("values"):
            if opcion.startswith(f"{insumo_id} -"):
                self.combo_insumo_entrada.set(opcion)
                break

    def _limpiar_formulario_insumo(self):
        self._insumo_seleccionado_id = None
        self.entry_nombre.delete(0, "end")
        self.combo_unidad.set("litros")
        self.entry_stock_inicial.delete(0, "end")
        self.entry_stock_minimo.delete(0, "end")
        self.tree_insumos.selection_remove(self.tree_insumos.selection())

    def _evento_crear_insumo(self):
        nombre = self.entry_nombre.get().strip()
        unidad = self.combo_unidad.get().strip()
        stock_ini = self.entry_stock_inicial.get().strip() or "0"
        stock_min = self.entry_stock_minimo.get().strip() or "0"

        try:
            insumo_id = InventarioLogica.registrar_insumo(nombre, unidad, stock_ini, stock_min)
            messagebox.showinfo("Éxito", f"Insumo '{nombre}' registrado con éxito (ID #{insumo_id}).")
            self._limpiar_formulario_insumo()
            self.cargar_datos()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_actualizar_insumo(self):
        if not self._insumo_seleccionado_id:
            messagebox.showwarning("Atención", "Por favor seleccione un insumo de la tabla para actualizar.")
            return

        nombre = self.entry_nombre.get().strip()
        unidad = self.combo_unidad.get().strip()
        stock_min = self.entry_stock_minimo.get().strip() or "0"

        try:
            InventarioLogica.editar_insumo(self._insumo_seleccionado_id, nombre, unidad, stock_min)
            messagebox.showinfo("Éxito", f"Insumo ID #{self._insumo_seleccionado_id} actualizado correctamente.")
            self._limpiar_formulario_insumo()
            self.cargar_datos()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_eliminar_insumo(self):
        if not self._insumo_seleccionado_id:
            messagebox.showwarning("Atención", "Por favor seleccione un insumo de la tabla para eliminar.")
            return

        ins = self._insumos_cache.get(self._insumo_seleccionado_id)
        nombre = ins.get("nombre") if ins else f"ID #{self._insumo_seleccionado_id}"

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el insumo '{nombre}'?\n\n(Quedará desactivado del catálogo activo)."
        )
        if confirmar:
            try:
                InventarioLogica.eliminar_insumo(self._insumo_seleccionado_id)
                messagebox.showinfo("Éxito", f"Insumo '{nombre}' eliminado correctamente.")
                self._limpiar_formulario_insumo()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Error", str(err))

    def _evento_registrar_entrada(self):
        seleccion_combo = self.combo_insumo_entrada.get()
        if not seleccion_combo or seleccion_combo == "Sin insumos registrados":
            messagebox.showwarning("Atención", "Debe seleccionar un insumo para registrar entrada de stock.")
            return

        try:
            insumo_id = int(seleccion_combo.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selección de insumo inválida.")
            return

        cantidad_str = self.entry_cantidad_entrada.get().strip()
        motivo = self.entry_motivo_entrada.get().strip() or "Entrada manual de inventario"

        try:
            InventarioLogica.registrar_entrada(insumo_id, cantidad_str, motivo=motivo)
            messagebox.showinfo("Éxito", f"Entrada de {cantidad_str} registrada exitosamente.")
            self.entry_cantidad_entrada.delete(0, "end")
            self.entry_motivo_entrada.delete(0, "end")
            self.cargar_datos()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
