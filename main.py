import os
import pandas as pd
import streamlit as st
from datetime import datetime
from supabase import create_client

# ------------------------------------------
# Conexión a supabase
# ------------------------------------------

SUPABASE_URL = os.environ.get("https://ondncxfrkzerxndpzvjz.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9uZG5jeGZya3plcnhuZHB6dmp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE3NDU3NzksImV4cCI6MjA1NzMyMTc3OX0.i-CknD56TkjtSzTW8gp4Ulr0VldY28nL1J-FBHG8uyc")

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