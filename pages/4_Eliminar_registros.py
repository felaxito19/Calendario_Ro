import streamlit as st
from datetime import date, timedelta
from supabase import create_client, Client
import pandas as pd

# ============================================================
# CONECTAR A SUPABASE
# ============================================================
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase: Client = init_supabase()

#==============================================================
# CARGAR CATÁLOGOS
#==============================================================
def cargar_personas():
    resp = supabase.table("catalogo_personas").select("nombre").execute()
    return [row["nombre"] for row in (resp.data or [])]

def cargar_clientes():
    resp = supabase.table("catalogo_clientes").select("nombre").execute()
    return [row["nombre"] for row in (resp.data or [])]

# ============================================================
# ESTADOS INICIALES
# ============================================================
if "post_guardado" not in st.session_state:
    st.session_state.post_guardado = False

if "default_persona" not in st.session_state:
    st.session_state.default_persona = None

if "default_cliente" not in st.session_state:
    st.session_state.default_cliente = None

if "default_rango" not in st.session_state:
    st.session_state.default_rango = None

# ============================================================
# UI PRINCIPAL
# ============================================================
st.title("📆 Eliminar registros")

# Personas y clientes con opción TODOS
PERSONAS = ["TODOS"] + cargar_personas()
CLIENTES = cargar_clientes()

persona_sel = st.selectbox(
    "👤 Usuario",
    PERSONAS,
    key="persona_input"
)


# Generemos una lista de rangos existentes
def cargar_rangos(persona, cliente):
    query = supabase.table("BD_calendario_disponibilidad").select("*")

    if persona != "TODOS":
        query = query.eq("persona", persona)

    if cliente != "TODOS":
        query = query.eq("cliente", cliente)

    resp = query.execute()
    df = pd.DataFrame(resp.data)
    return df

def generar_rangos(df):
    if df.empty:
        return pd.DataFrame(columns=["inicio", "fin"])

    df = df.sort_values("fecha")
    df["fecha"] = pd.to_datetime(df["fecha"])

    rangos = []
    inicio = df["fecha"].iloc[0]
    fin = inicio

    for fecha in df["fecha"].iloc[1:]:
        if fecha == fin + pd.Timedelta(days=1):
            fin = fecha
        else:
            rangos.append({"inicio": inicio, "fin": fin})
            inicio = fecha
            fin = fecha

    rangos.append({"inicio": inicio, "fin": fin})
    return pd.DataFrame(rangos)


rangos = cargar_rangos(persona_sel, "TODOS")
rangos_general = generar_rangos(rangos)


if not rangos_general.empty:

    for cliente in CLIENTES:
        rangos_df = generar_rangos(cargar_rangos(persona_sel,cliente)
        rangos_df["label"] = rangos_df["inicio"].dt.date.astype(str) + " → " + rangos_df["fin"].dt.date.astype(str)
        
        rango_sel = st.selectbox("🗑️ Seleccionar rango a eliminar", rangos_df["label"])

        if st.button("❌ Eliminar rango"):
            inicio_str = rango_sel.split(" → ")[0]
            fin_str = rango_sel.split(" → ")[1]
    
            # Borrar todas las fechas dentro del rango
            supabase.table("BD_calendario_disponibilidad") \
                .delete() \
                .gte("fecha", inicio_str) \
                .lte("fecha", fin_str) \
                .execute()
    
            st.success("✅ Rango eliminado correctamente.")
            st.rerun()












