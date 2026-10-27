"""
scripts/sembrar_datos_demo.py
Script para poblar la base de datos con datos de demostración realistas
para AutoWash System.

Reglas del proyecto:
- Usa las clases públicas de la capa logica/ para insertar y transicionar datos.
- Excepción permitida: Se usa obtener_conexion() directamente para actualizar
  las columnas fecha_hora de órdenes, movimientos de inventario y facturas, ya
  que la capa lógica fija siempre datetime.now().
- Reproducible mediante random.Random(42).
- Medidas de seguridad (--yes para omitir confirmación, --forzar para BD con clientes).
"""
import os
import sys
import argparse
import random
from datetime import datetime, timedelta, time

# Asegurar que la raíz del proyecto esté en sys.path
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from db.conexion import obtener_ruta_db, obtener_conexion, inicializar_db
from logica.clientes_logica import ClientesLogica
from logica.vehiculos_logica import VehiculosLogica
from logica.empleados_logica import EmpleadosLogica
from logica.servicios_logica import ServiciosLogica
from logica.inventario_logica import InventarioLogica
from logica.facturacion_logica import FacturacionLogica


def sembrar_datos(forzar=False, interactivo=True):
    """
    Función principal de siembra de datos demo.
    """
    ruta_db = obtener_ruta_db()
    print(f"[DEMO] Base de datos objetivo: {ruta_db}")

    # Asegurar tablas inicializadas
    inicializar_db()

    # Verificación de seguridad: abortar si ya tiene clientes
    clientes_existentes = ClientesLogica.listar_todos_los_clientes()
    if clientes_existentes and not forzar:
        print(f"[ALERTA] La base de datos ya contiene {len(clientes_existentes)} clientes.")
        print("Operación cancelada para evitar sobreescribir datos reales. Use --forzar si desea continuar.")
        return False

    if interactivo:
        confirmacion = input(f"¿Desea sembrar datos de prueba en '{ruta_db}'? (s/n): ").strip().lower()
        if confirmacion not in ("s", "si", "y", "yes"):
            print("Operación cancelada por el usuario.")
            return False

    rng = random.Random(42)

    # 1. Carga masiva inicial de inventario para evitar problemas de stock
    print("[1/5] Aprovisionando stock inicial de insumos...")
    insumos = InventarioLogica.listar_insumos()
    for insumo in insumos:
        InventarioLogica.registrar_entrada(
            insumo["id"],
            cantidad=10000,
            motivo="Carga inicial masiva para entorno de demostración"
        )

    # 2. Empleados
    print("[2/5] Registrando empleados...")
    nombres_empleados = [
        "Luis Alfonso Patiño",
        "Yeison Alexander Cárdenas",
        "Jhon Fredy Quintero"
    ]
    empleado_ids = []
    empleados_existentes = EmpleadosLogica.listar_empleados()
    if not empleados_existentes:
        for nombre in nombres_empleados:
            empleado_ids.append(EmpleadosLogica.registrar_empleado(nombre))
    else:
        empleado_ids = [e["id"] for e in empleados_existentes]

    # 3. Clientes (mínimo 8 con nombres colombianos y teléfonos con 3)
    print("[3/5] Registrando clientes...")
    datos_clientes = [
        ("Carlos Andrés Rodríguez", "3104567890"),
        ("María Fernanda Gómez", "3208765432"),
        ("Juan David Restrepo", "3156781234"),
        ("Diana Marcela Ospina", "3189012345"),
        ("Andrés Felipe Morales", "3001234567"),
        ("Valentina Betancur", "3123456789"),
        ("Santiago Jaramillo", "3178901234"),
        ("Camila Hernández", "3145678901"),
        ("Mateo Echeverri", "3167890123"),
        ("Paola Andrea Cañas", "3112345678"),
    ]
    cliente_ids = []
    for nombre, telefono in datos_clientes:
        cliente_ids.append(ClientesLogica.registrar_cliente(nombre, telefono))

    # 4. Vehículos (12 vehículos, placas únicas, tipos Automovil/Camioneta/Moto)
    print("[4/5] Registrando vehículos...")
    datos_vehiculos = [
        ("KLO789", "Automovil", "Mazda", "3"),
        ("UBX452", "Camioneta", "Toyota", "Hilux"),
        ("TRW890", "Moto", "Yamaha", "FZ25"),
        ("MNO123", "Automovil", "Chevrolet", "Onix"),
        ("FGH456", "Camioneta", "Renault", "Duster"),
        ("ZXC789", "Moto", "Bajaj", "Pulsar 200"),
        ("QWE321", "Automovil", "Kia", "Picanto"),
        ("ASD654", "Camioneta", "Ford", "Ranger"),
        ("JKL987", "Moto", "KTM", "Duke 390"),
        ("HJK234", "Automovil", "Volkswagen", "Gol"),
        ("VBN567", "Camioneta", "Nissan", "Frontier"),
        ("RTY891", "Automovil", "Hyundai", "i25"),
    ]
    vehiculo_ids = []
    for i, (placa, tipo, marca, modelo) in enumerate(datos_vehiculos):
        # Asignar a los clientes registrados rotativamente
        cliente_id = cliente_ids[i % len(cliente_ids)]
        vehiculo_ids.append(VehiculosLogica.registrar_vehiculo(placa, tipo, cliente_id, marca, modelo))

    # 5. Generar entre 60 y 90 órdenes repartidas en los últimos 45 días
    print("[5/5] Generando órdenes de servicio y facturación...")
    servicios = ServiciosLogica.listar_servicios()
    servicio_ids_disponibles = [s["id"] for s in servicios]

    hoy = datetime.now().date()
    total_ordenes = 75  # En el rango [60, 90]

    # Para garantizar que en los últimos 30 días haya más de 20 días con ventas:
    # Elegimos 24 días distintos en los últimos 30 días que tendrán al menos 1 orden que se factura.
    dias_ultimos_30 = list(range(30))
    dias_con_venta_garantizada = rng.sample(dias_ultimos_30, 24)

    # Resto de órdenes (75 - 24 = 51) se distribuyen con mayor peso viernes a domingo
    dias_pesados = []
    for offset in range(45):
        dia_fecha = hoy - timedelta(days=offset)
        # Viernes (4), Sábado (5), Domingo (6) tienen mayor peso
        peso = 4 if dia_fecha.weekday() in (4, 5, 6) else 1
        dias_pesados.extend([offset] * peso)

    ordenes_dias = dias_con_venta_garantizada + [rng.choice(dias_pesados) for _ in range(total_ordenes - len(dias_con_venta_garantizada))]
    # Ordenar cronológicamente (más antiguo primero)
    ordenes_dias.sort(reverse=True)

    lista_actualizaciones = []
    total_facturadas = 0

    for idx, offset_dias in enumerate(ordenes_dias):
        vehiculo_id = rng.choice(vehiculo_ids)
        empleado_id = rng.choice(empleado_ids)

        # Elegir 1 o 2 servicios
        cant_servicios = rng.choice([1, 1, 2])
        servicios_elegidos = rng.sample(servicio_ids_disponibles, k=cant_servicios)

        # Crear orden mediante la lógica pública
        orden_id = ServiciosLogica.asignar_servicios(vehiculo_id, servicios_elegidos, empleado_id)

        # Transición por los 4 estados hasta entregado
        ServiciosLogica.cambiar_estado_orden(orden_id, "proceso", empleado_id)
        ServiciosLogica.cambiar_estado_orden(orden_id, "terminado", empleado_id)
        ServiciosLogica.cambiar_estado_orden(orden_id, "entregado", empleado_id)

        # Facturar aproximadamente el 85%
        # Las primeras 24 (garantizadas para tener > 20 días de ventas en los últimos 30) se facturan seguro.
        debe_facturar = (idx < 24) or (rng.random() < 0.78)

        factura_id = None
        if debe_facturar:
            metodo_pago = rng.choice(FacturacionLogica.METODOS_PAGO)
            factura_id = FacturacionLogica.generar_factura(orden_id, metodo_pago)
            total_facturadas += 1

        # EXCEPCIÓN PERMITIDA:
        # Calcular fecha_hora retroactiva entre 08:00 y 18:00
        fecha_base = hoy - timedelta(days=offset_dias)

        hora_orden_val = rng.randint(8, 16)
        minuto_orden_val = rng.randint(0, 59)
        segundo_orden_val = rng.randint(0, 59)
        dt_orden = datetime.combine(
            fecha_base,
            time(hora_orden_val, minuto_orden_val, segundo_orden_val)
        )
        fecha_orden_str = dt_orden.strftime("%Y-%m-%d %H:%M:%S")

        fecha_factura_str = None
        if factura_id:
            minutos_servicio = rng.randint(20, 50)
            dt_factura = dt_orden + timedelta(minutes=minutos_servicio)
            if dt_factura.time() > time(18, 0, 0):
                dt_factura = datetime.combine(fecha_base, time(17, 59, rng.randint(0, 59)))
            fecha_factura_str = dt_factura.strftime("%Y-%m-%d %H:%M:%S")

        lista_actualizaciones.append((orden_id, factura_id, fecha_orden_str, fecha_factura_str))

    # EXCEPCIÓN PERMITIDA:
    # Como la lógica de negocio sella automáticamente fecha_hora = datetime.now(),
    # actualizamos directamente con SQL las fechas para simular el histórico
    # entre 08:00 y 18:00 en los últimos 45 días.
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        for orden_id, factura_id, f_orden, f_factura in lista_actualizaciones:
            cursor.execute(
                "UPDATE ordenes_servicio SET fecha_hora = ? WHERE id = ?",
                (f_orden, orden_id)
            )
            cursor.execute(
                "UPDATE movimientos_inventario SET fecha_hora = ? WHERE orden_id = ?",
                (f_orden, orden_id)
            )
            if factura_id and f_factura:
                cursor.execute(
                    "UPDATE facturas SET fecha_hora = ? WHERE id = ?",
                    (f_factura, factura_id)
                )
        conexion.commit()
    finally:
        conexion.close()

    pct_facturadas = (total_facturadas / total_ordenes) * 100
    print(f"\n[ÉXITO] Siembra completada con éxito.")
    print(f"- Clientes creados: {len(cliente_ids)}")
    print(f"- Vehículos creados: {len(vehiculo_ids)}")
    print(f"- Órdenes creadas: {total_ordenes}")
    print(f"- Facturas generadas: {total_facturadas} ({pct_facturadas:.1f}% de facturación)")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sembrar datos de prueba para AutoWash System")
    parser.add_argument("--yes", "-y", action="store_true", help="Omitir solicitud de confirmación interactiva")
    parser.add_argument("--forzar", "-f", action="store_true", help="Continuar aunque la BD ya tenga clientes")
    args = parser.parse_args()

    exito = sembrar_datos(forzar=args.forzar, interactivo=not args.yes)
    sys.exit(0 if exito else 1)
