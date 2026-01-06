import streamlit as st

# Configuración inicial (Siempre debe ser lo primero)
st.set_page_config(
    page_title="Metso Pumps Calendar",
    page_icon="📆"    
)

# --- DEFINICIÓN DE PÁGINAS DESDE ARCHIVOS ---

# Ahora definimos el Inicio como un archivo físico
inicio         = st.Page("pages/5_Inicio.py", title="Inicio", icon="🏠", default=True)
crear_registro = st.Page("pages/1_Crear_registro.py", title="Crear Registro", icon="➕")
calendario     = st.Page("pages/2_Calendario.py", title="Calendario", icon="📅")
editar_visita  = st.Page("pages/3_Editar_Visita.py", title="Editar Visita", icon="✏️")
configuracion  = st.Page("pages/4_Configuracion.py", title="Configuración", icon="⚙️")

# --- NAVEGACIÓN ---

# Agrupamos los scripts en secciones
pg = st.navigation({
    "Principal": [inicio, calendario],
    "Gestión": [crear_registro, editar_visita],
    "Ajustes": [configuracion]
})

# --- BARRA LATERAL ---
st.sidebar.caption("v1.0.0 | Metso Pumps")

# Ejecución
pg.run()