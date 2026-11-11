import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from tests.base import TestBaseAutoWash
from presentacion.clientes_screen import ClientesScreen
from presentacion.vehiculos_screen import VehiculosScreen
from presentacion.inventario_screen import InventarioScreen
from presentacion.reportes_screen import ReportesScreen
from logica.inventario_logica import InventarioLogica
from logica.reportes_logica import ReportesLogica


class TestFlujoEInventario(TestBaseAutoWash):

    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.update()
            self.root.destroy()
        except Exception:
            pass
        super().tearDown()

    def test_clientes_screen_flujo_vehiculos(self):
        """ClientesScreen debe incluir y ejecutar el callback al_ir_vehiculos."""
        mock_ir_vehiculos = MagicMock()
        mock_volver = MagicMock()
        screen = ClientesScreen(
            self.root,
            al_volver=mock_volver,
            al_ir_vehiculos=mock_ir_vehiculos
        )
        self.assertIsNotNone(screen.al_ir_vehiculos)
        screen.al_ir_vehiculos()
        mock_ir_vehiculos.assert_called_once()

    def test_vehiculos_screen_flujo_servicios_y_clientes(self):
        """VehiculosScreen debe aceptar al_ir_servicios y al_ir_clientes y ejecutarlos."""
        mock_ir_servicios = MagicMock()
        mock_ir_clientes = MagicMock()
        mock_volver = MagicMock()
        screen = VehiculosScreen(
            self.root,
            al_volver=mock_volver,
            al_ir_servicios=mock_ir_servicios,
            al_ir_clientes=mock_ir_clientes
        )
        self.assertIsNotNone(screen.al_ir_servicios)
        self.assertIsNotNone(screen.al_ir_clientes)
        screen.al_ir_servicios()
        mock_ir_servicios.assert_called_once()
        screen.al_ir_clientes()
        mock_ir_clientes.assert_called_once()

    def test_inventario_screen_creacion_y_entrada_stock(self):
        """InventarioScreen debe instanciarse, permitir crear insumo y registrar entrada de stock."""
        mock_volver = MagicMock()
        screen = InventarioScreen(self.root, al_volver=mock_volver)

        # 1. Crear insumo
        screen.entry_nombre.insert(0, "Cera Sintética")
        screen.combo_unidad.set("litros")
        screen.entry_stock_inicial.insert(0, "15")
        screen.entry_stock_minimo.insert(0, "5")

        with patch("presentacion.inventario_screen.messagebox.showinfo"):
            screen._evento_crear_insumo()

        insumos = InventarioLogica.listar_insumos()
        ins_creado = next((i for i in insumos if i["nombre"] == "Cera Sintética"), None)
        self.assertIsNotNone(ins_creado)
        self.assertEqual(ins_creado["stock_actual"], 15.0)

        # 2. Registrar entrada de stock
        screen.combo_insumo_entrada.set(f"{ins_creado['id']} - {ins_creado['nombre']}")
        screen.entry_cantidad_entrada.insert(0, "10")
        screen.entry_motivo_entrada.insert(0, "Factura compra #102")

        with patch("presentacion.inventario_screen.messagebox.showinfo"):
            screen._evento_registrar_entrada()

        insumos_act = InventarioLogica.listar_insumos()
        ins_actualizado = next(i for i in insumos_act if i["id"] == ins_creado["id"])
        self.assertEqual(ins_actualizado["stock_actual"], 25.0)

        # 3. Movimientos registrados
        movs = InventarioLogica.listar_movimientos(ins_creado["id"])
        self.assertGreaterEqual(len(movs), 2)  # Carga inicial + Entrada

    def test_reportes_screen_muestra_tabla_filas(self):
        """ReportesScreen debe poblar la tabla_ingresos con las filas del reporte de ingresos."""
        mock_reporte = {
            "rango": {"desde": "2026-11-01", "hasta": "2026-11-03"},
            "filas": [
                {"fecha": "2026-11-01", "cantidad_facturas": 3, "total_ingresos": 150000, "total_ingresos_texto": "$150.000"},
                {"fecha": "2026-11-02", "cantidad_facturas": 2, "total_ingresos": 90000, "total_ingresos_texto": "$90.000"},
            ],
            "resumen": {
                "total_ingresos": 240000,
                "total_ingresos_texto": "$240.000",
                "cantidad_facturas": 5,
                "promedio_por_factura": 48000,
                "promedio_por_factura_texto": "$48.000",
            },
            "grafica": {"etiquetas": ["2026-11-01", "2026-11-02"], "valores": [150000, 90000]},
        }

        with patch.object(ReportesLogica, "reporte_ingresos", return_value=mock_reporte):
            screen = ReportesScreen(self.root)
            filas_tabla = screen.tabla_ingresos.get_children()
            self.assertEqual(len(filas_tabla), 2)
            valores_primera_fila = screen.tabla_ingresos.item(filas_tabla[0])["values"]
            self.assertEqual(valores_primera_fila[0], "2026-11-01")
            self.assertEqual(valores_primera_fila[1], 3)
            self.assertEqual(valores_primera_fila[2], "$150.000")

    def test_navegacion_completa_main_app(self):
        """Verifica que todas las vistas de AplicacionPrincipal se instancien y naveguen sin TypeError."""
        from main import AplicacionPrincipal
        app = AplicacionPrincipal()
        app.withdraw()
        try:
            metodos = [
                app.mostrar_dashboard,
                app.mostrar_clientes,
                app.mostrar_vehiculos,
                app.mostrar_servicios,
                app.mostrar_empleados,
                app.mostrar_inventario,
                app.mostrar_facturacion,
                app.mostrar_reportes,
                app.mostrar_catalogo,
                app.mostrar_facturas,
                app.mostrar_login,
            ]
            for metodo in metodos:
                metodo()
                self.assertIsNotNone(app.vista_actual)
        finally:
            try:
                app.update()
                app.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
