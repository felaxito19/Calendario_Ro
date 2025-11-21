import streamlit as st
from supabase import create_client, Client

st.title("⚙️ Configuración del sistema")



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
# 1. EDITAR PERSONAS
# ============================================================
st.subheader("👥 Editar lista de personas")

# Obtener personas actuales
resp = supabase.table("catalogo_personas").select("id, nombre").order("nombre").execute()
personas = resp.data or []

# Mostrar lista
for p in personas:
    col1, col2 = st.columns([3,1])
    col1.write(f"• {p['nombre']}")
    if col2.button("Eliminar", key=f"del_persona_{p['id']}"):
        supabase.table("catalogo_personas").delete().eq("id", p["id"]).execute()
        st.rerun()

# Agregar persona
nueva_persona = st.text_input("Agregar nueva persona")
if st.button("➕ Agregar persona"):
    if nueva_persona.strip():
        supabase.table("catalogo_personas").insert({"nombre": nueva_persona}).execute()
        st.success("Persona agregada.")
        st.rerun()
    else:
        st.error("Ingrese un nombre válido.")

st.markdown("---")

# ============================================================
# 2. EDITAR CLIENTES
# ============================================================
st.subheader("🏢 Editar lista de clientes")

resp = supabase.table("catalogo_clientes").select("id, nombre").order("nombre").execute()
clientes = resp.data or []

for c in clientes:
    col1, col2 = st.columns([3,1])
    col1.write(f"• {c['nombre']}")
    if col2.button("Eliminar", key=f"del_cliente_{c['id']}"):
        supabase.table("catalogo_clientes").delete().eq("id", c["id"]).execute()
        st.rerun()

nuevo_cliente = st.text_input("Agregar nuevo cliente")
if st.button("➕ Agregar cliente"):
    if nuevo_cliente.strip():
        supabase.table("catalogo_clientes").insert({"nombre": nuevo_cliente}).execute()
        st.success("Cliente agregado.")
        st.rerun()
    else:
        st.error("Ingrese un nombre válido.")


# ============================================================
# 3. BORRAR TODOS LOS REGISTROS
# ============================================================
st.subheader("🗑 Borrar todos los registros del calendario")

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# Botón inicial
if st.button("🛑 ELIMINAR TODOS LOS REGISTROS"):
    st.session_state.confirm_delete = True

# Si está en modo confirmación…
if st.session_state.confirm_delete:
    st.warning("¿Seguro? Esta acción NO se puede deshacer?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✔ Sí, borrar todo"):
            supabase.table("BD_calendario_disponibilidad").delete().neq("id", -1).execute()
            st.success("Todos los registros fueron eliminados correctamente.")
            st.session_state.confirm_delete = False
            st.rerun()

    with col2:
        if st.button("❌ Cancelar"):
            st.session_state.confirm_delete = False
            st.rerun()


