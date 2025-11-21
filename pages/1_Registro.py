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

PERSONAS = ["Ana", "Carlos", "Luis", "Valeria", "Camila", "Royina", "Gerson", "Marco"]
CLIENTES = ["Antamina", "Las Bambas", "Cerro Verde", "Hudbay", "Quellaveco", "Antapaccay", "Southern Perú"]

persona = st.selectbox("👤 Nombre del empleado", PERSONAS)
cliente = st.selectbox("🏢 Cliente", CLIENTES)
tipo = st.text_input("📝 Tipo de actividad (opcional)")

# Selección de rango
rango = st.date_input("📅 Seleccionar rango de fechas", [])

if st.button("💾 Guardar"):

    # caso SOLO un día
    if isinstance(rango, date):
        st.error("Por favor selecciona un rango de dos fechas.")
        st.stop()

    # caso rango válido (tupla con 2 fechas)
    inicio, fin = rango
    delta = fin - inicio

    for i in range(delta.days + 1):
        dia = inicio + timedelta(days=i)
        guardar_evento(persona, cliente, dia.isoformat(), tipo)

    st.session_state.post_guardado = True
    st.rerun()   # recargar UI


# ============================================================
# MENSAJE DE ÉXITO (DEBAJO DEL FORMULARIO)
# ============================================================
if st.session_state.post_guardado:

    st.success("✔ Registro guardado correctamente.")

    st.write("¿Qué deseas hacer ahora?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔁 Agregar otra actividad"):
            st.session_state.post_guardado = False
            st.rerun()

    with col2:
        if st.button("🚪 Salir"):
            st.write("Gracias por registrar la disponibilidad.")
            st.stop()

