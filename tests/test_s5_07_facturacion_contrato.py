"""
tests/test_s5_07_facturacion_contrato.py
Pruebas para el contrato de facturación en la capa lógica (S5-07).
"""
import unittest

from tests.base import TestBaseAutoWash
from logica.clientes_logica import ClientesLogica
from logica.vehiculos_logica import VehiculosLogica
from logica.empleados_logica import EmpleadosLogica
from logica.servicios_logica import ServiciosLogica
from logica.facturacion_logica import FacturacionLogica


class TestFacturacionContrato(TestBaseAutoWash):

    def setUp(self):
        super().setUp()
        # Registrar cliente, vehículo y empleado
        self.cliente_id = ClientesLogica.registrar_cliente("Carlos Perez", "3001234567")
        self.vehiculo_id = VehiculosLogica.registrar_vehiculo("ABC123", "Automovil", self.cliente_id)
        self.empleado_id = EmpleadosLogica.registrar_empleado("Juan Empleado")
        
        # Obtener un servicio del catálogo por defecto
        servicios = ServiciosLogica.listar_servicios()
        self.assertTrue(len(servicios) > 0, "Debe existir al menos un servicio")
        self.servicio = servicios[0]

    def _crear_orden_entregada(self):
        orden_id = ServiciosLogica.asignar_servicios(
            self.vehiculo_id, [self.servicio["id"]], self.empleado_id
        )
        ServiciosLogica.cambiar_estado_orden(orden_id, "proceso", self.empleado_id)
        ServiciosLogica.cambiar_estado_orden(orden_id, "terminado", self.empleado_id)
        ServiciosLogica.cambiar_estado_orden(orden_id, "entregado", self.empleado_id)
        return orden_id

    def test_orden_entregada_aparece_en_por_facturar(self):
        """Una orden entregada sin factura debe aparecer en listar_ordenes_por_facturar()."""
        orden_id = self._crear_orden_entregada()
        por_facturar = FacturacionLogica.listar_ordenes_por_facturar()
        ids = [o["id"] for o in por_facturar]
        self.assertIn(orden_id, ids)
        
        # Verificar claves requeridas
        orden_info = next(o for o in por_facturar if o["id"] == orden_id)
        claves_esperadas = {"id", "vehiculo_id", "placa", "nombre_cliente", "fecha_hora", "total", "estado"}
        for clave in claves_esperadas:
            self.assertIn(clave, orden_info)
        self.assertEqual(orden_info["placa"], "ABC123")
        self.assertEqual(orden_info["nombre_cliente"], "Carlos Perez")
        self.assertEqual(orden_info["estado"], "entregado")

    def test_orden_no_entregada_no_aparece(self):
        """Una orden que no esté en estado 'entregado' no debe aparecer en listar_ordenes_por_facturar()."""
        orden_id = ServiciosLogica.asignar_servicios(
            self.vehiculo_id, [self.servicio["id"]], self.empleado_id
        )
        # Sigue en estado 'espera'
        por_facturar = FacturacionLogica.listar_ordenes_por_facturar()
        ids = [o["id"] for o in por_facturar]
        self.assertNotIn(orden_id, ids)

        # Avanzamos a 'proceso'
        ServiciosLogica.cambiar_estado_orden(orden_id, "proceso", self.empleado_id)
        por_facturar = FacturacionLogica.listar_ordenes_por_facturar()
        ids = [o["id"] for o in por_facturar]
        self.assertNotIn(orden_id, ids)

        # Avanzamos a 'terminado'
        ServiciosLogica.cambiar_estado_orden(orden_id, "terminado", self.empleado_id)
        por_facturar = FacturacionLogica.listar_ordenes_por_facturar()
        ids = [o["id"] for o in por_facturar]
        self.assertNotIn(orden_id, ids)

    def test_orden_facturada_desaparece_de_por_facturar(self):
        """Al facturar una orden entregada, esta debe desaparecer de listar_ordenes_por_facturar()."""
        orden_id = self._crear_orden_entregada()
        self.assertIn(orden_id, [o["id"] for o in FacturacionLogica.listar_ordenes_por_facturar()])

        # Generar factura
        factura_id = FacturacionLogica.generar_factura(orden_id, "efectivo")
        self.assertIsNotNone(factura_id)

        # Ya no debe aparecer
        por_facturar = FacturacionLogica.listar_ordenes_por_facturar()
        self.assertNotIn(orden_id, [o["id"] for o in por_facturar])

    def test_obtener_detalle_orden_exitoso(self):
        """obtener_detalle_orden devuelve el detalle con las claves correctas."""
        orden_id = self._crear_orden_entregada()
        detalle = FacturacionLogica.obtener_detalle_orden(orden_id)
        self.assertIsInstance(detalle, list)
        self.assertGreaterEqual(len(detalle), 1)

        item = detalle[0]
        self.assertIn("servicio_id", item)
        self.assertIn("precio_aplicado", item)
        self.assertIn("nombre_servicio", item)
        self.assertEqual(item["servicio_id"], self.servicio["id"])
        self.assertEqual(item["nombre_servicio"], self.servicio["nombre"])
        self.assertEqual(float(item["precio_aplicado"]), float(self.servicio["precio"]))

    def test_obtener_detalle_orden_inexistente_lanza_value_error(self):
        """Una orden inexistente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            FacturacionLogica.obtener_detalle_orden(99999)
        self.assertEqual(str(ctx.exception), "La orden de servicio no existe.")


if __name__ == "__main__":
    unittest.main()
