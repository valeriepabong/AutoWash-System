"""
Pantalla de Facturas emitidas (S5-11).

Muestra las facturas ya generadas y permite reimprimir el PDF de cualquiera.

Usa la lógica que ya existe:
    FacturacionLogica.listar_facturas()
        -> [{id, orden_id, metodo_pago, total, fecha_hora, placa, nombre_cliente}]
    FacturacionLogica.obtener_factura(factura_id)
        -> dict completo que necesita logica.pdf_factura.generar_pdf_factura
"""

import os
import subprocess
import sys
from tkinter import messagebox, ttk

import customtkinter as ctk

from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura


class FacturasScreen(ctk.CTkFrame):

    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self._crear_interfaz()
        self._cargar_facturas()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header, text="Facturas Emitidas", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        if self.al_volver:
            ctk.CTkButton(
                header, text="Volver al Dashboard", fg_color="gray",
                hover_color="#505050", width=140, command=self.al_volver,
            ).pack(side="right")

        self.label_resumen = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        self.label_resumen.pack(fill="x", padx=10, pady=(0, 5))

        columnas = ("id", "orden", "fecha", "placa", "cliente", "metodo", "total")
        self.tabla = ttk.Treeview(
            self, columns=columnas, show="headings", height=12, selectmode="browse"
        )
        encabezados = {
            "id": ("N.°", 50), "orden": ("Orden", 60), "fecha": ("Fecha de emisión", 150),
            "placa": ("Placa", 80), "cliente": ("Cliente", 160),
            "metodo": ("Método de pago", 110), "total": ("Total", 100),
        }
        for clave, (texto, ancho) in encabezados.items():
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor="e" if clave == "total" else "center")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=8)

        fila_botones = ctk.CTkFrame(self, fg_color="transparent")
        fila_botones.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            fila_botones, text="Reimprimir PDF de la seleccionada", fg_color="green",
            command=self._evento_reimprimir,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            fila_botones, text="Recargar", width=90, command=self._cargar_facturas
        ).pack(side="left")

    # ---------- Carga de datos ----------

    def _cargar_facturas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            facturas = FacturacionLogica.listar_facturas()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudieron cargar las facturas:\n{err}")
            return

        for f in facturas:
            self.tabla.insert(
                "", "end", iid=str(f["id"]),
                values=(
                    f["id"], f["orden_id"], f["fecha_hora"], f["placa"],
                    f["nombre_cliente"], f["metodo_pago"].capitalize(),
                    f"${f['total']:,.0f}",
                ),
            )

        total = sum(f["total"] for f in facturas)
        self.label_resumen.configure(
            text=f"{len(facturas)} factura(s) emitida(s) - Total facturado: ${total:,.0f}"
        )

    # ---------- Eventos ----------

    def _evento_reimprimir(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una factura de la tabla.")
            return

        factura_id = int(seleccion[0])

        try:
            factura = FacturacionLogica.obtener_factura(factura_id)
            if factura is None:
                messagebox.showerror("Error", "La factura ya no existe.")
                return

            carpeta = os.path.join(os.path.expanduser("~"), "Documents", "AutoWash_Facturas")
            os.makedirs(carpeta, exist_ok=True)
            ruta_pdf = os.path.join(carpeta, f"factura_{factura_id}.pdf")

            generar_pdf_factura(factura, ruta_pdf)
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{err}")
            return

        self._abrir_pdf(ruta_pdf)
        messagebox.showinfo("PDF generado", f"El PDF se guardó en:\n{ruta_pdf}")

    def _abrir_pdf(self, ruta_pdf):
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta_pdf)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", ruta_pdf])
            else:
                subprocess.run(["xdg-open", ruta_pdf])
        except Exception as err:
            print(f"No se pudo abrir el PDF automáticamente: {err}")