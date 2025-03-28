import streamlit as st
import json
import math
import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import base64

# === Cargar productos ===
@st.cache_data
def cargar_productos():
    with open("productos.json", "r", encoding="utf-8") as f:
        return json.load(f)

# === Factor de precio según plazo y monto ===
def obtener_factor_precio(precio, plazo):
    if plazo == 1 and precio <= 50:
        return 1.7
    elif plazo == 1 and precio <= 100:
        return 1.4
    elif plazo == 1 and precio <= 250:
        return 1.3
    elif plazo == 1 and precio <= 500:
        return 1.25
    elif plazo == 1 and precio > 500:
        return 1.2
    elif 2 <= plazo <= 7 and precio <= 50:
        return 1.9
    elif 2 <= plazo <= 7 and precio <= 100:
        return 1.55
    elif 2 <= plazo <= 7 and precio <= 250:
        return 1.55
    elif 2 <= plazo <= 7 and precio <= 500:
        return 1.5
    elif 2 <= plazo <= 7 and precio > 500:
        return 1.5
    elif 8 <= plazo <= 11 and precio <= 50:
        return 2.1
    elif 8 <= plazo <= 11 and precio <= 100:
        return 1.75
    elif 8 <= plazo <= 11 and precio <= 250:
        return 1.75
    elif 8 <= plazo <= 11 and precio <= 500:
        return 1.7
    elif 8 <= plazo <= 11 and precio > 500:
        return 1.7
    elif 12 <= plazo <= 15 and precio <= 50:
        return 2.3
    elif 12 <= plazo <= 15 and precio <= 100:
        return 1.95
    elif 12 <= plazo <= 15 and precio <= 250:
        return 1.95
    elif 12 <= plazo <= 15 and precio <= 500:
        return 1.9
    elif 12 <= plazo <= 15 and precio > 500:
        return 1.9
    elif 16 <= plazo <= 19 and precio <= 50:
        return 2.5
    elif 16 <= plazo <= 19 and precio <= 100:
        return 2.25
    elif 16 <= plazo <= 19 and precio <= 250:
        return 2.25
    elif 16 <= plazo <= 19 and precio <= 500:
        return 2.2
    elif 16 <= plazo <= 19 and precio > 500:
        return 2.2

# === Generar PDF ===
def generar_pdf(nombre_cliente, productos, resumen_tabla, resumen_consolidado, inicial, descuento, plazo_cliente):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Cotización - {nombre_cliente}")

    y = 750
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Cotización para: {nombre_cliente}")
    y -= 25

    pdf.setFont("Helvetica", 12)
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.drawString(50, y, f"Fecha: {fecha_actual}")
    y -= 20
    pdf.drawString(50, y, f"Inicial aplicada: ${inicial:,.2f}")
    y -= 20
    pdf.drawString(50, y, f"Descuento aplicado: {descuento:.2f}%")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Resumen (Plazo elegido: {plazo_cliente} semanas)")
    y -= 20
    pdf.setFont("Helvetica", 10)
    for item in resumen_tabla:
        linea = f"{item['Producto']} | Total: {item['Valor total']} | Cuota: {item['Cuota semanal']}"
        pdf.drawString(50, y, linea)
        y -= 15
        if y < 100:
            pdf.showPage()
            y = 750

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Resumen por otros plazos:")
    y -= 20
    pdf.setFont("Helvetica", 10)
    for item in resumen_consolidado:
        linea = f"{item['Plazo']} | Total: {item['Valor total']} | Cuota total: {item['Cuota total']}"
        pdf.drawString(50, y, linea)
        y -= 15
        if y < 100:
            pdf.showPage()
            y = 750

    y -= 30
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, y, "* Cotización válida por 30 días.")
    pdf.drawString(50, y - 15, "* La última cuota puede ser inferior.")
    pdf.drawString(50, y - 30, "* Mejora tu hogar y tu vida con Decohogar.")

    pdf.save()
    buffer.seek(0)
    return buffer

# === Interfaz principal ===

st.set_page_config(page_title="Cotizador Decohogar", layout="wide")
st.title("🛒 Cotizador Decohogar")

productos = cargar_productos()
nombres_productos = [p["name"] for p in productos]

with st.sidebar:
    st.header("📋 Parámetros de cotización")

    productos_seleccionados = st.multiselect("Selecciona productos", nombres_productos)

    st.markdown("---")
    st.subheader("➕ Agregar producto personalizado")
    nombre_personalizado = st.text_input("Nombre del producto")
    precio_personalizado = st.number_input("Precio del producto ($)", min_value=0.0, step=10.0)

    if nombre_personalizado and precio_personalizado > 0:
        productos_seleccionados.append(nombre_personalizado)
        productos.append({"name": nombre_personalizado, "price": precio_personalizado, "image": ""})
        nombres_productos.append(nombre_personalizado)

    st.markdown("---")
    plazo_elegido = st.selectbox("Plazo elegido por el cliente (semanas)", [1, 4, 8, 12, 16])
    inicial = st.number_input("Inicial ($)", min_value=0.0, value=0.0, step=10.0)
    descuento = st.slider("Descuento aplicado (%)", 0, 100, 0)

# === Cotización ===

if productos_seleccionados:
    st.subheader("📌 Cotización con plazo elegido")

    total_general = 0
    resumen = []

    for nombre in productos_seleccionados:
        producto = next(p for p in productos if p["name"] == nombre)
        precio = producto["price"]
        precio_desc = precio * (1 - descuento / 100)
        factor = obtener_factor_precio(precio_desc, plazo_elegido)
        valor_total = math.ceil(precio_desc * factor)
        total_general += valor_total
        resumen.append((nombre, precio, precio_desc, valor_total, producto.get("image", "")))

    tabla_resultado = []

    for nombre, precio, precio_desc, valor_total, imagen in resumen:
        proporcion = valor_total / total_general if total_general > 0 else 0
        aporte_inicial = math.ceil(inicial * proporcion)
        cuota = math.ceil((valor_total - aporte_inicial) / plazo_elegido)

        tabla_resultado.append({
            "Producto": nombre,
            "Precio base": f"${precio:,.2f}",
            "Con descuento": f"${precio_desc:,.2f}",
            "Valor total": f"${valor_total:,}",
            "Inicial": f"${aporte_inicial:,}",
            "Cuota semanal": f"${cuota:,}"
        })

    st.table(tabla_resultado)

    st.subheader("🖼️ Productos seleccionados")
    columnas = st.columns(len(resumen))
    for i, (_, _, _, _, imagen) in enumerate(resumen):
        if imagen and os.path.exists(imagen):
            with columnas[i]:
                st.image(imagen, width=180)
        else:
            with columnas[i]:
                st.warning("Imagen no disponible")

    st.subheader("📊 Resumen por otros plazos")
    plazos_default = [1, 4, 8, 12, 16]
    consolidado = []

    for plazo in plazos_default:
        total_valor_plazo = 0
        total_cuota_plazo = 0

        for nombre in productos_seleccionados:
            producto = next(p for p in productos if p["name"] == nombre)
            precio = producto["price"]
            precio_desc = precio * (1 - descuento / 100)
            factor = obtener_factor_precio(precio_desc, plazo)
            valor = math.ceil(precio_desc * factor)
            total_valor_plazo += valor

        for nombre in productos_seleccionados:
            producto = next(p for p in productos if p["name"] == nombre)
            precio = producto["price"]
            precio_desc = precio * (1 - descuento / 100)
            factor = obtener_factor_precio(precio_desc, plazo)
            valor = math.ceil(precio_desc * factor)
            proporcion = valor / total_valor_plazo if total_valor_plazo > 0 else 0
            inicial_aportado = math.ceil(inicial * proporcion)
            cuota = math.ceil((valor - inicial_aportado) / plazo)
            total_cuota_plazo += cuota

        consolidado.append({
            "Plazo": f"{plazo} semanas",
            "Valor total": f"${total_valor_plazo:,}",
            "Cuota total": f"${total_cuota_plazo:,}"
        })

    st.table(consolidado)

    # === PDF ===
    st.markdown("### 🧾 Generar PDF")
    nombre_cliente = st.text_input("Nombre del cliente")

    if st.button("Guardar cotización en PDF"):
        if not nombre_cliente.strip():
            st.warning("Por favor, escribe el nombre del cliente.")
        else:
            pdf_buffer = generar_pdf(
                nombre_cliente,
                productos_seleccionados,
                tabla_resultado,
                consolidado,
                inicial,
                descuento,
                plazo_elegido
            )
            b64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Cotizacion_{nombre_cliente}.pdf">📥 Descargar PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("Selecciona productos desde la barra lateral para comenzar.")
