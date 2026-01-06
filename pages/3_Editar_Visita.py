import streamlit as st
import pandas as pd
from database.loaders import cargar_catalogos
from database.repos_supabase import visitas_repo, visita_dias_repo

st.set_page_config(page_title="Gestión de Visita", layout="centered")

# 1. Recuperar el ID del session_state
id_visita = st.session_state.get("id_visita_editar")

# 2. VALIDACIÓN CRÍTICA: Detener si es None o inválido
if id_visita is None or id_visita == "None":
    st.warning("⚠️ Debes seleccionar una visita desde el calendario para estar aquí.")
    if st.button("Voler a inicio"):
        st.switch_page("pages/5_Inicio.py") 
    st.stop() 

# 3. Intentar convertir a entero por seguridad
try:
    id_visita = int(id_visita)
except ValueError:
    st.error(f"ID de visita no válido: {id_visita}")
    st.stop()

# 4. RECIÉN AQUÍ llamar a la base de datos
try:
    visita = visitas_repo.get_by_id(id_visita)
    if not visita:
        st.error("No se encontró el registro en la base de datos.")
        st.stop()
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

id_visita = st.session_state.id_visita_editar

# Cargar catálogos y datos actuales desde Supabase
df_clientes, df_personas, df_actividades = cargar_catalogos()
visita = visitas_repo.get_by_id(id_visita)
dias_existentes = visita_dias_repo.get_by_field("id_visita", id_visita)

# Mapeos para los Selectbox (Nombre -> ID)
dict_clientes = dict(zip(df_clientes["nombre"], df_clientes["id_cliente"]))
dict_personas = dict(zip(df_personas["nombre"], df_personas["id_persona"]))
dict_actividades = dict(zip(df_actividades["nombre"], df_actividades["id_actividad"]))

# Obtener rango actual de fechas para pre-llenar el formulario
if dias_existentes:
    df_temp_dias = pd.DataFrame(dias_existentes)
    fecha_min = pd.to_datetime(df_temp_dias['fecha']).min().date()
    fecha_max = pd.to_datetime(df_temp_dias['fecha']).max().date()
else:
    fecha_min = fecha_max = pd.to_datetime("today").date()

st.title(f"🛠️ Gestión de Visita #{id_visita}")

# ==============================================================================
# SECCIÓN 1: FORMULARIO DE EDICIÓN
# ==============================================================================
with st.form("form_edicion_total"):
    st.subheader("📌 Editar Información")
    
    col1, col2 = st.columns(2)
    with col1:
        # Cliente
        nombre_c = df_clientes.loc[df_clientes["id_cliente"] == visita["id_cliente"], "nombre"].iloc[0]
        cliente_sel = st.selectbox("🏭 Cliente", options=df_clientes["nombre"].tolist(), 
                                index=df_clientes["nombre"].tolist().index(nombre_c))
        
        # Actividad
        nombre_a = df_actividades.loc[df_actividades["id_actividad"] == visita["id_actividad"], "nombre"].iloc[0]
        actividad_sel = st.selectbox("✈️ Actividad", options=df_actividades["nombre"].tolist(),
                                    index=df_actividades["nombre"].tolist().index(nombre_a))

    with col2:
        # Persona Asignada
        nombre_p = df_personas.loc[df_personas["id_persona"] == visita["id_persona"], "nombre"].iloc[0]
        persona_sel = st.selectbox("👤 Persona Asignada", options=df_personas["nombre"].tolist(),
                                index=df_personas["nombre"].tolist().index(nombre_p))
        
        # Agregado por
        nombre_ag = df_personas.loc[df_personas["id_persona"] == visita["id_agregado_por"], "nombre"].iloc[0]
        agregado_por_sel = st.selectbox("🧾 Registrado por", options=df_personas["nombre"].tolist(),
                                        index=df_personas["nombre"].tolist().index(nombre_ag))

    st.divider()
    
    st.subheader("📅 Rango de Fechas")
    rango_fechas = st.date_input("Selecciona el tramo", value=(fecha_min, fecha_max), format="DD/MM/YYYY")
    
    notas = st.text_area("📝 Notas y Observaciones", value=visita.get("notas", ""))

    # Botones principales del form
    c_save, c_back = st.columns([1, 4])
    save_btn = c_save.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
    if c_back.form_submit_button("Volver"):
        st.switch_page("5_Inicio.py")

# Lógica Guardar
if save_btn:
    if not isinstance(rango_fechas, tuple) or len(rango_fechas) < 2:
        st.error("Error: Selecciona Fecha Inicio y Fin.")
    else:
        try:
            # 1. Update Cabecera
            visitas_repo.update(id_visita, {
                "id_cliente": dict_clientes[cliente_sel],
                "id_persona": dict_personas[persona_sel],
                "id_actividad": dict_actividades[actividad_sel],
                "id_agregado_por": dict_personas[agregado_por_sel],
                "notas": notas
            })
            # 2. Update Días (Borrar e insertar)
            visita_dias_repo.delete_by_field("id_visita", id_visita)
            nuevo_rango = pd.date_range(start=rango_fechas[0], end=rango_fechas[1])
            for d in nuevo_rango:
                visita_dias_repo.insert({"id_visita": id_visita, "fecha": str(d.date())})
            
            st.success("✅ Cambios aplicados con éxito.")
            st.balloons()
        except Exception as e:
            st.error(f"Error al guardar: {e}")

# ==============================================================================
# SECCIÓN 2: ZONA DE PELIGRO (Eliminación)
# ==============================================================================
st.divider()
with st.expander("🚨 Zona de Peligro - Eliminar Registro"):
    st.write("Al eliminar esta visita, se borrarán también todos los días asociados en el calendario.")
    
    # Confirmación de doble paso
    check_borrar = st.checkbox("Confirmo que deseo borrar permanentemente esta visita.")
    
    if st.button("🗑️ Eliminar Visita Completa", type="secondary", disabled=not check_borrar, use_container_width=True):
        try:
            # Orden: primero hijos (días), luego padre (visita)
            visita_dias_repo.delete_by_field("id_visita", id_visita)
            visitas_repo.delete(id_visita)
            
            st.success("Registro eliminado correctamente. Redirigiendo...")
            st.session_state.pop("id_visita_editar", None) # Limpiar el ID seleccionado
            st.switch_page("5_Inicio.py")
        except Exception as e:
            st.error(f"Error al eliminar: {e}")