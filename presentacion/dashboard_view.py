import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox

from logica.dashboard_logica import DashboardLogica
from logica.facturacion_logica import FacturacionLogica
from presentacion.sidebar_component import SidebarComponent


class DashboardView(ctk.CTkFrame):
    """
    Panel de Control de AutoWash System.
    Diseño fiel al prototipo React:
    - Barra lateral #0B4F66 con logo 🚘 AUTOWASH SYSTEM y menú de navegación.
    - Cabecera: título, buscador y avatar de usuario.
    - 4 tarjetas KPI con datos reales obtenidos a través de DashboardLogica.
    - Tabla 'Vehículos en Servicio Activo' filtrable, datos 100 % desde DashboardLogica.
    Paleta: #0B4F66 | #E7F9FF | #3F8FA9 | #F68B2E | #F79D4F | #A2EDA2 | #FFECAF | #85CDE5.
    """

    def __init__(self, parent, al_volver=None, al_ir_dashboard=None,
                 al_ir_clientes=None, al_ir_vehiculos=None,
                 al_ir_empleados=None, al_ir_servicios=None,
                 al_ir_inventario=None, al_ir_facturacion=None,
                 al_ir_reportes=None, al_ir_catalogo=None,
                 al_ir_facturas=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(parent, fg_color="#E7F9FF", corner_radius=0)
        self.al_volver = al_volver
        self.al_ir_dashboard = al_ir_dashboard or al_volver
        self.al_ir_clientes = al_ir_clientes
        self.al_ir_vehiculos = al_ir_vehiculos
        self.al_ir_empleados = al_ir_empleados
        self.al_ir_servicios = al_ir_servicios
        self.al_ir_inventario = al_ir_inventario
        self.al_ir_facturacion = al_ir_facturacion
        self.al_ir_reportes = al_ir_reportes
        self.al_ir_catalogo = al_ir_catalogo
        self.al_ir_facturas = al_ir_facturas
        self.al_cerrar_sesion = al_cerrar_sesion

        self._todos_vehiculos = []
        self._kpi_labels = {}
        self.pack(fill="both", expand=True)
        self._construir_interfaz()

    # ========================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        # ------------------------------------------------------------------ #
        # 1. BARRA LATERAL (SIDEBAR)                                          #
        # ------------------------------------------------------------------ #
        self.sidebar = SidebarComponent(
            self,
            seccion_activa="Panel principal",
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
        # 2. CONTENIDO PRINCIPAL                                              #
        # ------------------------------------------------------------------ #
        self.main_container = ctk.CTkFrame(self, fg_color="#E7F9FF", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        self._construir_cabecera()

        self.scroll_body = ctk.CTkScrollableFrame(self.main_container, fg_color="#E7F9FF")
        self.scroll_body.pack(fill="both", expand=True, padx=16, pady=(2, 12))

        self._construir_kpis()
        self._construir_tabla()

        # Carga inicial de datos (refresca KPIs y filas de la tabla)
        self._actualizar_tabla()

    # ========================================================================
    # CABECERA
    # ========================================================================

    def _construir_cabecera(self):
        """Barra superior: Título · Buscador · Avatar."""
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(14, 6))

        # Título
        ctk.CTkLabel(
            header, text="Panel de Control",
            font=("Segoe UI", 22, "bold"), text_color="#111111"
        ).pack(side="left")

        # Avatar Administrador (derecha)
        avatar_cont = ctk.CTkFrame(header, fg_color="transparent")
        avatar_cont.pack(side="right")

        ctk.CTkLabel(
            avatar_cont, text="Administrador",
            font=("Segoe UI", 12), text_color="#888888"
        ).pack(side="right", padx=(6, 0))

        avatar = ctk.CTkFrame(avatar_cont, width=34, height=34, fg_color="#3F8FA9", corner_radius=17)
        avatar.pack(side="right")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="A", font=("Segoe UI", 13, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

        # Buscador (entre título y avatar)
        search_box = ctk.CTkFrame(
            header,
            fg_color="#F5FAFE",
            corner_radius=14,
            border_color="#000000",
            border_width=1,
            height=36,
            width=240
        )
        search_box.pack(side="right", padx=(0, 14))
        search_box.pack_propagate(False)

        ctk.CTkLabel(search_box, text="🔍", font=("Segoe UI Emoji", 11), text_color="#555555").pack(side="left", padx=(8, 2))

        self.txt_buscar = ctk.CTkEntry(
            search_box,
            placeholder_text="Buscar por placa o cliente...",
            font=("Segoe UI", 11),
            fg_color="transparent",
            text_color="#111111",
            border_width=0,
            height=28
        )
        self.txt_buscar.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.txt_buscar.bind("<KeyRelease>", lambda _e: self._filtrar())

    # ========================================================================
    # TARJETAS KPI
    # ========================================================================

    def _construir_kpis(self):
        """Construye las 4 tarjetas KPI guardando referencias a sus labels."""
        en_proceso, finalizados, ingresos_txt, pendientes = self._calcular_kpis()

        contenedor = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        contenedor.pack(fill="x", pady=(4, 10))
        for c in range(4):
            contenedor.grid_columnconfigure(c, weight=1, uniform="kpi")

        kpi_defs = [
            # (clave, titulo, valor_inicial, icono, color_icono, bg_icono, bg_card, color_texto)
            ("en_proceso",      "Vehículos en Proceso",    str(en_proceso),  "🚘", "#3F8FA9", "#D9F0F9", "#FFFFFF",  "#111111"),
            ("finalizados_hoy", "Lavados Finalizados Hoy", str(finalizados), "✓",  "#3F8FA9", "#FFFFFF",  "#3F8FA9",  "#FFFFFF"),
            ("ingresos_dia",    "Ingresos del Día",        ingresos_txt,     "$",  "#0B4F66", "#A2EDA2", "#FFFFFF",  "#111111"),
            ("pendientes",      "Servicios Pendientes",    str(pendientes),  "⏱",  "#FFFFFF", "#F68B2E",  "#FFFFFF",  "#111111"),
        ]

        self._kpi_labels = {}

        for col, (clave, titulo, valor, icono, color_icono, bg_icono, bg_card, color_txt) in enumerate(kpi_defs):
            card = ctk.CTkFrame(
                contenedor, fg_color=bg_card, corner_radius=14,
                border_color="#CCE5F0", border_width=1, height=84
            )
            card.grid(row=0, column=col, padx=5, pady=3, sticky="nsew")
            card.pack_propagate(False)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=8)

            ctk.CTkLabel(
                inner, text=titulo,
                font=("Segoe UI", 10),
                text_color="#D0EEF8" if bg_card == "#3F8FA9" else "#666666",
                anchor="w"
            ).pack(fill="x")

            fila_inf = ctk.CTkFrame(inner, fg_color="transparent")
            fila_inf.pack(fill="x", expand=True, pady=(2, 0))

            fuente_val = ("Segoe UI", 16, "bold") if len(valor) > 5 else ("Segoe UI", 22, "bold")
            lbl_val = ctk.CTkLabel(
                fila_inf, text=valor,
                font=fuente_val, text_color=color_txt, anchor="w"
            )
            lbl_val.pack(side="left", anchor="s")
            self._kpi_labels[clave] = lbl_val

            badge = ctk.CTkFrame(fila_inf, width=28, height=28, fg_color=bg_icono, corner_radius=14)
            badge.pack(side="right", anchor="s")
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=icono, font=("Segoe UI", 11, "bold"), text_color=color_icono).place(relx=0.5, rely=0.5, anchor="center")

    def _actualizar_kpis(self):
        """Actualiza dinámicamente los valores de las 4 tarjetas KPI usando DashboardLogica."""
        kpis = DashboardLogica.obtener_kpis()
        valores = {
            "en_proceso": str(kpis.get("en_proceso", 0)),
            "finalizados_hoy": str(kpis.get("finalizados_hoy", 0)),
            "ingresos_dia": str(kpis.get("ingresos_dia", "$0")),
            "pendientes": str(kpis.get("pendientes", 0)),
        }
        for clave, valor in valores.items():
            lbl = self._kpi_labels.get(clave)
            if lbl:
                fuente = ("Segoe UI", 16, "bold") if len(valor) > 5 else ("Segoe UI", 22, "bold")
                lbl.configure(text=valor, font=fuente)

    def _calcular_kpis(self):
        """Consulta métricas a través de DashboardLogica (sin tocar datos/ directamente)."""
        kpis = DashboardLogica.obtener_kpis()
        return (
            kpis.get("en_proceso", 0),
            kpis.get("finalizados_hoy", 0),
            kpis.get("ingresos_dia", "$0"),
            kpis.get("pendientes", 0)
        )

    # ========================================================================
    # TABLA DE VEHÍCULOS EN SERVICIO ACTIVO
    # ========================================================================

    def _construir_tabla(self):
        """Crea la tarjeta contenedora de la tabla."""
        self.card_tabla = ctk.CTkFrame(
            self.scroll_body, fg_color="#F5FAFE",
            corner_radius=14, border_color="#CCE5F0", border_width=1
        )
        self.card_tabla.pack(fill="both", expand=True, pady=(0, 6))

        head = ctk.CTkFrame(self.card_tabla, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            head, text="Vehículos en Servicio Activo",
            font=("Segoe UI", 16), text_color="#555555"
        ).pack(side="left")

        def iniciar_recepcion():
            if self.al_ir_servicios:
                self.al_ir_servicios()
            elif self.al_ir_clientes:
                self.al_ir_clientes()

        btn_actualizar = ctk.CTkButton(
            head, text="🔄 Actualizar",
            width=90, height=28, corner_radius=8,
            fg_color="#D9F0F9", hover_color="#B8E2F2",
            text_color="#0B4F66", font=("Segoe UI", 10, "bold"),
            command=self._actualizar_tabla
        )
        btn_actualizar.pack(side="right")

        btn_nueva_orden = ctk.CTkButton(
            head,
            text="+ Nueva Orden / Recepción",
            fg_color="#F68B2E",
            hover_color="#F79D4F",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            height=28,
            corner_radius=8,
            command=iniciar_recepcion
        )
        btn_nueva_orden.pack(side="right", padx=(0, 8))

        self.tabla_frame = ctk.CTkFrame(self.card_tabla, fg_color="transparent")
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _cargar_filas_bd(self):
        """Obtiene las filas de servicio activo usando DashboardLogica."""
        return DashboardLogica.obtener_filas_servicio_activo()

    def _actualizar_tabla(self):
        """Recarga KPIs y filas de servicio activo, y repinta la tabla."""
        self._actualizar_kpis()
        self._todos_vehiculos = self._cargar_filas_bd()
        self._filtrar()

    def _filtrar(self):
        """Filtra la lista según el texto del buscador y repinta."""
        query = self.txt_buscar.get().strip().lower()
        if query:
            visibles = [
                v for v in self._todos_vehiculos
                if query in str(v.get("placa", "")).lower() or query in str(v.get("cliente", "")).lower()
            ]
        else:
            visibles = self._todos_vehiculos
        self._renderizar_tabla(visibles)

    def _renderizar_tabla(self, filas):
        """Dibuja cabecera y filas de datos; muestra mensaje si no hay registros."""
        # Limpiar tabla previa
        for w in self.tabla_frame.winfo_children():
            w.destroy()

        columnas = ["Placa", "Cliente", "Tipo de Vehículo", "Servicio", "Estado", "Tiempo", "Acciones"]
        pesos    = [10, 17, 13, 20, 13, 8, 19]

        for i, p in enumerate(pesos):
            self.tabla_frame.grid_columnconfigure(i, weight=p)

        # — Cabecera —
        head_row = ctk.CTkFrame(self.tabla_frame, fg_color="#C8E9F2", corner_radius=8, height=34)
        head_row.pack(fill="x", pady=(0, 4))
        for i, p in enumerate(pesos):
            head_row.grid_columnconfigure(i, weight=p)
        for i, col in enumerate(columnas):
            ctk.CTkLabel(
                head_row, text=col,
                font=("Segoe UI", 11), text_color="#555555", anchor="w"
            ).grid(row=0, column=i, padx=8, pady=6, sticky="w")

        # — Sin datos —
        if not filas:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay vehículos en servicio registrados.",
                font=("Segoe UI", 12), text_color="#888888"
            ).pack(pady=20)
            return

        # Colores de badges de estado
        badge_colores = {
            "En Proceso": ("#85CDE5", "#1E1E1E"),
            "Completado": ("#A2EDA2", "#1E1E1E"),
            "En Espera":  ("#FFECAF", "#1E1E1E"),
        }

        for i, v in enumerate(filas):
            fila = ctk.CTkFrame(
                self.tabla_frame,
                fg_color="#F8FAFC" if i % 2 == 0 else "#FFFFFF",
                corner_radius=8, height=44
            )
            fila.pack(fill="x", pady=1)
            for j, p in enumerate(pesos):
                fila.grid_columnconfigure(j, weight=p)

            # Placa
            ctk.CTkLabel(fila, text=v.get("placa", "—"), font=("Segoe UI", 12, "bold"), text_color="#111111", anchor="w").grid(row=0, column=0, padx=8, pady=9, sticky="w")
            # Cliente
            ctk.CTkLabel(fila, text=v.get("cliente", "—"), font=("Segoe UI", 12), text_color="#222222", anchor="w").grid(row=0, column=1, padx=8, pady=9, sticky="w")
            # Tipo
            ctk.CTkLabel(fila, text=v.get("tipo", "—"), font=("Segoe UI", 11), text_color="#555555", anchor="w").grid(row=0, column=2, padx=8, pady=9, sticky="w")
            # Servicio
            ctk.CTkLabel(fila, text=v.get("servicio", "—"), font=("Segoe UI", 11), text_color="#111111", anchor="w").grid(row=0, column=3, padx=8, pady=9, sticky="w")

            # Estado (badge)
            estado_txt = v.get("estado", "—")
            bg_b, fg_b = badge_colores.get(estado_txt, ("#E2E8F0", "#333333"))
            badge_f = ctk.CTkFrame(fila, fg_color=bg_b, corner_radius=12, height=24)
            badge_f.grid(row=0, column=4, padx=8, pady=9, sticky="w")
            ctk.CTkLabel(badge_f, text=f"  {estado_txt}  ", font=("Segoe UI", 10), text_color=fg_b).pack(padx=2, pady=1)

            # Tiempo
            ctk.CTkLabel(fila, text=v.get("tiempo", "—"), font=("Segoe UI", 11), text_color="#333333", anchor="w").grid(row=0, column=5, padx=8, pady=9, sticky="w")

            # Acciones
            acciones_f = ctk.CTkFrame(fila, fg_color="transparent")
            acciones_f.grid(row=0, column=6, padx=4, pady=6, sticky="w")
            orden_id = v.get("id")

            for item in v.get("acciones", []):
                if len(item) == 3:
                    etiqueta, clave, es_danger = item
                elif len(item) == 2:
                    etiqueta, es_danger = item
                    clave = etiqueta.lower()
                else:
                    continue

                ctk.CTkButton(
                    acciones_f,
                    text=f"[{etiqueta}]",
                    font=("Segoe UI", 10, "bold"),
                    fg_color="transparent",
                    hover_color="#EDF7FB",
                    text_color="#F16262" if es_danger else "#0B4F66",
                    width=60, height=24,
                    command=lambda oid=orden_id, act=clave: self._ejecutar_accion(oid, act)
                ).pack(side="left", padx=2)

    # ========================================================================
    # MANEJO DE ACCIONES Y MODALES
    # ========================================================================

    def _ejecutar_accion(self, orden_id, clave):
        """Manejador central para las acciones de cada fila."""
        clave = (clave or "").lower()
        if clave in ("iniciar", "finalizar", "entregar"):
            self._accion_avanzar_estado(orden_id)
        elif clave == "facturar":
            self._modal_facturar(orden_id)
        elif clave == "recibo":
            self._accion_ver_recibo(orden_id)
        elif clave == "editar":
            if self.al_ir_servicios:
                self.al_ir_servicios()

    def _manejador_accion(self, etiqueta):
        """Mantiene compatibilidad con versiones previas."""
        if etiqueta in ("Editar", "Iniciar", "Finalizar", "Cancelar"):
            return self.al_ir_servicios if self.al_ir_servicios else lambda: None
        if etiqueta in ("Ver Recibo", "Recibo"):
            return self.al_ir_facturas or self.al_ir_facturacion or (lambda: None)
        return lambda: None

    def _accion_avanzar_estado(self, orden_id):
        """Avanza el estado de la orden; si requiere empleado, abre modal para asignarlo."""
        try:
            requiere_emp = DashboardLogica.orden_requiere_empleado(orden_id)
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo consultar la orden:\n{err}")
            return

        if requiere_emp:
            empleados = DashboardLogica.listar_empleados_activos()
            if not empleados:
                messagebox.showwarning(
                    "Empleado requerido",
                    "Esta orden requiere asignar un empleado responsable, pero no hay empleados activos registrados.\n\n"
                    "Por favor registre un empleado primero en el módulo de Empleados."
                )
                return
            self._modal_asignar_empleado(orden_id, empleados)
        else:
            try:
                DashboardLogica.avanzar_orden(orden_id)
                self._actualizar_tabla()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo avanzar la orden:\n{err}")

    def _modal_asignar_empleado(self, orden_id, empleados):
        """Modal para elegir empleado responsable cuando una orden no lo tiene."""
        modal = ctk.CTkToplevel(self)
        modal.title("Asignar Empleado")
        modal.configure(fg_color="#F5FAFE")
        modal.resizable(False, False)

        ancho, alto = 400, 230
        self._centrar_modal(modal, ancho, alto)

        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        cont = ctk.CTkFrame(modal, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(
            cont,
            text=f"Asignar Empleado - Orden #{orden_id}",
            font=("Segoe UI", 14, "bold"),
            text_color="#0B4F66"
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            cont,
            text="Seleccione el empleado responsable para continuar con el servicio:",
            font=("Segoe UI", 11),
            text_color="#555555",
            wraplength=350,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        opciones = [f"{emp_id} - {emp_nombre}" for emp_id, emp_nombre in empleados]
        combo_empleado = ctk.CTkComboBox(
            cont,
            values=opciones,
            state="readonly",
            height=32,
            corner_radius=8,
            border_color="#3F8FA9",
            button_color="#3F8FA9",
            button_hover_color="#336E84",
            dropdown_hover_color="#E7F9FF"
        )
        combo_empleado.set(opciones[0])
        combo_empleado.pack(fill="x", pady=(0, 18))

        btn_row = ctk.CTkFrame(cont, fg_color="transparent")
        btn_row.pack(fill="x")

        def confirmar():
            seleccion = combo_empleado.get()
            try:
                emp_id = int(seleccion.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Selección de empleado inválida.", parent=modal)
                return

            try:
                DashboardLogica.avanzar_orden(orden_id, empleado_id=emp_id)
                modal.destroy()
                self._actualizar_tabla()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo avanzar la orden:\n{err}", parent=modal)

        ctk.CTkButton(
            btn_row,
            text="Cancelar",
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#333333",
            font=("Segoe UI", 11, "bold"),
            width=90,
            height=32,
            corner_radius=8,
            command=modal.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Confirmar",
            fg_color="#0B4F66",
            hover_color="#336E84",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            width=110,
            height=32,
            corner_radius=8,
            command=confirmar
        ).pack(side="right")

    def _modal_facturar(self, orden_id):
        """Modal de facturación rápida con selección de método de pago y apertura de PDF."""
        modal = ctk.CTkToplevel(self)
        modal.title("Facturar Orden")
        modal.configure(fg_color="#F5FAFE")
        modal.resizable(False, False)

        ancho, alto = 430, 240
        self._centrar_modal(modal, ancho, alto)

        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        cont = ctk.CTkFrame(modal, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(
            cont,
            text=f"Facturación Rápida - Orden #{orden_id}",
            font=("Segoe UI", 14, "bold"),
            text_color="#0B4F66"
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            cont,
            text="Seleccione el método de pago para emitir la factura:",
            font=("Segoe UI", 11),
            text_color="#555555"
        ).pack(anchor="w", pady=(0, 10))

        metodos = ["Efectivo", "Tarjeta", "Transferencia"]
        combo_metodo = ctk.CTkComboBox(
            cont,
            values=metodos,
            state="readonly",
            height=32,
            corner_radius=8,
            border_color="#3F8FA9",
            button_color="#3F8FA9",
            button_hover_color="#336E84",
            dropdown_hover_color="#E7F9FF"
        )
        combo_metodo.set(metodos[0])
        combo_metodo.pack(fill="x", pady=(0, 18))

        def facturar():
            metodo = combo_metodo.get().strip().lower()
            try:
                FacturacionLogica.generar_factura(orden_id, metodo)
            except Exception as err:
                messagebox.showerror("Error de Facturación", f"No se pudo generar la factura:\n{err}", parent=modal)
                return

            modal.destroy()
            self._actualizar_tabla()

            try:
                ruta_pdf = DashboardLogica.generar_recibo_pdf(orden_id)
                self._abrir_pdf(ruta_pdf)
            except Exception as err:
                messagebox.showinfo(
                    "Factura Emitida",
                    f"La factura de la orden #{orden_id} se generó exitosamente, pero ocurrió un problema al generar o abrir el PDF:\n{err}"
                )

        btn_row = ctk.CTkFrame(cont, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row,
            text="Cancelar",
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#333333",
            font=("Segoe UI", 11, "bold"),
            width=80,
            height=32,
            corner_radius=8,
            command=modal.destroy
        ).pack(side="left")

        if self.al_ir_facturacion:
            def ir_a_facturacion():
                modal.destroy()
                self.al_ir_facturacion()

            ctk.CTkButton(
                btn_row,
                text="Ir a Facturación",
                fg_color="transparent",
                hover_color="#EDF7FB",
                text_color="#0B4F66",
                border_width=1,
                border_color="#0B4F66",
                font=("Segoe UI", 11),
                width=120,
                height=32,
                corner_radius=8,
                command=ir_a_facturacion
            ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row,
            text="Facturar y PDF",
            fg_color="#0B4F66",
            hover_color="#336E84",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            width=120,
            height=32,
            corner_radius=8,
            command=facturar
        ).pack(side="right")

    def _accion_ver_recibo(self, orden_id):
        """Genera y abre el recibo PDF de la orden."""
        try:
            ruta_pdf = DashboardLogica.generar_recibo_pdf(orden_id)
            self._abrir_pdf(ruta_pdf)
        except Exception as err:
            messagebox.showinfo("Aviso", f"No se pudo abrir el recibo:\n{err}")

    def _abrir_pdf(self, ruta_pdf):
        """Abre el archivo PDF automáticamente según el sistema operativo."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta_pdf)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", ruta_pdf], check=True)
            else:
                subprocess.run(["xdg-open", ruta_pdf], check=True)
        except Exception as err:
            messagebox.showinfo(
                "Recibo PDF",
                f"El archivo se guardó en:\n{ruta_pdf}\n\n(No se pudo abrir automáticamente: {err})"
            )

    def _centrar_modal(self, modal, ancho, alto):
        """Centra una ventana modal respecto a la ventana principal."""
        modal.update_idletasks()
        try:
            root = self.winfo_toplevel()
            root_x = root.winfo_rootx()
            root_y = root.winfo_rooty()
            root_w = root.winfo_width()
            root_h = root.winfo_height()
            x = root_x + (root_w // 2) - (ancho // 2)
            y = root_y + (root_h // 2) - (alto // 2)
        except Exception:
            screen_w = modal.winfo_screenwidth()
            screen_h = modal.winfo_screenheight()
            x = (screen_w // 2) - (ancho // 2)
            y = (screen_h // 2) - (alto // 2)

        modal.geometry(f"{ancho}x{alto}+{max(0, x)}+{max(0, y)}")
