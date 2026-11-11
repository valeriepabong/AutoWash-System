import inspect
import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from tests.base import TestBaseAutoWash
import presentacion.dashboard_view as dv_mod
from presentacion.dashboard_view import DashboardView
from logica.dashboard_logica import DashboardLogica
from logica.facturacion_logica import FacturacionLogica


class TestDashboardView(TestBaseAutoWash):

    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.root.withdraw()
        self.mock_servicios = MagicMock()
        self.mock_facturas = MagicMock()
        self.mock_facturacion = MagicMock()
        self.view = DashboardView(
            self.root,
            al_ir_servicios=self.mock_servicios,
            al_ir_facturas=self.mock_facturas,
            al_ir_facturacion=self.mock_facturacion,
        )

    def tearDown(self):
        try:
            self.root.update()
            self.root.destroy()
        except Exception:
            pass
        super().tearDown()

    def test_arquitectura_sin_imports_de_datos(self):
        """Verifica estrictamente que presentacion/dashboard_view.py no importe datos/."""
        source = inspect.getsource(dv_mod)
        lines = source.splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertFalse(
                "datos." in stripped or "import datos" in stripped or "from datos" in stripped,
                f"dashboard_view.py importa la capa de datos en la línea {idx}: {line}"
            )
        self.assertIn("from logica.dashboard_logica import DashboardLogica", source)
        self.assertIn("from logica.facturacion_logica import FacturacionLogica", source)

    def test_kpis_labels_actualizados_dinamicamente(self):
        """Verifica que _actualizar_kpis refleje los datos de DashboardLogica.obtener_kpis."""
        mock_kpis = {
            "en_proceso": 7,
            "finalizados_hoy": 14,
            "ingresos_dia": "$350.000",
            "pendientes": 4,
        }
        with patch.object(DashboardLogica, "obtener_kpis", return_value=mock_kpis):
            self.view._actualizar_kpis()

            self.assertEqual(self.view._kpi_labels["en_proceso"].cget("text"), "7")
            self.assertEqual(self.view._kpi_labels["finalizados_hoy"].cget("text"), "14")
            self.assertEqual(self.view._kpi_labels["ingresos_dia"].cget("text"), "$350.000")
            self.assertEqual(self.view._kpi_labels["pendientes"].cget("text"), "4")

    def test_actualizar_tabla_refresca_kpis_y_filas(self):
        """_actualizar_tabla debe llamar a _actualizar_kpis, _cargar_filas_bd y _filtrar."""
        mock_filas = [
            {
                "id": 101,
                "placa": "XYZ123",
                "cliente": "Carlos Perez",
                "tipo": "Sedán",
                "servicio": "Lavado General",
                "estado": "En Proceso",
                "estado_bd": "proceso",
                "tiempo": "15 min",
                "empleado_id": 1,
                "acciones": [("Editar", "editar", False), ("Finalizar", "finalizar", False)],
            }
        ]
        with patch.object(self.view, "_actualizar_kpis") as mock_act_kpis, \
             patch.object(DashboardLogica, "obtener_filas_servicio_activo", return_value=mock_filas):
            self.view._actualizar_tabla()
            mock_act_kpis.assert_called_once()
            self.assertEqual(len(self.view._todos_vehiculos), 1)
            self.assertEqual(self.view._todos_vehiculos[0]["placa"], "XYZ123")

    def test_filtrar_por_placa_y_cliente(self):
        """_filtrar busca por coincidencia en placa o nombre de cliente."""
        self.view._todos_vehiculos = [
            {"id": 1, "placa": "ABC123", "cliente": "Juan Perez", "tipo": "Sedan", "servicio": "Basico", "estado": "En Proceso", "tiempo": "10 min", "acciones": []},
            {"id": 2, "placa": "XYZ789", "cliente": "Maria Gomez", "tipo": "SUV", "servicio": "Completo", "estado": "En Espera", "tiempo": "5 min", "acciones": []},
        ]
        with patch.object(self.view, "_renderizar_tabla") as mock_render:
            # Buscar por placa
            self.view.txt_buscar.delete(0, "end")
            self.view.txt_buscar.insert(0, "XYZ")
            self.view._filtrar()
            mock_render.assert_called_with([self.view._todos_vehiculos[1]])

            # Buscar por cliente
            self.view.txt_buscar.delete(0, "end")
            self.view.txt_buscar.insert(0, "juan")
            self.view._filtrar()
            mock_render.assert_called_with([self.view._todos_vehiculos[0]])

    def test_accion_editar_redirige_a_servicios(self):
        """La acción 'editar' ejecuta al_ir_servicios."""
        self.view._ejecutar_accion(1, "editar")
        self.mock_servicios.assert_called_once()

    def test_accion_avanzar_sin_empleado_requerido(self):
        """Si la orden ya tiene empleado asignado, avanza directamente con un clic."""
        with patch.object(DashboardLogica, "orden_requiere_empleado", return_value=False) as mock_req, \
             patch.object(DashboardLogica, "avanzar_orden") as mock_avanzar, \
             patch.object(self.view, "_actualizar_tabla") as mock_act:
            self.view._ejecutar_accion(42, "iniciar")
            mock_req.assert_called_once_with(42)
            mock_avanzar.assert_called_once_with(42)
            mock_act.assert_called_once()

    def test_accion_avanzar_requiere_empleado_sin_activos_muestra_advertencia(self):
        """Si requiere empleado pero no hay empleados activos, muestra warning."""
        with patch.object(DashboardLogica, "orden_requiere_empleado", return_value=True), \
             patch.object(DashboardLogica, "listar_empleados_activos", return_value=[]), \
             patch("presentacion.dashboard_view.messagebox.showwarning") as mock_warn:
            self.view._ejecutar_accion(42, "iniciar")
            mock_warn.assert_called_once()

    def test_accion_avanzar_requiere_empleado_abre_modal(self):
        """Si requiere empleado y hay empleados activos, abre el modal correspondiente."""
        empleados = [(1, "Pedro Lopez"), (2, "Ana Rios")]
        with patch.object(DashboardLogica, "orden_requiere_empleado", return_value=True), \
             patch.object(DashboardLogica, "listar_empleados_activos", return_value=empleados), \
             patch.object(self.view, "_modal_asignar_empleado") as mock_modal:
            self.view._ejecutar_accion(42, "iniciar")
            mock_modal.assert_called_once_with(42, empleados)

    def test_accion_ver_recibo_abre_pdf(self):
        """La acción 'recibo' genera el PDF y llama a _abrir_pdf."""
        with patch.object(DashboardLogica, "generar_recibo_pdf", return_value="/tmp/factura_1.pdf") as mock_gen, \
             patch.object(self.view, "_abrir_pdf") as mock_abrir:
            self.view._ejecutar_accion(15, "recibo")
            mock_gen.assert_called_once_with(15)
            mock_abrir.assert_called_once_with("/tmp/factura_1.pdf")

    def test_accion_facturar_abre_modal(self):
        """La acción 'facturar' abre el modal de facturación rápida."""
        with patch.object(self.view, "_modal_facturar") as mock_modal:
            self.view._ejecutar_accion(15, "facturar")
            mock_modal.assert_called_once_with(15)


if __name__ == "__main__":
    unittest.main()
