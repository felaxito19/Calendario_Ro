import streamlit as st
import pandas as pd

# ============================================================
# REPOS
# ============================================================
from database.repos_supabase import (
    catalogo_clientes_repo,
    catalogo_personas_repo,
    catalogo_actividades_repo,
)

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Catálogos",
    layout="wide"
)

st.markdown(
    """
    <div style="font-size:34px; font-weight:700;">
        ⚙️ Configuración
    </div>
    <div style="font-size:22px; color:#6B7280; margin-bottom:24px;">
        Gestión de catálogos
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# ============================================================
# DEFINICIÓN DE CATÁLOGOS
# ============================================================
CATALOGOS = {
    "Clientes": {
        "repo": catalogo_clientes_repo,
        "id_field": "id_cliente",
        "nombre_field": "nombre",
    },
    "Personas": {
        "repo": catalogo_personas_repo,
        "id_field": "id_persona",
        "nombre_field": "nombre",
    },
    "Actividades": {
        "repo": catalogo_actividades_repo,
        "id_field": "id_actividad",
        "nombre_field": "nombre",
    },
}

# ============================================================
# SELECTOR DE CATÁLOGO
# ============================================================
st.subheader("📚Catálogo")

catalogo_nombre = st.selectbox(
    "Seleccionar catálogo",
    list(CATALOGOS.keys())
)

cfg = CATALOGOS[catalogo_nombre]

repo = cfg["repo"]
id_field = cfg["id_field"]
nombre_field = cfg["nombre_field"]

# ... (imports y selección de catálogo igual)

# ============================================================
# CARGAR DATA
# ============================================================
# Es vital usar un identificador único para que el editor no se resetee
# ... (tu código previo de selección de catálogo)

# 1. CARGAR DATA
# Usamos un contenedor para que al recargar la data sea más limpio
df = pd.DataFrame(repo.get_all())

if df.empty:
    st.info("Este catálogo no tiene registros.")
    # Si quieres permitir añadir el primer registro:
    df = pd.DataFrame(columns=[id_field, nombre_field]) 

st.divider()

if not df.empty or catalogo_nombre:
    st.subheader(f"📋 Lista de {catalogo_nombre}")
    st.caption("Aquí podemos editar los catálgos directamente. Doble clic para modificar una celda")
    
    # Configuramos las columnas
    # Importante: El ID debe estar presente pero podemos ponerlo como lectura (disabled)
    config_dinamica = {
        id_field: st.column_config.TextColumn("ID", disabled=True),
        nombre_field: st.column_config.TextColumn(nombre_field.replace("_", " ").title())
    }

    # El editor
    df_editado = st.data_editor(
        df,
        column_config=config_dinamica,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"editor_{catalogo_nombre}"
    )

    # Accedemos al estado del editor
    state = st.session_state[f"editor_{catalogo_nombre}"]
    
    # Cambios detectados
    editados = state.get("edited_rows", {})
    borrados = state.get("deleted_rows", [])
    añadidos = state.get("added_rows", [])

    if editados or borrados or añadidos:
        st.warning("⚠️ Tienes cambios pendientes de guardar.")
        col1, col2 = st.columns([1, 5])
        
        with col1:
            if st.button("💾 Aplicar todo", type="primary"):
                try:
                    # --- 1. PROCESAR ELIMINACIONES (Primero borrar para evitar conflictos) ---
                    for idx in borrados:
                        # Obtenemos el ID real desde el DF original usando el índice
                        row_id = df.iloc[idx][id_field]
                        repo.delete(row_id)

                    # --- 2. PROCESAR EDICIONES ---
                    for idx, updates in editados.items():
                        row_id = df.iloc[idx][id_field]
                        repo.update(row_id, updates)

                    # --- 3. PROCESAR NUEVOS REGISTROS ---
                    for fila_nueva in añadidos:
                        if fila_nueva.get(nombre_field): # Validación mínima
                            repo.insert(fila_nueva)
                    
                    st.success("¡Cambios aplicados!") 
                    # Limpiar caché si usas st.cache_data en tus métodos get_all
                    if hasattr(st, "cache_data"):
                        st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
        
        with col2:
            if st.button("🚫 Descartar"):
                st.rerun()