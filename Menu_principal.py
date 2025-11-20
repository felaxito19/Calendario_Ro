import streamlit as st

st.set_page_config(
    page_title="Sistema de Disponibilidad",
    page_icon="📌",
    layout="wide"
)

st.title("📌 Sistema de Disponibilidad")
st.write("Bienvenido al panel principal. Usa el menú de la izquierda para registrar actividades o visualizar el calendario.")

# ======== DISEÑO VERTICAL ==========
st.markdown("""
<br>

## 👋 Bienvenido  
Este sistema permite que los empleados registren su disponibilidad de manera rápida y que el jefe pueda visualizar todo en un calendario moderno.

<br>

## 🔧 ¿Qué puedes hacer aquí?
""", unsafe_allow_html=True)

# SECCIÓN 1
st.markdown("""
### 📝 Registrar disponibilidad  
- Seleccionar un empleado  
- Elegir un cliente  
- Registrar una o varias fechas  
- Guardar la actividad en la base de datos  

<br>
""", unsafe_allow_html=True)

# SECCIÓN 2
st.markdown("""
### 📅 Ver calendario  
- Vista anual Multi-Mes  
- Colores por persona  
- Filtrar por empleado o cliente  
- Revisar disponibilidad general  

<br><br>
""", unsafe_allow_html=True)
