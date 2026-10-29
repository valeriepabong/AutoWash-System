import tkinter as tk
from tkinter import ttk, messagebox
from logica.inventario_logica import InventarioLogica


class InventarioScreen(ttk.Frame):
    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_interfaz()
        self.cargar_datos()

    def _crear_interfaz(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=5)

        lbl_titulo = ttk.Label(
            header_frame, text="Gestión de Inventario", font=("Arial", 16, "bold")
        )
        lbl_titulo.pack(side="left")

        self.lbl_alerta = ttk.Label(
            header_frame, text="", font=("Arial", 10, "bold"), foreground="red"
        )
        self.lbl_alerta.pack(side="right")

        if self.al_volver:
            btn_volver = ttk.Button(
                header_frame, text="Volver al Dashboard", command=self.al_volver
            )
            btn_volver.pack(side="right", padx=10)

        columnas = ("id", "nombre", "stock_actual", "stock_minimo", "unidad")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=7)

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Insumo")
        self.tree.heading("stock_actual", text="Stock Actual")
        self.tree.heading("stock_minimo", text="Stock Mínimo")
        self.tree.heading("unidad", text="Unidad")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=180, anchor="w")
        self.tree.column("stock_actual", width=90, anchor="center")
        self.tree.column("stock_minimo", width=90, anchor="center")
        self.tree.column("unidad", width=90, anchor="center")

        self.tree.tag_configure("bajo", background="#ffcccc")
        self.tree.pack(fill="both", expand=True, pady=(10, 5))

        # --- S5-12: acciones sobre el insumo seleccionado ---
        frame_acciones = ttk.Frame(self)
        frame_acciones.pack(fill="x", pady=(0, 5))

        ttk.Button(
            frame_acciones, text="Editar seleccionado", command=self._editar_insumo
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            frame_acciones, text="Eliminar seleccionado", command=self._eliminar_insumo
        ).pack(side="left", padx=5)
        ttk.Button(
            frame_acciones, text="Ver historial de movimientos",
            command=self._ver_historial,
        ).pack(side="left", padx=5)

        # --- Formulario para registrar un insumo desde cero ---
        form_nuevo = ttk.LabelFrame(self, text="Registrar Insumo Nuevo")
        form_nuevo.pack(fill="x", pady=5, ipady=5)

        ttk.Label(form_nuevo, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.txt_nombre_insumo = ttk.Entry(form_nuevo, width=20)
        self.txt_nombre_insumo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_nuevo, text="Unidad de medida:").grid(row=0, column=2, padx=5, pady=5)
        self.txt_unidad = ttk.Entry(form_nuevo, width=12)
        self.txt_unidad.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_nuevo, text="Stock inicial:").grid(row=1, column=0, padx=5, pady=5)
        self.txt_stock_inicial = ttk.Entry(form_nuevo, width=10)
        self.txt_stock_inicial.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_nuevo, text="Stock mínimo:").grid(row=1, column=2, padx=5, pady=5)
        self.txt_stock_minimo = ttk.Entry(form_nuevo, width=10)
        self.txt_stock_minimo.grid(row=1, column=3, padx=5, pady=5)

        btn_crear_insumo = ttk.Button(
            form_nuevo, text="Crear Insumo", command=self._registrar_insumo_nuevo
        )
        btn_crear_insumo.grid(row=0, column=4, rowspan=2, padx=10, pady=5)

        # --- Formulario: registrar entrada de stock a un insumo ya creado ---
        form_frame = ttk.LabelFrame(self, text="Registrar Entrada de Stock")
        form_frame.pack(fill="x", pady=5, ipady=5)

        ttk.Label(form_frame, text="Cantidad:").grid(row=0, column=0, padx=5, pady=5)
        self.txt_cantidad = ttk.Entry(form_frame, width=10)
        self.txt_cantidad.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Motivo:").grid(row=0, column=2, padx=5, pady=5)
        self.txt_motivo = ttk.Entry(form_frame, width=25)
        self.txt_motivo.grid(row=0, column=3, padx=5, pady=5)

        btn_registrar = ttk.Button(
            form_frame, text="Agregar Stock", command=self._registrar_entrada
        )
        btn_registrar.grid(row=0, column=4, padx=10, pady=5)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            insumos = InventarioLogica.listar_insumos()
            alertas = InventarioLogica.listar_alertas_stock_bajo()

            if alertas:
                self.lbl_alerta.config(
                    text=f"⚠️ ¡Atención! Hay {len(alertas)} insumo(s) con stock bajo."
                )
            else:
                self.lbl_alerta.config(text="")

            for ins in insumos:
                es_bajo = ins["stock_actual"] <= ins["stock_minimo"]
                tags = ("bajo",) if es_bajo else ()

                self.tree.insert(
                    "", "end", iid=str(ins["id"]),
                    values=(
                        ins["id"], ins["nombre"], ins["stock_actual"],
                        ins["stock_minimo"], ins["unidad_medida"],
                    ),
                    tags=tags,
                )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos del inventario:\n{e}"
            )

    def _registrar_insumo_nuevo(self):
        nombre = self.txt_nombre_insumo.get().strip()
        unidad = self.txt_unidad.get().strip()
        stock_inicial = self.txt_stock_inicial.get().strip() or "0"
        stock_minimo = self.txt_stock_minimo.get().strip() or "0"

        try:
            InventarioLogica.registrar_insumo(nombre, unidad, stock_inicial, stock_minimo)
            messagebox.showinfo("Éxito", f"Insumo '{nombre}' creado correctamente.")

            self.txt_nombre_insumo.delete(0, tk.END)
            self.txt_unidad.delete(0, tk.END)
            self.txt_stock_inicial.delete(0, tk.END)
            self.txt_stock_minimo.delete(0, tk.END)

            self.cargar_datos()

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al crear el insumo:\n{e}")

    def _registrar_entrada(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia", "Por favor, selecciona un insumo de la tabla primero."
            )
            return

        item = self.tree.item(seleccion[0])
        insumo_id = item["values"][0]

        try:
            cantidad = float(self.txt_cantidad.get())
            motivo = self.txt_motivo.get().strip() or "Entrada manual"

            InventarioLogica.registrar_entrada(insumo_id, cantidad, motivo)
            messagebox.showinfo("Éxito", "Entrada de stock registrada correctamente.")

            self.txt_cantidad.delete(0, tk.END)
            self.txt_motivo.delete(0, tk.END)
            self.cargar_datos()

        except ValueError as e:
            messagebox.showerror(
                "Error de entrada", f"Ingresa una cantidad válida numérica mayor a 0.\n{e}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al registrar entrada:\n{e}")

    # ---------- S5-12: editar, eliminar e historial ----------

    def _insumo_seleccionado(self):
        """Devuelve el dict del insumo elegido en la tabla, o None (y avisa)."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia", "Por favor, selecciona un insumo de la tabla primero."
            )
            return None

        insumo_id = int(seleccion[0])
        for insumo in InventarioLogica.listar_insumos():
            if insumo["id"] == insumo_id:
                return insumo
        messagebox.showerror("Error", "El insumo seleccionado ya no existe.")
        self.cargar_datos()
        return None

    def _editar_insumo(self):
        insumo = self._insumo_seleccionado()
        if insumo is None:
            return

        ventana = tk.Toplevel(self)
        ventana.title(f"Editar insumo #{insumo['id']}")
        ventana.transient(self.winfo_toplevel())
        ventana.resizable(False, False)

        ttk.Label(ventana, text="Nombre:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        txt_nombre = ttk.Entry(ventana, width=28)
        txt_nombre.insert(0, insumo["nombre"])
        txt_nombre.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(ventana, text="Unidad de medida:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        txt_unidad = ttk.Entry(ventana, width=28)
        txt_unidad.insert(0, insumo["unidad_medida"])
        txt_unidad.grid(row=1, column=1, padx=10, pady=8)

        ttk.Label(ventana, text="Stock mínimo:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        txt_minimo = ttk.Entry(ventana, width=28)
        txt_minimo.insert(0, f"{insumo['stock_minimo']:g}")
        txt_minimo.grid(row=2, column=1, padx=10, pady=8)

        ttk.Label(
            ventana,
            text="El stock actual no se edita aquí: cambia con entradas y consumos.",
            foreground="gray",
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 8))

        def guardar():
            try:
                InventarioLogica.editar_insumo(
                    insumo["id"], txt_nombre.get(), txt_unidad.get(), txt_minimo.get()
                )
            except ValueError as e:
                messagebox.showerror("Error de validación", str(e), parent=ventana)
                return
            ventana.destroy()
            messagebox.showinfo("Éxito", "Insumo actualizado correctamente.")
            self.cargar_datos()

        botones = ttk.Frame(ventana)
        botones.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar", command=ventana.destroy).pack(side="left", padx=5)

        ventana.grab_set()
        txt_nombre.focus_set()

    def _eliminar_insumo(self):
        insumo = self._insumo_seleccionado()
        if insumo is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Desea eliminar el insumo '{insumo['nombre']}'?\n\n"
            "Dejará de aparecer en el inventario, pero su historial se conserva.",
        )
        if not confirmar:
            return

        try:
            InventarioLogica.eliminar_insumo(insumo["id"])
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Éxito", "Insumo eliminado correctamente.")
        self.cargar_datos()

    def _ver_historial(self):
        """Muestra los movimientos del insumo seleccionado (o de todos si no hay selección)."""
        seleccion = self.tree.selection()
        insumo_id = int(seleccion[0]) if seleccion else None

        try:
            movimientos = InventarioLogica.listar_movimientos(insumo_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{e}")
            return

        ventana = tk.Toplevel(self)
        titulo = "Historial de movimientos"
        if insumo_id is not None and movimientos:
            titulo += f" - {movimientos[0]['nombre_insumo']}"
        elif insumo_id is None:
            titulo += " - todos los insumos"
        ventana.title(titulo)
        ventana.transient(self.winfo_toplevel())
        ventana.geometry("780x380")

        columnas = ("fecha", "insumo", "tipo", "cantidad", "orden", "motivo")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        encabezados = {
            "fecha": ("Fecha y hora", 140), "insumo": ("Insumo", 150),
            "tipo": ("Tipo", 70), "cantidad": ("Cantidad", 90),
            "orden": ("Orden", 60), "motivo": ("Motivo", 240),
        }
        for clave, (texto, ancho) in encabezados.items():
            tabla.heading(clave, text=texto)
            tabla.column(clave, width=ancho, anchor="w" if clave in ("insumo", "motivo") else "center")

        tabla.tag_configure("entrada", foreground="#1b7f3b")
        tabla.tag_configure("salida", foreground="#b02a2a")

        for m in movimientos:
            tabla.insert(
                "", "end",
                values=(
                    m["fecha_hora"], m["nombre_insumo"], m["tipo_movimiento"].capitalize(),
                    f"{m['cantidad']:g} {m['unidad_medida']}",
                    m["orden_id"] if m["orden_id"] else "-",
                    m["motivo"] or "",
                ),
                tags=(m["tipo_movimiento"],),
            )

        if not movimientos:
            tabla.insert("", "end", values=("", "Sin movimientos registrados", "", "", "", ""))

        barra = ttk.Scrollbar(ventana, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        barra.pack(side="right", fill="y", pady=10, padx=(0, 10))