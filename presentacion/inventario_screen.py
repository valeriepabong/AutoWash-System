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
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=10)

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
        self.tree.pack(fill="both", expand=True, pady=10)

        # --- NUEVO: formulario para registrar un insumo desde cero ---
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

        # --- Formulario existente: registrar entrada de stock a un insumo ya creado ---
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
                    "", "end",
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