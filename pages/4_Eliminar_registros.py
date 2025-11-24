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
    return ["TODOS"] + [row["nombre"] for row in (resp.data or [])]

def cargar_clientes():
    resp = supabase.table("catalogo_clientes").select("nombre").execute()
    return [row["nombre"] for row in (resp.data or [])]

# ============================================================
# UI PRINCIPAL
# ============================================================
st.title("📆 Eliminar registros")

# Selección de persona
PERSONAS = cargar_personas()
CLIENTES = cargar_clientes()

persona_sel = st.selectbox("👤 Usuario", PERSONAS)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def cargar_rangos(persona, cliente):
    query = supabase.table("BD_calendario_disponibilidad").select("*")

    if persona != "TODOS":
        query = query.eq("persona", persona)

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

# ============================================================
# MOSTRAR CLIENTE + RANGOS
# ============================================================
for cliente in CLIENTES:


    df = cargar_rangos(persona_sel, cliente)
    rangos_df = generar_rangos(df)

    st.subheader(f"🏢 {cliente}")
    
    if rangos_df.empty:
        continue

    # Mostrar cada rango con su botón eliminar
    for idx, row in rangos_df.iterrows():
        inicio = row["inicio"].date()
        fin = row["fin"].date()

        col1, col2 = st.columns([3,1])
        col1.write(f"📅 **{inicio} → {fin}**")

        if col2.button("❌ Eliminar", key=f"del_{cliente}_{idx}"):
            supabase.table("BD_calendario_disponibilidad") \
                .delete() \
                .gte("fecha", str(inicio)) \
                .lte("fecha", str(fin)) \
                .execute()

            st.success("✅ Rango eliminado correctamente.")
            st.rerun()

    st.markdown("---")
