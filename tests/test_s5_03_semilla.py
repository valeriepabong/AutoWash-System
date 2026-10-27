"""
tests/test_s5_03_semilla.py
Pruebas para el script de sembrado de datos de demostración (S5-03).
"""
import unittest

from tests.base import TestBaseAutoWash
from scripts.sembrar_datos_demo import sembrar_datos
from logica.reportes_logica import ReportesLogica
from logica.clientes_logica import ClientesLogica


class TestSembradoDatosDemo(TestBaseAutoWash):

    def test_siembra_y_reportes_demo(self):
        """
        Verifica que la siembra se complete exitosamente sobre una base limpia y que
        los reportes cumplan con los criterios especificados:
        - reporte_ingresos de los últimos 30 días devuelve más de 20 días con ventas.
        - suma de ingresos por servicio de reporte_servicios_mas_solicitados coincide
          con el total de ingresos de reporte_ingresos.
        - reporte_consumo_insumos devuelve filas de consumo.
        """
        # Ejecutar siembra sin interactividad y forzar en caso necesario
        exito = sembrar_datos(forzar=True, interactivo=False)
        self.assertTrue(exito, "La siembra de datos debe completarse con éxito")

        # 1. Reporte de ingresos de los últimos 30 días
        rep_ingresos = ReportesLogica.reporte_ingresos()
        filas_ingresos = rep_ingresos["filas"]
        total_ingresos = rep_ingresos["resumen"]["total_ingresos"]

        # Criterio: más de 20 días con ventas
        self.assertGreater(
            len(filas_ingresos), 20,
            f"Se esperaban más de 20 días con ventas, se obtuvieron {len(filas_ingresos)}"
        )
        self.assertGreater(total_ingresos, 0, "El total de ingresos debe ser mayor a cero")

        # Rango consultado
        desde = rep_ingresos["rango"]["desde"]
        hasta = rep_ingresos["rango"]["hasta"]

        # 2. Reporte de servicios más solicitados
        rep_servicios = ReportesLogica.reporte_servicios_mas_solicitados(desde, hasta)
        filas_servicios = rep_servicios["filas"]
        self.assertGreater(len(filas_servicios), 0, "Debe haber servicios vendidos")

        suma_ingresos_servicios = sum(f["ingreso_generado"] for f in filas_servicios)
        self.assertAlmostEqual(
            suma_ingresos_servicios, total_ingresos, places=2,
            msg="La suma de ingresos por servicio debe coincidir exactamente con el total de ingresos"
        )

        # 3. Reporte de consumo de insumos
        rep_insumos = ReportesLogica.reporte_consumo_insumos(desde, hasta)
        filas_insumos = rep_insumos["filas"]
        self.assertGreater(len(filas_insumos), 0, "El reporte de consumo de insumos debe devolver filas")
        for f in filas_insumos:
            self.assertGreater(f["cantidad_consumida"], 0, "El consumo de insumos debe ser mayor a cero")

    def test_seguridad_no_sobrescribe_sin_forzar(self):
        """Si la BD ya contiene clientes, sembrar_datos sin forzar debe abortar."""
        # Insertar un cliente previo
        ClientesLogica.registrar_cliente("Cliente Preexistente", "3000000000")
        
        # Intentar sembrar sin --forzar ni confirmación interactiva
        exito = sembrar_datos(forzar=False, interactivo=False)
        self.assertFalse(exito, "Debe rechazar la siembra si ya hay clientes y no se pasa forzar=True")


if __name__ == "__main__":
    unittest.main()
