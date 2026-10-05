import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import sys

from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura
from datos.ordenes_datos import OrdenesDatos
from datos.facturacion_datos import FacturacionDatos


class FacturacionScreen(ttk.Frame):
    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.ordenes_map = {}
        self.orden_seleccionada_id = None

        self._crear_interfaz()
        self.cargar_ordenes_pendientes()

    def _crear_interfaz(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=5)

        ttk.Label(
            header_frame, text="Módulo de Facturación", font=("Arial", 16, "bold")
        ).pack(side="left")

        if self.al_volver:
            btn_volver = ttk.Button(
                header_frame, text="Volver al Dashboard", command=self.al_volver
            )
            btn_volver.pack(side="right", padx=10)

        frame_orden = ttk.LabelFrame(self, text="Selección de Orden Entregada")
        frame_orden.pack(fill="x", pady=5, ipady=5)

        ttk.Label(frame_orden, text="Órdenes listos para facturar:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.combo_ordenes = ttk.Combobox(frame_orden, state="readonly", width=45)
        self.combo_ordenes.grid(row=0, column=1, padx=5, pady=5)
        self.combo_ordenes.bind("<<ComboboxSelected>>", self._al_seleccionar_orden)

        btn_refrescar = ttk.Button(
            frame_orden, text="🔄 Recargar", command=self.cargar_ordenes_pendientes
        )
        btn_refrescar.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(
            self, text="Detalle de Servicios:", font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(10, 2))

        columnas = ("servicio", "precio")
        self.tree_detalle = ttk.Treeview(self, columns=columnas, show="headings", height=6)
        self.tree_detalle.heading("servicio", text="Servicio")
        self.tree_detalle.heading("precio", text="Precio Aplicado ($)")
        self.tree_detalle.column("servicio", width=250, anchor="w")
        self.tree_detalle.column("precio", width=100, anchor="e")
        self.tree_detalle.pack(fill="both", expand=True, pady=5)

        frame_pago = ttk.Frame(self)
        frame_pago.pack(fill="x", pady=10)

        self.lbl_total = ttk.Label(
            frame_pago, text="Total a Pagar: $0.00", font=("Arial", 12, "bold")
        )
        self.lbl_total.pack(side="left", padx=5)

        btn_facturar = ttk.Button(
            frame_pago, text="💳 Generar Comprobante", command=self._generar_comprobante,
        )
        btn_facturar.pack(side="right", padx=5)

        ttk.Label(frame_pago, text="Método de Pago:").pack(side="right", padx=2)

        self.combo_metodo = ttk.Combobox(
            frame_pago, state="readonly",
            values=["Efectivo", "Tarjeta", "Transferencia"], width=15,
        )
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.pack(side="right", padx=5)

    def cargar_ordenes_pendientes(self):
        try:
            ordenes = OrdenesDatos.listar_ordenes(solo_activas=False)
            ordenes_pendientes = [
                o
                for o in ordenes
                if o["estado"] == "entregado"
                and FacturacionDatos.obtener_factura_por_orden(o["id"]) is None
            ]

            self.ordenes_map.clear()
            opciones = []

            for o in ordenes_pendientes:
                texto = f"Orden #{o['id']} - Placa: {o['placa']} ({o['fecha_hora']})"
                self.ordenes_map[texto] = o["id"]
                opciones.append(texto)

            self.combo_ordenes["values"] = opciones
            self.combo_ordenes.set("")
            self.orden_seleccionada_id = None
            self._limpiar_detalle()

            if not opciones:
                self.combo_ordenes.set("No hay órdenes pendientes por facturar")

        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar órdenes pendientes:\n{e}")

    def _al_seleccionar_orden(self, event=None):
        seleccion = self.combo_ordenes.get()
        if seleccion in self.ordenes_map:
            self.orden_seleccionada_id = self.ordenes_map[seleccion]
            self._cargar_detalle_orden(self.orden_seleccionada_id)

    def _cargar_detalle_orden(self, orden_id):
        self._limpiar_detalle()
        try:
            detalles = OrdenesDatos.obtener_detalle_de_orden(orden_id)
            total = 0.0

            for item in detalles:
                precio = float(item["precio_aplicado"])
                total += precio
                nombre_servicio = item.get("nombre_servicio", f"Servicio #{item['servicio_id']}")
                self.tree_detalle.insert(
                    "", "end", values=(nombre_servicio, f"${precio:.2f}")
                )

            self.lbl_total.config(text=f"Total a Pagar: ${total:.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el detalle de la orden:\n{e}")

    def _limpiar_detalle(self):
        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)
        self.lbl_total.config(text="Total a Pagar: $0.00")

    def _generar_comprobante(self):
        if not self.orden_seleccionada_id:
            messagebox.showwarning(
                "Atención", "Por favor selecciona una orden antes de facturar."
            )
            return

        metodo_pago = self.combo_metodo.get().lower()

        try:
            factura_id = FacturacionLogica.generar_factura(
                self.orden_seleccionada_id, metodo_pago
            )

            ruta_pdf = self._generar_y_abrir_pdf(factura_id)

            if ruta_pdf:
                messagebox.showinfo(
                    "Comprobante Generado",
                    f"¡Factura #{factura_id} generada exitosamente!\n\n"
                    f"El PDF se guardó en:\n{ruta_pdf}",
                )
            else:
                messagebox.showinfo(
                    "Comprobante Generado",
                    f"¡Factura #{factura_id} generada exitosamente!\n"
                    f"(No fue posible generar el PDF, pero la factura quedó registrada.)",
                )

            self.cargar_ordenes_pendientes()

        except ValueError as e:
            messagebox.showerror("Error de Facturación", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error:\n{e}")

    def _generar_y_abrir_pdf(self, factura_id):
        """
        Genera el PDF de la factura en la carpeta de Documentos del usuario
        y lo abre automáticamente con el visor de PDF predeterminado.
        Si algo falla, devuelve None sin interrumpir el flujo de facturación.
        """
        try:
            factura = FacturacionLogica.obtener_factura(factura_id)

            carpeta_destino = os.path.join(os.path.expanduser("~"), "Documents", "AutoWash_Facturas")
            os.makedirs(carpeta_destino, exist_ok=True)

            nombre_archivo = f"factura_{factura_id}.pdf"
            ruta_pdf = os.path.join(carpeta_destino, nombre_archivo)

            generar_pdf_factura(factura, ruta_pdf)

            self._abrir_pdf(ruta_pdf)
            return ruta_pdf

        except Exception as e:
            print(f"No se pudo generar/abrir el PDF de la factura: {e}")
            return None

    def _abrir_pdf(self, ruta_pdf):
        """Abre el PDF con el programa predeterminado del sistema operativo."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta_pdf)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", ruta_pdf])
            else:
                subprocess.run(["xdg-open", ruta_pdf])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")