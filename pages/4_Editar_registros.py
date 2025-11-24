import streamlit as st
from datetime import date, timedelta
from supabase import create_client, Client

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

PERSONAS = cargar_personas()
CLIENTES = cargar_clientes()

# Usar valores por defecto si existen
persona_default = st.session_state.default_persona or PERSONAS[0]
cliente_default = st.session_state.default_cliente or CLIENTES[0]


persona_sel = st.selectbox("👤 Usuario", PERSONAS, key="persona_input",
                       index=PERSONAS.index(persona_default))

cliente_sel = st.selectbox("⛏️ Unidad Minera", CLIENTES, key="cliente_input",
                       index=CLIENTES.index(cliente_default))

# Generemos una lista de rangos existentes
def cargar_rangos(persona, cliente):
  resp = supabase.table("BD_calendario_disponibilidad") \
               .select("*") \
               .eq("persona", persona) \
               .eq("cliente", cliente) \
               .execute()
  df = pd.DataFrame(resp.data)

  return df

rangos = cargar_rangos(persona_sel, cliente_sel)

print(rangos)

# Mostramos la lista peo esta vez de RANGOS 


# --------------------

if not st.session_state.post_guardado:
    if st.button("💾 Guardar"):
        
        # caso SOLO un día
        if isinstance(rango, date):
            st.error("Por favor selecciona un rango de dos fechas.")
            st.stop()

        # caso rango válido
        inicio, fin = rango
        delta = fin - inicio

        for i in range(delta.days + 1):
            dia = inicio + timedelta(days=i)
            guardar_evento(persona, cliente, dia.isoformat())

        st.session_state.post_guardado = True
        st.rerun()



# ============================================================
# MENSAJE DE ÉXITO
# ============================================================
if st.session_state.post_guardado:

    st.success("✔ Registro guardado correctamente.")
    st.write("¿Qué deseas hacer ahora?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔁 Agregar otra actividad"):

            # Reset de defaults
            st.session_state.default_persona = PERSONAS[0]
            st.session_state.default_cliente = CLIENTES[0]
            st.session_state.default_rango = date.today()

            # Reset widgets
            for k in ["persona_input", "cliente_input", "rango_input"]:
                if k in st.session_state:
                    del st.session_state[k]

            st.session_state.post_guardado = False
            st.rerun()













