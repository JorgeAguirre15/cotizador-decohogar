import streamlit as st
import json
import math
import os
from PIL import Image

@st.cache_data
def cargar_productos():
    with open("productos.json", "r", encoding="utf-8") as f:
        return json.load(f)

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

# Interfaz
st.set_page_config(page_title="Cotizador Decohogar", layout="wide")
st.title("🛒 Cotizador Decohogar")

productos = cargar_productos()
nombres_productos = [p["name"] for p in productos]

with st.sidebar:
    st.header("📋 Parámetros de cotización")
    productos_seleccionados = st.multiselect("Selecciona productos", nombres_productos)
    plazo_elegido = st.selectbox("Plazo elegido por el cliente (semanas)", [1, 4, 8, 12, 16])
    inicial = st.number_input("Inicial ($)", min_value=0.0, value=0.0, step=10.0)
    descuento = st.slider("Descuento aplicado (%)", 0, 100, 0)

# Resultado por plazo del cliente
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

    # Mostrar imágenes de productos seleccionados
    st.subheader("🖼️ Productos seleccionados")
    columnas = st.columns(len(resumen))

    for i, (_, _, _, _, imagen) in enumerate(resumen):
        if imagen and os.path.exists(imagen):
            with columnas[i]:
                st.image(imagen, width=180)
        else:
            with columnas[i]:
                st.warning("Imagen no disponible")

    # Tabla consolidada por otros plazos
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

else:
    st.info("Selecciona productos desde la barra lateral para comenzar.")
