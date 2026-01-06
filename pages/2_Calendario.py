from streamlit_calendar import calendar
import streamlit as st
import pandas as pd
from io import BytesIO



if "id_visita_editar" not in st.session_state:
    st.session_state.id_visita_editar = None


st.markdown("""
    <style>
    /* Centrar la página al 80% */
    .main .block-container {
        max-width: 80%;
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 2rem;
    }

    /* Estilos del calendario (salto de línea y centrado) */
    .fc-event-title {
        white-space: pre-wrap !important; 
        text-align: center !important;    
        font-size: 0.85rem !important;    
        overflow: visible !important;     
    }
    .fc-event {
        height: auto !important;
        padding: 2px 0; /* Un poco de aire interno */
    }
    .fc-event-title {
        white-space: pre-wrap !important; /* Permite saltos de linea */
        text-align: center !important;    /* Centra el texto */
        font-size: 0.85rem !important;    /* Ajusta tamaño si es necesario */
        overflow: visible !important;     /* Muestra todo el texto */
    }
    .fc-event {
        height: auto !important;          /* Permite que la cajita crezca */
    }
    </style>
""", unsafe_allow_html=True)



st.session_state.id_visita_editar = None

# ------------------------------------------------------
# CONFIG
# ----------------------------------------------------
st.title("📆 Calendario de disponibilidad")
st.divider()

# -------------------------------------------------------
# CATÁLOGOS
# -------------------------------------------------------

from database.loaders import cargar_catalogos

df_clientes, df_personas, df_actividades = cargar_catalogos()



# ------------------------------------------------------
# EVENTOS
# ------------------------------------------------------
from database.repos_supabase import vista_calendario_repo

df_eventos = pd.DataFrame(vista_calendario_repo.get_all())

# ------------------------------------------------------
# EXPORTAR DF COMPLETO A EXCEL (SIN IDS)
# ------------------------------------------------------

COLUMNAS_EXCLUIR = [
    "id_visita",
    "id_visita_dia",
    "id_cliente",
    "id_persona",
    "id_tipo_actividad"
]

df_excel = df_eventos.drop(columns=COLUMNAS_EXCLUIR, errors="ignore")


# ------------------------------------------------------
# FILTROS
# ------------------------------------------------------

lista_usuarios = df_personas["nombre"].tolist()
lista_clientes = df_clientes["nombre"].tolist()
lista_tipos = sorted(df_actividades["tipo_actividad"].dropna().unique().tolist())

col1, col2, col3 = st.columns(3)

with col1:
    tipo_filtro = st.selectbox(
        "🧭 Tipo de actividad",
        ["Todos"] + lista_tipos
    )

with col2:
    usuario_filtro = st.selectbox(
        "👤 Filtrar por persona",
        ["Todos"] + lista_usuarios
    )

with col3:
    cliente_filtro = st.selectbox(
        "🏢 Filtrar por cliente",
        ["Todos"] + lista_clientes
    )

st.divider()

# ----------------------------
# Aplicar filtros
# ----------------------------
if usuario_filtro != "Todos":
    df_eventos = df_eventos[df_eventos["persona"] == usuario_filtro]

if cliente_filtro != "Todos":
    df_eventos = df_eventos[df_eventos["cliente"] == cliente_filtro]

if tipo_filtro != "Todos":
    df_eventos = df_eventos[df_eventos["tipo_actividad"] == tipo_filtro]




#st.write(df_eventos)

# -------------------------------------------------------
def abreviar(nombre):
    partes = nombre.split()
    if len(partes) >= 2:
        return f"{partes[0]} {partes[2]}"
    return nombre


# ------------------------------------------------------
# CALENDARIO
# ------------------------------------------------------




def build_events(df):
    events = []
    
    # Definimos una paleta de colores agradables (Hex codes)
    PALETA = [
        "#2E5BFF", # Azul
        "#8E44AD", # Morado
        "#27AE60", # Verde
        "#E67E22", # Naranja
        "#E74C3C", # Rojo
        "#16A085"  # Turquesa
    ]
    
    # Creamos un mapeo de Persona -> Color para que la misma persona siempre tenga el mismo color
    personas_unicas = df["persona"].unique().tolist()
    color_map = {persona: PALETA[i % len(PALETA)] for i, persona in enumerate(personas_unicas)}

    for _, row in df.iterrows():
            persona_short = abreviar(row["persona"])
            
            # AQUÍ ESTÁ EL CAMBIO: Usamos \n para el salto de línea
            title = f"{persona_short}" 
            
            # Asignamos el color según la persona
            color = color_map.get(row["persona"], "#000000")

            events.append({
                "id": row["id_visita_dia"],
                "title": title,
                "start": row["fecha"],
                "allDay": True,
                "backgroundColor": color,
                "borderColor": color,
                "textColor": "#FFFFFF"
            })

    return events




events = build_events(df_eventos)



calendar_options = {
    "locale": "es",
    "firstDay": 1,
    "initialView": "dayGridMonth", # Puedes cambiar esto a "dayGridWeek" si quieres que inicie en semana
    "dayMaxEvents": 4,
    "height": 850,
    "contentHeight": 600,
    "expandRows": False,
    
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        # Agregamos 'dayGridWeek' aquí 👇
        "right": "dayGridMonth,dayGridWeek,listMonth", 
    },

    "buttonText": {
        "today": "Hoy",
        "dayGridMonth": "Mes",
        "dayGridWeek": "Semana", # Nombre para el botón
        "listMonth": "Agenda"
    }
}

calendar_options["nowIndicator"] = True


event_id = None

result = calendar(
    events=events,
    options=calendar_options
)


# ---------------------------------------------------------------
# DETALLE
# ---------------------------------------------------------------


@st.dialog("📌 Detalle del Registro")
def mostrar_detalle(evento_row):

    
    st.write(f"**👤 Persona:**\n{evento_row['persona']}")
    
    col1, col2 = st.columns(2)
        
    with col1:
        st.write(f"**🏢 Cliente:**\n{evento_row['cliente']}")
        st.write(f"**📅 Fecha:**\n{evento_row['fecha']}")
    
    with col2:
        st.write(f"**🗃️ Categoría:**\n{evento_row['tipo_actividad']}")
        st.write(f"**🧭 Actividad:**\n{evento_row['tipo_actividad']}")
    
       
    st.write(f"**📝 Agregado por:** {evento_row.get('agregado_por', 'N/A')}")
    
    # Información adicional que mencionaste
    # Si tienes una columna de notas o descripción en tu df original
    if "notas" in evento_row:
        st.info(f"**Notas:** {evento_row['notas']}")

    
    st.divider()

    # Botones de Acción
    c1, c2, c3 = st.columns(3)
    if c1.button("✏️ Editar", use_container_width=True):
        st.session_state.id_visita_editar = evento_row["id_visita"]
        st.switch_page("pages/3_Editar_Visita.py")
        st.rerun()
      

# ---------------------------------------------------------------
# LÓGICA DE ACTIVACIÓN
# ---------------------------------------------------------------

if result and result.get("eventClick"):
    event_id = result["eventClick"]["event"]["id"]
    
    try:
        event_id = int(event_id)
        df_match = df_eventos[df_eventos["id_visita_dia"] == event_id]
        
        if not df_match.empty:
            # LLAMADA AL DIÁLOGO
            mostrar_detalle(df_match.iloc[0])
        else:
            st.error("Evento no encontrado en la base de datos.")
    except ValueError:
        st.error("ID de evento inválido.")


st.caption("💡 Haz clic en cualquier evento para ver el detalle completo.")
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Calendario")
    return output.getvalue()


st.download_button(
    label="⬇️ Descargar vista completa (Excel)",
    data=df_to_excel_bytes(df_excel),
    file_name="vista_calendario_completa.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)






