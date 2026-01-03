from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generar_recibo(id_trabajo, fecha, nombre, tel, equipo, falla, estado, precio):
    # 1. Definir nombre de la carpeta y del archivo
    carpeta = "Comprobantes"
    nombre_archivo = f"Recibo_{id_trabajo}_{nombre.replace(' ', '_')}.pdf"

    # 2. Truco: Crear la carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # 3. Unir carpeta + nombre para saber la ruta completa
    # (Ej: "Comprobantes/Recibo_001_Juan.pdf")
    ruta_completa = os.path.join(carpeta, nombre_archivo)

    # Crear el lienzo en esa ruta específica
    c = canvas.Canvas(ruta_completa, pagesize=A4)
    width, height = A4

    # --- ENCABEZADO ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "MATI-FIX Service")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "Servicio Técnico Especializado de PC y Notebooks")
    c.drawString(50, height - 85, "Tel: (Tu Número Aquí) | Email: matias@matifix.com")

    c.line(50, height - 100, width - 50, height - 100)

    # --- DATOS ---
    y = height - 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"ORDEN DE SERVICIO N°: {id_trabajo:04d}")

    c.setFont("Helvetica", 12)
    c.drawString(400, y, f"Fecha: {fecha}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Datos del Cliente:")
    c.setFont("Helvetica", 12)
    c.drawString(200, y, f"{nombre}")

    y -= 20
    c.drawString(200, y, f"Tel: {tel}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Equipo / Modelo:")
    c.setFont("Helvetica", 12)
    c.drawString(200, y, f"{equipo}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Falla Declarada:")
    c.setFont("Helvetica", 12)
    c.drawString(200, y, f"{falla[:60]}")
    if len(falla) > 60:
        c.drawString(200, y - 20, f"{falla[60:120]}")

    y -= 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Estado Actual:")
    c.drawString(200, y, f"{estado}")

    # --- PRECIOS ---
    y -= 60
    c.line(50, y, width - 50, y)
    y -= 30
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PRECIO FINAL / PRESUPUESTO:")
    c.drawString(400, y, f"{precio}")

    # --- TERMINOS ---
    y -= 100
    c.setFont("Helvetica", 8)
    texto_garantia = [
        "CONDICIONES DE SERVICIO:",
        "1. La empresa no se responsabiliza por la pérdida de información.",
        "   Se recomienda realizar copias de seguridad antes de ingresar el equipo.",
        "2. Los presupuestos tienen una validez de 15 días.",
        "3. Pasados los 90 días, el equipo se considerará abandonado.",
        "4. La garantía de reparación es de 30 días sobre la mano de obra.",
    ]

    for linea in texto_garantia:
        c.drawString(50, y, linea)
        y -= 12

    # --- FIRMA ---
    y -= 50
    c.line(350, y, 500, y)
    c.drawString(380, y - 15, "Firma / Aceptación")

    c.save()

    # Abrir el archivo desde la nueva carpeta
    try:
        os.startfile(ruta_completa)
    except:
        pass
