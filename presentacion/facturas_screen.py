import os
import subprocess
import sys
from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.facturacion_logica import FacturacionLogica
from logica.pdf_factura import generar_pdf_factura
from presentacion.sidebar_component import SidebarComponent, configurar_estilo_tabla


class FacturasScreen(ctk.CTkFrame):
    """
    Pantalla de Facturas emitidas fiel al diseño Figma (Imagen 1):
    - Barra lateral #0B4F66 (SidebarComponent) con sección activa 'Facturas'.
    - Área principal #E7F9FF con enlace '← volver al panel principal'.
    - Tarjeta blanca superior de resumen (height=50, corner_radius=14).
    - Tabla Autowash.Treeview en contenedor blanco con 7 columnas centradas.
    - Botones inferiores alineados a la izquierda en naranja #F68B2E.
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

        self.pack(fill="both", expand=True)

        configurar_estilo_tabla()
        self._crear_interfaz()
        self._cargar_facturas()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                         #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Facturas",
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
            text="Facturas emitidas",
            font=("Georgia", 30),
            text_color="#000000",
            anchor="w"
        ).pack(fill="x", pady=(4, 2))

        ctk.CTkLabel(
            self.scroll_body,
            text="Historial de comprobantes generados",
            font=("Segoe UI", 13),
            text_color="#666666",
            anchor="w"
        ).pack(fill="x", pady=(0, 16))

        # ————— TARJETA BLANCA DE RESUMEN SUPERIOR —————
        card_resumen = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#CCE5F0",
            height=50
        )
        card_resumen.pack(fill="x", pady=(0, 18))
        card_resumen.pack_propagate(False)

        self.label_resumen = ctk.CTkLabel(
            card_resumen,
            text="0 factura(s) emitida(s) - Total facturado: $0",
            font=("Georgia", 14),
            text_color="#3C3B3B",
            anchor="w"
        )
        self.label_resumen.pack(fill="both", expand=True, padx=20)

        # ————— CONTENEDOR BLANCO: TABLA DE FACTURAS —————
        card_tabla = ctk.CTkFrame(
            self.scroll_body,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#CCE5F0"
        )
        card_tabla.pack(fill="both", expand=True, pady=(0, 18))

        inner_tabla = ctk.CTkFrame(card_tabla, fg_color="transparent")
        inner_tabla.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("id", "orden", "fecha", "placa", "cliente", "metodo", "total")
        self.tabla = ttk.Treeview(
            inner_tabla,
            columns=columnas,
            show="headings",
            height=10,
            selectmode="browse",
            style="Autowash.Treeview"
        )
        encabezados = {
            "id": ("N.°", 50),
            "orden": ("Orden", 65),
            "fecha": ("Fecha de emisión", 150),
            "placa": ("Placa", 95),
            "cliente": ("Cliente", 160),
            "metodo": ("Método de pago", 120),
            "total": ("Total", 110),
        }
        for clave, (texto, ancho) in encabezados.items():
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor="center")
        self.tabla.pack(fill="both", expand=True)

        # ————— FILA INFERIOR DE BOTONES —————
        fila_botones = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        fila_botones.pack(fill="x", pady=(0, 4))

        ctk.CTkButton(
            fila_botones,
            text="Reimprimir PDF de la seleccionada",
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=14,
            height=42,
            width=270,
            command=self._evento_reimprimir,
        ).pack(side="left", padx=(0, 14))

        ctk.CTkButton(
            fila_botones,
            text="Recargar",
            fg_color="#F68B2E",
            hover_color="#E0781E",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=14,
            height=42,
            width=140,
            command=self._cargar_facturas
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
