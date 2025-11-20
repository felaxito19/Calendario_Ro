import streamlit as st
from datetime import date, timedelta
import sqlite3
import os


# Crear carpeta data si no existe
os.makedirs("data", exist_ok=True)

# Inicializar DB
def init_db():
    conn = sqlite3.connect("data/calendario.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT,
            cliente TEXT,
            fecha TEXT,
            tipo TEXT,
            creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

init_db()

def guardar_evento(persona, cliente, fecha, tipo):
    conn = sqlite3.connect("data/calendario.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO eventos (persona, cliente, fecha, tipo)
        VALUES (?, ?, ?, ?)
    """, (persona, cliente, fecha, tipo))
    conn.commit()
    conn.close()


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
    st.rerun()   # ÚNICO método válido ahora


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
