import streamlit as st
import sqlite3
import pandas as pd
import json
import streamlit.components.v1 as components

from supabase import create_client, Client

@st.cache_resource
def init_supabase():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase: Client = init_supabase()


st.set_page_config(page_title="Calendario", layout="wide")
st.title("📆 Calendario de disponibilidad")



# LECUTRA DE DATA REAL
def cargar_eventos():
    response = supabase.table("eventos").select("*").order("fecha").execute()
    data = response.data
    if not data:
        return pd.DataFrame(columns=["persona", "cliente", "fecha", "tipo"])
    return pd.DataFrame(data)


df = cargar_eventos()

# Convertir a la misma estructura que tus datos ficticios
data = list(df[["persona", "cliente", "fecha"]].itertuples(index=False, name=None))


usuarios = sorted(set([u for (u, c, f) in data]))
clientes = sorted(set([c for (u, c, f) in data]))


# ------------------------------------------------------
# Filtros
# ------------------------------------------------------
usuario_filtro = st.selectbox("👤 Filtrar por persona", ["TODOS"] + usuarios)
cliente_filtro = st.selectbox("🏢 Filtrar por cliente", ["TODOS"] + clientes)

# ------------------------------------------------------
# Generación de eventos
# ------------------------------------------------------
# ------------------------------------------------------
# Generación de eventos
# ------------------------------------------------------
def color_unico(nombre):
    return f"#{abs(hash(nombre)) % 0xFFFFFF:06x}"

eventos = []
for usuario, cliente, fecha in data:
    
    # Filtro persona
    if usuario_filtro != "TODOS" and usuario != usuario_filtro:
        continue
    
    # Filtro cliente
    if cliente_filtro != "TODOS" and cliente != cliente_filtro:
        continue
    
    eventos.append({
        "title": usuario,   # o cliente si quieres
        "start": fecha,
        "color": color_unico(usuario),
        "extendedProps": {
            "descripcion": cliente   # tooltip muestra cliente
        }
    })


eventos_json = json.dumps(eventos)

# ------------------------------------------------------
# Vista según selección
# ------------------------------------------------------

# Nos quedamos ocn la vista multiple de año
initialView = "multiMonthYear"
multi_columns = None
multi_rows = None

# ------------------------------------------------------
# HTML + JS FullCalendar
# ------------------------------------------------------
html_code = f"""
<link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' rel='stylesheet'>

<div id='calendar'></div>

<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>

<script>

document.addEventListener('DOMContentLoaded', function() {{
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {{
        initialView: '{initialView}',
        locale: 'es',
        height: 'auto',
        events: {eventos_json},

        headerToolbar: {{
            left: 'prev',
            center: 'title',
            right: 'next'
        }},

        titleFormat: {{ year: 'numeric', month: 'long' }},
        

        expandRows: true,
        eventDisplay: 'block',
    }});

    calendar.render();
}});

</script>

<style>

body {{
    font-family: 'Inter', sans-serif !important;
}}

#calendar {{
    background-color: #ffffff;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.1);
}}

.fc .fc-toolbar-title {{
    font-size: 28px;
    font-weight: 600;
    color: #333;
    text-transform: capitalize;
}}

.fc .fc-button {{
    background: #4A90E2 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: white !important;
}}
.fc .fc-button:hover {{
    background: #357ABD !important;
}}

.fc .fc-col-header-cell {{
    background: #f7f7f7;
    font-size: 14px;
    font-weight: 600;
    color: #444;
    padding: 8px 0;
}}

.fc .fc-daygrid-day-number {{
    font-size: 13px;
    font-weight: 500;
    color: #555;
}}

.fc-event {{
    border: none !important;
    border-radius: 10px !important;
    padding: 4px 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    opacity: 0.9;
}}

.fc-event:hover {{
    opacity: 1;
    transform: scale(1.02);
    transition: 0.1s ease-in-out;
}}

.fc-theme-standard td, 
.fc-theme-standard th {{
    border: 1px solid #e5e5e5 !important;
}}

.fc .fc-multimonth-title {{
    font-size: 22px;
    font-weight: 600;
    padding-bottom: 10px;
    text-transform: capitalize;
}}

.fc-multimonth-view {{
    gap: 18px;
}}

</style>
"""


components.html(html_code, height=3200)


