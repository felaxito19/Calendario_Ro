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
# CARGAMOS INFORMACIÓN NECESARIA - (funciones)
#==============================================================

def cargar_personas():
    resp = supabase.table("catalogo_personas").select("nombre").execute()
    data = resp.data or []
    return [row["nombre"] for row in data]

def cargar_clientes():
    resp = supabase.table("catalogo_clientes").select("nombre").execute()
    data = resp.data or []
    return [row["nombre"] for row in data]

# ============================================================
# GUARDAR EVENTO EN SUPABASE
# ============================================================
def guardar_evento(persona, cliente, fecha, tipo):
    data = {
        "persona": persona,
        "cliente": cliente,
        "fecha": fecha,
        "tipo": tipo
    }
    supabase.table("BD_calendario_disponibilidad").insert(data).execute()

# ============================================================
# ESTADO GLOBAL PARA SABER SI SE GUARDÓ
# ============================================================
if "post_guardado" not in st.session_state:
    st.session_state.post_guardado = False

# ============================================================
# UI PRINCIPAL (FORMULARIO)
# ============================================================
st.title("📆 Registrar disponibilidad")

PERSONAS = cargar_personas()
CLIENTES = cargar_clientes()

# Ingreso de información del periodo de tiempo
persona = st.selectbox("👤 Nombre del empleado", PERSONAS)
cliente = st.selectbox("🏢 Cliente", CLIENTES)

# Selección de rango
rango = st.date_input("📅 Seleccionar rango de fechas", [])

if st.button("💾 Guardar"):

    # caso SOLO un día (date)
    if isinstance(rango, date):
        guardar_evento(persona, cliente, rango.isoformat(), tipo)
        st.session_state.post_guardado = True
        st.rerun()

    # caso rango (tuple)
    elif isinstance(rango, tuple) and len(rango) == 2:
        inicio, fin = rango

        # si el usuario pone fin < inicio, no guardar
        if fin < inicio:
            st.error("La fecha final no puede ser menor que la inicial.")
            st.stop()

        delta = fin - inicio
        for i in range(delta.days + 1):
            dia = inicio + timedelta(days=i)
            guardar_evento(persona, cliente, dia.isoformat(), tipo)

        st.session_state.post_guardado = True
        st.rerun()

    else:
        st.error("Selecciona una fecha o un rango válido.")

# ============================================================
# MENSAJE DE ÉXITO (DEBAJO DEL FORMULARIO)
# ============================================================
if st.session_state.post_guardado:

    st.success("✔ Registro guardado correctamente.")

    st.write("¿Qué deseas hacer ahora?")

    # Una vez guardado el registro:
    if "default_persona" not in st.session_state:
    st.session_state.default_persona = PERSONAS[0]

    if "default_cliente" not in st.session_state:
        st.session_state.default_cliente = CLIENTES[0]
    
    if "default_rango" not in st.session_state:
        st.session_state.default_rango = date.today()

    persona = st.selectbox("Persona:", PERSONAS, key="persona_input", index=PERSONAS.index(st.session_state.default_persona))
    cliente = st.selectbox("Cliente:", CLIENTES, key="cliente_input", index=CLIENTES.index(st.session_state.default_cliente))
    rango = st.date_input("Fecha o rango:", key="rango_input", value=st.session_state.default_rango)

    
    col1, col2 = st.columns(2)

    if st.button("🔁 Agregar otra actividad"):
        st.session_state.post_guardado = False
    
        # RESET de valores por defecto
        st.session_state.default_persona = PERSONAS[0]
        st.session_state.default_cliente = CLIENTES[0]
        st.session_state.default_rango = date.today()
    
        # RESET de widgets (Streamlit los reconstruye fresh)
        for key in ["persona_input", "cliente_input", "rango_input"]:
            if key in st.session_state:
                del st.session_state[key]
    
        st.rerun()




