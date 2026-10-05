"""
Generador de comprobante de pago (factura) en PDF para AutoWash System.

Se construye a partir del diccionario que devuelve
FacturacionLogica.obtener_factura(factura_id), el cual ya incluye:
id, orden_id, metodo_pago, total, fecha_hora, fecha_servicio, estado,
placa, nombre_cliente, telefono, nombre_empleado, detalle (lista de
{servicio_id, precio_aplicado, nombre_servicio}).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

NOMBRE_NEGOCIO = "AutoWash System"
DIRECCION_NEGOCIO = "Cúcuta, Norte de Santander"

NAVY = colors.HexColor("#1F3864")
GRAY = colors.HexColor("#595959")
LIGHTGRAY = colors.HexColor("#F2F2F2")


def generar_pdf_factura(factura, ruta_salida):
    """
    factura: dict devuelto por FacturacionLogica.obtener_factura(factura_id)
    ruta_salida: ruta completa donde se va a guardar el archivo .pdf
    """
    doc = SimpleDocTemplate(
        ruta_salida, pagesize=letter,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "TituloNegocio", parent=styles["Title"], textColor=NAVY, fontSize=20,
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo", parent=styles["Normal"], textColor=GRAY, fontSize=10,
    )
    etiqueta_style = ParagraphStyle(
        "Etiqueta", parent=styles["Normal"], fontSize=10, textColor=GRAY,
    )
    valor_style = ParagraphStyle(
        "Valor", parent=styles["Normal"], fontSize=11,
    )

    story = []

    # Encabezado
    story.append(Paragraph(NOMBRE_NEGOCIO, titulo_style))
    story.append(Paragraph(DIRECCION_NEGOCIO, subtitulo_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", color=NAVY, thickness=1.2))
    story.append(Spacer(1, 14))

    story.append(Paragraph(f"Comprobante de pago N.° {factura['id']}", styles["Heading2"]))
    story.append(Spacer(1, 10))

    # Datos de la factura y del cliente, en dos columnas
    datos_izq = [
        ["Fecha de emisión:", factura["fecha_hora"]],
        ["Fecha del servicio:", factura["fecha_servicio"]],
        ["Método de pago:", factura["metodo_pago"].capitalize()],
    ]
    datos_der = [
        ["Cliente:", factura["nombre_cliente"]],
        ["Teléfono:", factura.get("telefono") or "No registrado"],
        ["Placa del vehículo:", factura["placa"]],
    ]

    tabla_izq = Table(datos_izq, colWidths=[3.3 * cm, 4.8 * cm])
    tabla_der = Table(datos_der, colWidths=[3.3 * cm, 4.8 * cm])
    for t in (tabla_izq, tabla_der):
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

    tabla_contenedora = Table(
        [[tabla_izq, tabla_der]], colWidths=[8.1 * cm, 8.1 * cm]
    )
    story.append(tabla_contenedora)
    story.append(Spacer(1, 18))

    # Empleado responsable
    empleado = factura.get("nombre_empleado") or "No asignado"
    story.append(Paragraph(f"<b>Atendido por:</b> {empleado}", valor_style))
    story.append(Spacer(1, 16))

    # Detalle de servicios
    story.append(Paragraph("Detalle de servicios", styles["Heading3"]))
    story.append(Spacer(1, 6))

    filas_detalle = [["Servicio", "Precio aplicado"]]
    for item in factura["detalle"]:
        filas_detalle.append([
            item["nombre_servicio"],
            f"${item['precio_aplicado']:,.0f}",
        ])

    tabla_detalle = Table(filas_detalle, colWidths=[11 * cm, 5.2 * cm])
    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTGRAY]),
    ]))
    story.append(tabla_detalle)
    story.append(Spacer(1, 14))

    # Total
    tabla_total = Table(
        [["TOTAL A PAGAR", f"${factura['total']:,.0f}"]],
        colWidths=[11 * cm, 5.2 * cm],
    )
    tabla_total.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(tabla_total)
    story.append(Spacer(1, 24))

    story.append(HRFlowable(width="100%", color=colors.lightgrey, thickness=0.8))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Gracias por confiar en nosotros. Este comprobante es generado "
        "automáticamente por AutoWash System.",
        subtitulo_style,
    ))

    doc.build(story)
    return ruta_salida