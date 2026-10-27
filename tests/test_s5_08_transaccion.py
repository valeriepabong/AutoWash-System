"""
tests/test_s5_08_transaccion.py
Pruebas para la atomicidad en la creación de órdenes y descuento de insumos (S5-08).
"""
import unittest
from unittest.mock import patch

from tests.base import TestBaseAutoWash
from logica.clientes_logica import ClientesLogica
from logica.vehiculos_logica import VehiculosLogica
from logica.empleados_logica import EmpleadosLogica
from logica.servicios_logica import ServiciosLogica
from logica.inventario_logica import InventarioLogica
from datos.inventario_datos import InventarioDatos
from datos.ordenes_datos import OrdenesDatos
from db.conexion import obtener_conexion


class TestTransaccionOrdenInsumos(TestBaseAutoWash):

    def setUp(self):
        super().setUp()
        self.cliente_id = ClientesLogica.registrar_cliente("Laura Gomez", "3201112233")
        self.vehiculo_id = VehiculosLogica.registrar_vehiculo("XYZ789", "Automovil", self.cliente_id)
        self.empleado_id = EmpleadosLogica.registrar_empleado("Operario Prueba")

        # Usar "Lavado básico" que consume al menos 2 insumos: Shampoo (1L) y Agua (40L)
        servicios = ServiciosLogica.listar_servicios()
        self.servicio = next(s for s in servicios if s["nombre"] == "Lavado básico")
        
        # Verificar que la receta tenga al menos 2 insumos
        receta = InventarioLogica.listar_insumos_de_servicio(self.servicio["id"])
        self.assertGreaterEqual(
            len(receta), 2,
            "El servicio para la prueba debe requerir al menos 2 insumos para probar la atomicidad"
        )
        self.receta = receta

    def _contar_filas(self, tabla):
        con = obtener_conexion()
        c = con.cursor()
        c.execute(f"SELECT COUNT(*) FROM {tabla}")
        total = c.fetchone()[0]
        con.close()
        return total

    def test_falla_en_segundo_insumo_realiza_rollback_total(self):
        """
        Fuerza un error al descontar el segundo insumo y verifica:
        1) Se propaga la excepción.
        2) NO se crea ninguna orden de servicio ni detalle.
        3) El stock del primer insumo (y de todos) queda INTACTO (rollback).
        4) No queda ningún movimiento de inventario huérfano.
        """
        # Registrar estado inicial
        ordenes_antes = self._contar_filas("ordenes_servicio")
        detalles_antes = self._contar_filas("orden_servicio_detalle")
        movimientos_antes = self._contar_filas("movimientos_inventario")

        stocks_iniciales = {}
        for item in self.receta:
            insumo = InventarioDatos.obtener_insumo_por_id(item["insumo_id"])
            stocks_iniciales[item["insumo_id"]] = insumo["stock_actual"]

        # Parchear InventarioDatos.registrar_movimiento para fallar en la 2da llamada
        original_registrar = InventarioDatos.registrar_movimiento
        llamadas = 0

        def registrar_con_fallo(*args, **kwargs):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 2:
                raise RuntimeError("Fallo forzado en el segundo insumo para probar rollback")
            return original_registrar(*args, **kwargs)

        with patch.object(InventarioDatos, "registrar_movimiento", side_effect=registrar_con_fallo):
            with self.assertRaises(RuntimeError) as ctx:
                ServiciosLogica.asignar_servicios(
                    self.vehiculo_id, [self.servicio["id"]], self.empleado_id
                )
            self.assertIn("Fallo forzado en el segundo insumo", str(ctx.exception))

        self.assertGreaterEqual(llamadas, 2, "Debió intentar descontar al menos 2 insumos")

        # Verificaciones de ROLLBACK TOTAL:
        # 1. No se crearon órdenes
        ordenes_despues = self._contar_filas("ordenes_servicio")
        self.assertEqual(ordenes_despues, ordenes_antes, "No debe haberse creado ninguna orden de servicio")

        # 2. No se crearon detalles
        detalles_despues = self._contar_filas("orden_servicio_detalle")
        self.assertEqual(detalles_despues, detalles_antes, "No debe haberse creado ningún detalle de orden")

        # 3. No se crearon movimientos de inventario
        movimientos_despues = self._contar_filas("movimientos_inventario")
        self.assertEqual(movimientos_despues, movimientos_antes, "No deben quedar movimientos registrados")

        # 4. Los stocks quedaron exactamente intactos
        for item in self.receta:
            insumo_despues = InventarioDatos.obtener_insumo_por_id(item["insumo_id"])
            stock_esperado = stocks_iniciales[item["insumo_id"]]
            self.assertEqual(
                insumo_despues["stock_actual"], stock_esperado,
                f"El stock del insumo '{insumo_despues['nombre']}' debió quedar intacto"
            )

    def test_caso_feliz_transaccion_completa(self):
        """
        En un flujo normal sin errores, la orden, el detalle, los movimientos
        y la actualización de stock se persisten de manera consistente.
        """
        ordenes_antes = self._contar_filas("ordenes_servicio")
        stocks_iniciales = {}
        for item in self.receta:
            insumo = InventarioDatos.obtener_insumo_por_id(item["insumo_id"])
            stocks_iniciales[item["insumo_id"]] = insumo["stock_actual"]

        orden_id = ServiciosLogica.asignar_servicios(
            self.vehiculo_id, [self.servicio["id"]], self.empleado_id
        )
        self.assertIsNotNone(orden_id)

        # 1. La orden existe y tiene estado espera
        orden = OrdenesDatos.obtener_orden_por_id(orden_id)
        self.assertEqual(orden["estado"], "espera")
        self.assertEqual(orden["vehiculo_id"], self.vehiculo_id)

        # 2. El detalle fue guardado correctamente
        detalles = OrdenesDatos.obtener_detalle_de_orden(orden_id)
        self.assertEqual(len(detalles), 1)
        self.assertEqual(detalles[0]["servicio_id"], self.servicio["id"])

        # 3. El stock de cada insumo fue descontado según la receta
        for item in self.receta:
            insumo_despues = InventarioDatos.obtener_insumo_por_id(item["insumo_id"])
            consumo = item["cantidad_consumida"]
            self.assertEqual(
                insumo_despues["stock_actual"],
                stocks_iniciales[item["insumo_id"]] - consumo,
                f"El stock de '{insumo_despues['nombre']}' no se descontó correctamente"
            )

        # 4. Los movimientos_inventario quedaron asociados a la orden_id
        con = obtener_conexion()
        c = con.cursor()
        c.execute("SELECT COUNT(*) FROM movimientos_inventario WHERE orden_id = ?", (orden_id,))
        movs_orden = c.fetchone()[0]
        con.close()
        self.assertEqual(movs_orden, len(self.receta), "Cada insumo de la receta debe tener su movimiento")


if __name__ == "__main__":
    unittest.main()
