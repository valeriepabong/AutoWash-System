import tkinter as tk
from tkinter import ttk, messagebox
from logica.inventario_logica import InventarioLogica


class InventarioScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_interfaz()
        self.cargar_datos()

    def _crear_interfaz(self):
        # Título y Alerta de Stock Bajo
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

        # Tabla de Insumos
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

        # Configuración de color para stock bajo
        self.tree.tag_configure("bajo", background="#ffcccc")
        self.tree.pack(fill="both", expand=True, pady=10)

        # Formulario para registrar entrada
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
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            insumos = InventarioLogica.listar_insumos()
            alertas = InventarioLogica.listar_alertas_stock_bajo()

            # Mostrar texto global de alerta si existen insumos con stock bajo
            if alertas:
                self.lbl_alerta.config(
                    text=f"⚠️ ¡Atención! Hay {len(alertas)} insumo(s) con stock bajo."
                )
            else:
                self.lbl_alerta.config(text="")

            # Poblar la tabla
            for ins in insumos:
                es_bajo = ins["stock_actual"] <= ins["stock_minimo"]
                tags = ("bajo",) if es_bajo else ()

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        ins["id"],
                        ins["nombre"],
                        ins["stock_actual"],
                        ins["stock_minimo"],
                        ins["unidad_medida"],
                    ),
                    tags=tags,
                )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos del inventario:\n{e}"
            )

    def _registrar_entrada(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia",
                "Por favor, selecciona un insumo de la tabla primero.",
            )
            return

        item = self.tree.item(seleccion[0])
        insumo_id = item["values"][0]

        try:
            cantidad = float(self.txt_cantidad.get())
            motivo = self.txt_motivo.get().strip() or "Entrada manual"

            InventarioLogica.registrar_entrada(insumo_id, cantidad, motivo)
            messagebox.showinfo("Éxito", "Entrada de stock registrada correctamente.")

            # Limpiar entradas y recargar la tabla
            self.txt_cantidad.delete(0, tk.END)
            self.txt_motivo.delete(0, tk.END)
            self.cargar_datos()

        except ValueError as e:
            messagebox.showerror(
                "Error de entrada", f"Ingresa una cantidad válida numérica mayor a 0.\n{e}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al registrar entrada:\n{e}")