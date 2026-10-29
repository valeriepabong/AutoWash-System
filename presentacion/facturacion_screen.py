import os
import subprocess
import sys

import customtkinter as ctk
from tkinter import ttk, messagebox

from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura


class FacturacionScreen(ctk.CTkFrame):
    """
    Pantalla de Facturación (S5-07).

    Usa exactamente los dos métodos que definió backend para esta tarea:
        FacturacionLogica.listar_ordenes_por_facturar()
            -> [{id, vehiculo_id, placa, nombre_cliente, fecha_hora, total, estado}]
        FacturacionLogica.obtener_detalle_orden(orden_id)
            -> [{id, servicio_id, precio_aplicado, nombre_servicio}]
    y para generar el comprobante:
        FacturacionLogica.generar_factura(orden_id, metodo_pago) -> id de la factura
        FacturacionLogica.obtener_factura(factura_id) -> dict con todo lo que pide el PDF
    """

    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.ordenes_map = {}
        self.orden_seleccionada_id = None

        self._crear_interfaz()
        self.cargar_ordenes_pendientes()

    def _crear_interfaz(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame, text="Módulo de Facturación", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        if self.al_volver:
            ctk.CTkButton(
                header_frame, text="Volver al Dashboard", command=self.al_volver, width=150
            ).pack(side="right")

        frame_orden = ctk.CTkFrame(self)
        frame_orden.pack(fill="x", pady=5, padx=5, ipady=5)

        ctk.CTkLabel(frame_orden, text="Órdenes listas para facturar:").grid(
            row=0, column=0, padx=10, pady=10
        )

        self.combo_ordenes = ctk.CTkComboBox(
            frame_orden, state="readonly", width=350, command=self._al_seleccionar_orden
        )
        self.combo_ordenes.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(
            frame_orden, text="Recargar", width=90, command=self.cargar_ordenes_pendientes
        ).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkLabel(
            self, text="Detalle de servicios:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(15, 5), padx=5)

        columnas = ("servicio", "precio")
        self.tree_detalle = ttk.Treeview(self, columns=columnas, show="headings", height=6)
        self.tree_detalle.heading("servicio", text="Servicio")
        self.tree_detalle.heading("precio", text="Precio aplicado")
        self.tree_detalle.column("servicio", width=300, anchor="w")
        self.tree_detalle.column("precio", width=120, anchor="e")
        self.tree_detalle.pack(fill="both", expand=True, pady=5, padx=5)

        frame_pago = ctk.CTkFrame(self, fg_color="transparent")
        frame_pago.pack(fill="x", pady=10, padx=5)

        self.label_total = ctk.CTkLabel(
            frame_pago, text="Total a pagar: $0", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_total.pack(side="left", padx=5)

        ctk.CTkLabel(frame_pago, text="Método de pago:").pack(side="left", padx=(30, 5))
        self.combo_metodo = ctk.CTkComboBox(
            frame_pago, state="readonly", values=["Efectivo", "Tarjeta", "Transferencia"], width=140
        )
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_pago, text="Generar Comprobante", command=self._generar_comprobante, fg_color="green"
        ).pack(side="right", padx=5)

    # ---------- Carga de datos ----------

    def cargar_ordenes_pendientes(self):
        try:
            ordenes = FacturacionLogica.listar_ordenes_por_facturar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron consultar las órdenes pendientes:\n{e}")
            return

        self.ordenes_map.clear()
        opciones = []
        for o in ordenes:
            texto = f"Orden #{o['id']} - {o['placa']} - {o['nombre_cliente']} (${o['total']:,.0f})"
            self.ordenes_map[texto] = o["id"]
            opciones.append(texto)

        self.combo_ordenes.configure(values=opciones or ["Sin órdenes pendientes"])
        self.combo_ordenes.set(opciones[0] if opciones else "Sin órdenes pendientes")
        self.orden_seleccionada_id = self.ordenes_map[opciones[0]] if opciones else None
        self._limpiar_detalle()
        if self.orden_seleccionada_id:
            self._cargar_detalle_orden(self.orden_seleccionada_id)

    def _al_seleccionar_orden(self, seleccion):
        if seleccion in self.ordenes_map:
            self.orden_seleccionada_id = self.ordenes_map[seleccion]
            self._cargar_detalle_orden(self.orden_seleccionada_id)

    def _cargar_detalle_orden(self, orden_id):
        self._limpiar_detalle()
        try:
            detalle = FacturacionLogica.obtener_detalle_orden(orden_id)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        total = 0.0
        for item in detalle:
            precio = float(item["precio_aplicado"])
            total += precio
            self.tree_detalle.insert(
                "", "end", values=(item["nombre_servicio"], f"${precio:,.0f}")
            )

        self.label_total.configure(text=f"Total a pagar: ${total:,.0f}")

    def _limpiar_detalle(self):
        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)
        self.label_total.configure(text="Total a pagar: $0")

    # ---------- Eventos ----------

    def _generar_comprobante(self):
        if not self.orden_seleccionada_id:
            messagebox.showwarning("Atención", "Seleccione una orden antes de facturar.")
            return

        metodo_pago = self.combo_metodo.get().lower()

        try:
            factura_id = FacturacionLogica.generar_factura(self.orden_seleccionada_id, metodo_pago)
        except ValueError as e:
            messagebox.showerror("Error de Facturación", str(e))
            return

        ruta_pdf = self._generar_y_abrir_pdf(factura_id)

        if ruta_pdf:
            messagebox.showinfo(
                "Comprobante generado",
                f"Factura #{factura_id} generada correctamente.\n\nEl PDF se guardó en:\n{ruta_pdf}",
            )
        else:
            messagebox.showinfo(
                "Comprobante generado",
                f"Factura #{factura_id} generada correctamente.\n"
                f"(No fue posible generar el PDF, pero la factura quedó registrada.)",
            )

        self.cargar_ordenes_pendientes()

    def _generar_y_abrir_pdf(self, factura_id):
        try:
            factura = FacturacionLogica.obtener_factura(factura_id)

            carpeta_destino = os.path.join(os.path.expanduser("~"), "Documents", "AutoWash_Facturas")
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_pdf = os.path.join(carpeta_destino, f"factura_{factura_id}.pdf")
            generar_pdf_factura(factura, ruta_pdf)
            self._abrir_pdf(ruta_pdf)
            return ruta_pdf
        except Exception as e:
            print(f"No se pudo generar/abrir el PDF de la factura: {e}")
            return None

    def _abrir_pdf(self, ruta_pdf):
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta_pdf)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", ruta_pdf])
            else:
                subprocess.run(["xdg-open", ruta_pdf])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")