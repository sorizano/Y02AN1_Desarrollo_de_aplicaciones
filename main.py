import os
import pandas as pd
import streamlit as st
from datetime import datetime
from supabase import create_client

# ------------------------------------------
# Conexión a supabase
# ------------------------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ALLOWED_CATEGORIES = [
    "Chocolates", "Caramelos", "Mashmelos", "Galletas", "Salados", "Gomas de mascar"
]

# ------------------------------------------
# Funciones CRUD
# ------------------------------------------

def sb_list() -> pd.DataFrame:
    res = supabase.table("products").select("*").order("ts", desc=True).execute()
    return pd.DataFrame(res.data or [])

def sb_insert(nombre: str, precio:float, categorias: list, en_venta: bool):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta,
        "ts": datetime.utcnow().isoformat()
    }
    supabase.table("products").insert(payload).execute()

def sb_update(id_:int, nombre: str, precio: float, categorias: list, en_venta:bool ):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta,
    }
    supabase.table("products").update(payload).eq("id", id_).execute()

def sb_delete(id_: int):
    supabase.table("products").delete().eq("id", id_).execute()

def validar(nombre: str, precio:float, categorias: list[str]) -> str | None:
    if not nombre or len(nombre.strip()) == 0 or len(nombre.strip()) > 20:
        return "El nombre es obligatorio y debe de tener <= 20 caracteres."
    try:
        p = float(precio)
    except Exception:
        return "Por favor verifique el campo precio."
    if not (0 < p < 999):
        return "El precio debe ser mayor a 0 y menor a 999"
    if not categorias:
        return "Debe elegir al menos una categoría"
    for c in categorias:
        if c not in ALLOWED_CATEGORIES:
            return f"Categoría inválida: {c}"
    return None

#------------------------------------- UI -----------------------------------

st.title("Confitería Dulcino - Registro de productos")

# ------- Crear Producto -------
st.header("Agregar Producto")
with st.form("form-add", clear_on_submit=True):
    nombre = st.text_input("Nombre de producto")
    precio = st.number_input("Precio (S/)", min_value=0.01, max_value=998.99, step=0.10)
    categorias = st.multiselect("Categorias", ALLOWED_CATEGORIES)
    en_venta = st.radio("¿En Venta?",["Sí","No"]) == "Sí"
    submitted = st.form_submit_button("Guardar")

if submitted:
    err = validar(nombre, precio, categorias)
    if err:
        if "precio" in err.lower():
            st.error("Por favor verifique el campo precio")
        else:
            st.error("Lo sentimos no pudo crear este producto")
        st.info(err)
    else:
        sb_insert(nombre.strip(), float(precio), categorias, en_venta)
        st.success("Felicidades su producto se agregó")
        st.rerun()
st.divider()

# ----------------- Listar / Editar / Borrar -----------------------

st.header("Productos registrados")
df = sb_list()
if df.empty:
    st.info("No hay productos aún.")
else:
    st.dataframe(df, use_container_width=True)

    #Seleccionar el producto
    opciones = {
        f"{r['nombre']} - {r['precio']}": r["id"] 
        for _, r in df.iterrows()
    }

    etiqueta = st.selectbox("Selecciona para editar/eliminar", list(opciones.keys()))
    producto_id = int(opciones[etiqueta])
    fila = df[df["id"]== producto_id].iloc[0]

    with st.form("form-edit"):
        c1, c2 = st.columns([2,1])
        with c1:
            ed_nombre = st.text_input("Nombre", value=fila["nombre"])
        with c2:
            ed_precio = st.number_input(
                "precio (S/)", value=float(fila["precio"]),
                min_value=0.0, max_value=998.99, step=0.10, format="%.2f"
            )
        ed_categorias = st.multiselect("Categorías", ALLOWED_CATEGORIES, default=fila["categorias"])
        ed_en_venta = st.radio("¿En venta?", ["Sí", "No"], index=0 if fila["en_venta"] else 1, horizontal=True) == "Sí"

        colu1, colu2 = st.columns(2)
        with colu1:
            btn_update = st.form_submit_button("Guardar Cambios")
        with colu2:
            btn_delete = st.form_submit_button("Eliminar", type="primary")

        if btn_update:
            err = validar(ed_nombre, ed_precio, ed_categorias)
            if err:
                if "precio" in err.lower():
                    st.error("Por favor verifique el campo precio.")
                else:
                    st.error("Lo sentimos no pudo actualizar este producto.")
                st.info(err)
            else:
                sb_update(producto_id, ed_nombre.strip(), float(ed_precio), ed_categorias, ed_en_venta)
                st.success("Producto Actualizado.")
                st.rerun()
        
        if btn_delete:
            sb_delete(producto_id)
            st.success("Producto Eliminado")
            st.rerun()