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