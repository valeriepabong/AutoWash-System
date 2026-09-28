from tkinter import messagebox, ttk
import customtkinter as ctk

from logica.servicios_logica import ServiciosLogica
from logica.vehiculos_logica import VehiculosLogica
from logica.empleados_logica import EmpleadosLogica


class ServiciosScreen(ctk.CTkFrame):
    def __init__(self, parent, al_volver=None):
        super().__init__(parent)
        self.al_volver = al_volver
       

        self.vehiculos_disponibles = []
        self.empleados_disponibles = []
        self.ordenes = {}  # id de orden -> datos de la orden
        self.checks = []  # lista de tuplas (servicio, variable del checkbox)

        self.pack(fill="both", expand=True, padx=20, pady=20)

        self._crear_interfaz()
        self._cargar_vehiculos()
        self._cargar_servicios()
        self._cargar_empleados()
        self._cargar_ordenes()

    # ---------- Interfaz ----------

    def _crear_interfaz(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Asignación de Servicios",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="Volver al Dashboard",
            fg_color="gray",
            hover_color="#505050",
            width=140,
            command=self.al_volver,
        ).pack(side="right")

        # Vehículo
        ctk.CTkLabel(self, text="Vehículo:", anchor="w").pack(fill="x", padx=40)
        self.combo_vehiculo = ctk.CTkOptionMenu(
            self, values=["Sin vehículos registrados"]
        )
        self.combo_vehiculo.pack(pady=(0, 8), fill="x", padx=40)

        # Servicios (checkboxes)
        ctk.CTkLabel(
            self, text="Servicios (marque uno o más):", anchor="w"
        ).pack(fill="x", padx=40)
        self.frame_servicios = ctk.CTkScrollableFrame(self, height=100)
        self.frame_servicios.pack(pady=(0, 5), fill="x", padx=40)

        # Empleado responsable
        ctk.CTkLabel(self, text="Empleado responsable:", anchor="w").pack(
            fill="x", padx=40
        )
        self.combo_empleado = ctk.CTkOptionMenu(
            self, values=["Sin empleados registrados"]
        )
        self.combo_empleado.pack(pady=(0, 8), fill="x", padx=40)

        # Total + botón asignar
        fila_total = ctk.CTkFrame(self, fg_color="transparent")
        fila_total.pack(fill="x", padx=40, pady=5)

        self.label_total = ctk.CTkLabel(
            fila_total,
            text="Total: $0",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.label_total.pack(side="left")

        ctk.CTkButton(
            fila_total,
            text="Asignar Servicios",
            command=self._evento_asignar,
            fg_color="green",
        ).pack(side="right")

        # Órdenes en curso
        ctk.CTkLabel(
            self,
            text="Órdenes en curso",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 0))

        columnas = ("id", "placa", "empleado", "estado", "total")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=5)

        self.tabla.heading("id", text="Orden")
        self.tabla.heading("placa", text="Placa")
        self.tabla.heading("empleado", text="Empleado")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("total", text="Total")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("placa", width=90, anchor="center")
        self.tabla.column("empleado", width=140, anchor="center")
        self.tabla.column("estado", width=100, anchor="center")
        self.tabla.column("total", width=100, anchor="center")

        self.tabla.pack(pady=5, fill="both", expand=True, padx=20)

        ctk.CTkButton(
            self,
            text="Avanzar Orden al Siguiente Estado",
            command=self._evento_avanzar,
            fg_color="#1f538d",
        ).pack(pady=5)

    # ---------- Carga de datos ----------

    def _cargar_vehiculos(self):
        self.vehiculos_disponibles = VehiculosLogica.obtener_vehiculos()

        if not self.vehiculos_disponibles:
            self.combo_vehiculo.configure(values=["Sin vehículos registrados"])
            self.combo_vehiculo.set("Sin vehículos registrados")
            return

        opciones = [
            f"{v['id']} - {v['placa']} ({v['nombre_cliente']})"
            for v in self.vehiculos_disponibles
        ]
        self.combo_vehiculo.configure(values=opciones)
        self.combo_vehiculo.set(opciones[0])

    def _cargar_servicios(self):
        for servicio in ServiciosLogica.listar_servicios():
            variable = ctk.IntVar(value=0)
            ctk.CTkCheckBox(
                self.frame_servicios,
                text=f"{servicio['nombre']} - ${servicio['precio']:,.0f}",
                variable=variable,
                onvalue=1,
                offvalue=0,
                command=self._actualizar_total,
            ).pack(anchor="w", pady=3, padx=5)
            self.checks.append((servicio, variable))

    def _cargar_empleados(self):
        self.empleados_disponibles = EmpleadosLogica.listar_empleados()

        if not self.empleados_disponibles:
            self.combo_empleado.configure(values=["Sin empleados registrados"])
            self.combo_empleado.set("Sin empleados registrados")
            return

        opciones = [f"{e['id']} - {e['nombre']}" for e in self.empleados_disponibles]
        self.combo_empleado.configure(values=opciones)
        self.combo_empleado.set(opciones[0])

    def _cargar_ordenes(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.ordenes = {}
        for orden in ServiciosLogica.listar_ordenes():
            # Las entregadas ya terminaron su ciclo: no se muestran aquí
            if orden["estado"] == "entregado":
                continue
            self.ordenes[orden["id"]] = orden
            self.tabla.insert(
                "", "end",
                values=(
                    orden["id"],
                    orden["placa"],
                    orden["nombre_empleado"] or "Sin asignar",
                    orden["estado"].capitalize(),
                    f"${orden['total']:,.0f}",
                ),
            )

    # ---------- Utilidades ----------

    def _actualizar_total(self):
        total = sum(s["precio"] for s, var in self.checks if var.get() == 1)
        self.label_total.configure(text=f"Total: ${total:,.0f}")

    def _limpiar_seleccion(self):
        for _, variable in self.checks:
            variable.set(0)
        self._actualizar_total()

    def _obtener_vehiculo_id(self):
        if not self.vehiculos_disponibles:
            return None
        return int(self.combo_vehiculo.get().split(" - ")[0])

    def _obtener_empleado_id(self):
        if not self.empleados_disponibles:
            return None
        return int(self.combo_empleado.get().split(" - ")[0])

    # ---------- Eventos ----------

    def _evento_asignar(self):
        vehiculo_id = self._obtener_vehiculo_id()
        if vehiculo_id is None:
            messagebox.showerror(
                "Error", "Debe registrar al menos un vehículo antes de asignar servicios."
            )
            return

        servicio_ids = [s["id"] for s, var in self.checks if var.get() == 1]

        try:
            orden_id = ServiciosLogica.asignar_servicios(
                vehiculo_id, servicio_ids, empleado_id=self._obtener_empleado_id()
            )
            messagebox.showinfo(
                "Éxito", f"Orden #{orden_id} creada en estado 'Espera'."
            )
            self._limpiar_seleccion()
            self._cargar_ordenes()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))

    def _evento_avanzar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Por favor seleccione una orden de la tabla."
            )
            return

        orden_id = int(self.tabla.item(seleccion[0])["values"][0])
        orden = self.ordenes[orden_id]

        siguiente = ServiciosLogica.siguiente_estado(orden["estado"])
        if siguiente is None:
            messagebox.showinfo("Atención", "Esta orden ya fue entregada.")
            return

        # Si la orden no tiene empleado, se usa el elegido en el desplegable
        empleado_id = None
        if orden["empleado_id"] is None:
            empleado_id = self._obtener_empleado_id()

        try:
            ServiciosLogica.cambiar_estado_orden(
                orden_id, siguiente, empleado_id=empleado_id
            )
            messagebox.showinfo(
                "Éxito", f"Orden #{orden_id} pasó a '{siguiente.capitalize()}'."
            )
            self._cargar_ordenes()
        except ValueError as err:
            messagebox.showerror("Error", str(err))