import streamlit as st
import pandas as pd
from supabase import create_client, Client
from streamlit_calendar import calendar
import json

# ------------------------------------------------------
# INIT
# ------------------------------------------------------
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase: Client = init_supabase()

st.set_page_config(page_title="Calendario", layout="wide")
st.title("📆 Calendario de disponibilidad")

# ------------------------------------------------------
# DATA REAL
# ------------------------------------------------------
def cargar_eventos():
    response = (
        supabase.table("BD_calendario_disponibilidad")
        .select("*")
        .order("fecha")
        .execute()
    )
    data = response.data
    if not data:
        return pd.DataFrame(columns=["persona", "cliente", "fecha", "tipo"])
    return pd.DataFrame(data)

df = cargar_eventos()

# Lista simple
data = list(df[["persona", "cliente", "fecha"]].itertuples(index=False, name=None))

usuarios = sorted(set([u for (u, c, f) in data]))
clientes = sorted(set([c for (u, c, f) in data]))


# ------------------------------------------------------
# FILTROS
# ------------------------------------------------------
usuario_filtro = st.selectbox("👤 Filtrar por persona", ["TODOS"] + usuarios)
cliente_filtro = st.selectbox("🏢 Filtrar por cliente", ["TODOS"] + clientes)


# ------------------------------------------------------
# EVENTOS
# ------------------------------------------------------
def color_unico(nombre):
    return f"#{abs(hash(nombre)) % 0xFFFFFF:06x}"

eventos = []
for usuario, cliente, fecha in data:

    if usuario_filtro != "TODOS" and usuario != usuario_filtro:
        continue

    if cliente_filtro != "TODOS" and cliente != cliente_filtro:
        continue

    eventos.append({
        "title": usuario,
        "start": fecha,
        "color": color_unico(usuario),
        "extendedProps": {
            "cliente": cliente
        }
    })

# ------------------------------------------------------
# RENDER
# ------------------------------------------------------
options = {
    "initialView": "dayGridMonth",
    "locale": "es",
    "height": "auto",
    "expandRows": True,
    "headerToolbar": {
        "left": "prev",
        "center": "title",
        "right": "next"
    },
}

response = calendar(events=eventos, options=options)



