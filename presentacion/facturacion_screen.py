import os
import subprocess
import sys
from tkinter import ttk, messagebox
import customtkinter as ctk

from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class FacturacionScreen(ctk.CTkFrame):
    """
    Pantalla de Gestión de Facturación fiel al diseño Figma (Imagen 3 derecha):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Facturacion'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Tarjeta blanca superior 'Seleccion de orden entregada' con combo y botón 'Recargar' (#F68B2E).
    - Sección media 'Detalle de servicios' con tabla Autowash.Treeview (cabecera #BCE3F0).
    - Tarjeta blanca inferior con 'Metodo de pago', 'Total a pagar : $ 0' y botón 'Generar comprobante'.
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

        self.ordenes_map = {}
        self.orden_seleccionada_id = None

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self.cargar_ordenes_pendientes()

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Facturacion",
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

        if self.al_ir_facturas:
            ctk.CTkButton(
                header_nav,
                text="📑 Historial de facturas",
                command=self.al_ir_facturas,
                fg_color="#0B4F66",
                hover_color="#336E84",
                text_color="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
                height=32,
                corner_radius=12
            ).pack(side="right")

        ctk.CTkLabel(
            self.scroll_body,
            text="Gestión de facturación",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Comprobantes para órdenes entregadas",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 18))

        # ————— TARJETA BLANCA SUPERIOR: Seleccion de orden entregada —————
        card_orden = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_orden.pack(fill="x", pady=(0, 18))

        inner_orden = ctk.CTkFrame(card_orden, fg_color="transparent")
        inner_orden.pack(fill="both", expand=True, padx=24, pady=18)

        ctk.CTkLabel(
            inner_orden,
            text="Seleccion de orden entregada",
            font=("Georgia", 20),
            text_color="#3C3B3B",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            inner_orden,
            text="Orden lista para facturar",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        fila_orden = ctk.CTkFrame(inner_orden, fg_color="transparent")
        fila_orden.pack(fill="x")

        self.combo_ordenes = ctk.CTkComboBox(
            fila_orden,
            state="readonly",
            height=40,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            button_color="#FFFFFF",
            button_hover_color="#E7F9FF",
            text_color="#111111",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#111111",
            dropdown_hover_color="#D9F0F9",
            command=self._al_seleccionar_orden,
            font=("Segoe UI", 12)
        )
        self.combo_ordenes.pack(side="left", fill="x", expand=True, padx=(0, 14))

        ctk.CTkButton(
            fila_orden,
            text="Recargar",
            width=150,
            height=40,
            corner_radius=14,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            command=self.cargar_ordenes_pendientes
        ).pack(side="right")

        # ————— SECCIÓN MEDIA: Detalle de servicios —————
        ctk.CTkLabel(
            self.scroll_body,
            text="Detalle de servicios",
            font=("Georgia", 15),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        card_detalle = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_detalle.pack(fill="both", expand=True, pady=(0, 18))

        inner_detalle = ctk.CTkFrame(card_detalle, fg_color="transparent")
        inner_detalle.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("servicio", "precio")
        self.tree_detalle = ttk.Treeview(
            inner_detalle,
            columns=columnas,
            show="headings",
            height=6,
            style="Autowash.Treeview"
        )
        self.tree_detalle.heading("servicio", text="Servicio")
        self.tree_detalle.heading("precio", text="Precio aplicado ( $ )")
        self.tree_detalle.column("servicio", width=360, anchor="center")
        self.tree_detalle.column("precio", width=180, anchor="center")
        self.tree_detalle.pack(fill="both", expand=True)

        # ————— TARJETA BLANCA INFERIOR DE PAGO —————
        card_pago = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_pago.pack(fill="x")

        inner_pago = ctk.CTkFrame(card_pago, fg_color="transparent")
        inner_pago.pack(fill="x", padx=24, pady=18)
        inner_pago.grid_columnconfigure(0, weight=1)
        inner_pago.grid_columnconfigure(1, weight=1)
        inner_pago.grid_columnconfigure(2, weight=1)

        # Izquierda: Label "Metodo de pago" + self.combo_metodo
        col_metodo = ctk.CTkFrame(inner_pago, fg_color="transparent")
        col_metodo.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            col_metodo,
            text="Metodo de pago",
            font=("Segoe UI", 12, "bold"),
            text_color="#111111",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.combo_metodo = ctk.CTkComboBox(
            col_metodo,
            state="readonly",
            values=["Efectivo", "Tarjeta", "Transferencia"],
            width=190,
            height=40,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#000000",
            button_color="#FFFFFF",
            button_hover_color="#E7F9FF",
            text_color="#111111",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#111111",
            dropdown_hover_color="#D9F0F9",
            font=("Segoe UI", 12)
        )
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.pack(anchor="w")

        # Centro: Total a pagar
        self.label_total = ctk.CTkLabel(
            inner_pago,
            text="Total a pagar : $ 0",
            font=("Georgia", 16, "bold"),
            text_color="#111111"
        )
        self.label_total.grid(row=0, column=1, sticky="s", pady=6)

        # Derecha: Botón Generar comprobante
        btn_generar = ctk.CTkButton(
            inner_pago,
            text="Generar comprobante",
            command=self._generar_comprobante,
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            height=42,
            corner_radius=14,
            width=190
        )
        btn_generar.grid(row=0, column=2, sticky="se")

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

        self.label_total.configure(text=f"Total a pagar : $ {total:,.0f}")

    def _limpiar_detalle(self):
        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)
        self.label_total.configure(text="Total a pagar : $ 0")

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
