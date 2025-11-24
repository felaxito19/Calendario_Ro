import streamlit as st


st.set_page_config(
    page_title="Sistema de Disponibilidad",
    page_icon="📌",
    layout="centered"
)

st.title("Seguimiento - Visitas a unidades mineras")
st.write("Bienvenido al panel principal. Este sistema permite dar seguimiento y visualizar las visitas del equipo en las unidades mineras. Usa el menú de la izquierda para registrar actividades o visualizar el calendario.")

# ======== DISEÑO VERTICAL ==========

# SECCIÓN 1
st.markdown("""
### 📅 Ver calendario  
Podras filtrar el usuario y/o la unidad minera para visualizar las visitas programadas :) 

<br><br>
""", unsafe_allow_html=True)


# SECCIÓN 2
st.markdown("""
### 📝 Registrar visitas  
- Seleccionar tu nombre 
- Elegir la unidad minera  
- Registrar las fechas de visita  
- Guardar la actividad en la base de datos  

<br>
""", unsafe_allow_html=True)

# SECCIÓN 3
st.markdown("""
### 🚩 Eliminar registro
En caso deseas hacer un cambio con alguna visita registrada, se debe eliminar y crear uno nuevo. 
Para ello, seleccionas tu nombre y aparecerá tus visitas registradas, selecciona el boton de "Eliminar" y espera el mensaje de confirmación. 

<br>
""", unsafe_allow_html=True)

# SECCIÓN 4
st.markdown("""
### ⚙️Configuración  
No ingresar a esta sección, se utilizará únicamente para agregar a nuevos usuarios y/o clientes.

<br><br>
""", unsafe_allow_html=True)



