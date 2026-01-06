import streamlit as st
import pandas as pd

# ============================================================
# CARGAR CATÁLOGOS
# ============================================================
from database.loaders import cargar_catalogos
from database.repos_supabase import (
    visitas_repo,
    visita_dias_repo   
)

df_clientes, df_personas, df_actividades = cargar_catalogos()

# ============================================================
# CARGAR DATOS
# ============================================================
df_visitas = pd.DataFrame(visitas_repo.get_all())
df_visita_dias = pd.DataFrame(visita_dias_repo.get_all())

st.title("🗑️ Eliminar visita registrada")
st.subheader("Selecciona una visita para eliminar")

# ============================================================
# SELECCIÓN DE PERSONA
# ============================================================
lista_personas = df_personas["nombre"].tolist()

persona = st.selectbox("👤 Persona", lista_personas)

id_persona = int(
    df_personas
        .loc[df_personas["nombre"] == persona, "id_persona"]
        .iloc[0]
)

# ============================================================
# VISITAS DE LA PERSONA
# ============================================================
visitas_persona = (
    df_visitas
        .loc[df_visitas["id_persona"] == id_persona]
        .merge(
            df_clientes[["id_cliente", "nombre"]],
            on="id_cliente",
            how="left"
        )
        .rename(columns={"nombre": "cliente"})
)

if visitas_persona.empty:
    st.info("Esta persona no tiene visitas registradas.")
    st.stop()

# ============================================================
# ARMAR RESUMEN DE VISITAS
# ============================================================
dias_visita = (
    df_visita_dias
        .groupby("id_visita")
        .agg(
            fecha_inicio=("fecha", "min"),
            fecha_fin=("fecha", "max"),
        )
        .reset_index()
)

visitas_resumen = (
    visitas_persona
        .merge(dias_visita, on="id_visita", how="left")
        [["id_visita", "cliente", "fecha_inicio", "fecha_fin"]]
        .sort_values("fecha_inicio")
)

opciones = [
    f"{row.cliente} | {row.fecha_inicio} → {row.fecha_fin}"
    for _, row in visitas_resumen.iterrows()
]

seleccion = st.selectbox(
    "📅 Visitas registradas",
    opciones
)

id_visita_seleccionada = visitas_resumen.iloc[
    opciones.index(seleccion)
]["id_visita"]

st.markdown("---")

# ============================================================
# DETALLE DE LA VISITA
# ============================================================
# ============================================================
# DETALLE DE LA VISITA
# ============================================================

visita = (
    df_visitas
        .loc[df_visitas["id_visita"] == id_visita_seleccionada]
        .iloc[0]
)

# Nombres desde catálogos
nombre_persona = df_personas.loc[
    df_personas["id_persona"] == visita["id_persona"], "nombre"
].iloc[0]

nombre_agregado_por = df_personas.loc[
    df_personas["id_persona"] == visita["id_agregado_por"], "nombre"
].iloc[0]

nombre_cliente = df_clientes.loc[
    df_clientes["id_cliente"] == visita["id_cliente"], "nombre"
].iloc[0]

nombre_actividad = df_actividades.loc[
    df_actividades["id_actividad"] == visita["id_actividad"], "nombre"
].iloc[0]

# Fechas
fechas_visita = (
    df_visita_dias
        .loc[df_visita_dias["id_visita"] == id_visita_seleccionada, "fecha"]
        .sort_values()
)

fecha_inicio = fechas_visita.iloc[0]
fecha_fin = fechas_visita.iloc[-1]

# ============================================================
# RENDER
# ============================================================
st.markdown("##### Detalles de la visita")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**🏭 Cliente:** {nombre_cliente}")
    st.markdown(f"**✈️ Actividad:** {nombre_actividad}")

with col2:
    st.markdown(f"**🧾 Agregado por:** {nombre_agregado_por}")
    st.markdown(f"**📅 Fechas:** {fecha_inicio} → {fecha_fin}")


#
# ============================================================
# CONFIRMACIÓN Y ELIMINACIÓN
# ============================================================
st.markdown("---")
st.warning("⚠️ Esta acción eliminará la visita y todos sus registros asociados.")

confirmar = st.checkbox("Confirmo que deseo eliminar esta visita")

if confirmar:
    if st.button("🗑️ Eliminar visita", type="primary"):
        
        # IMPORTANTE: borrar en orden

        visita_dias_repo.delete_by_field(
            field="id_visita",
            value=id_visita_seleccionada
        )

        visitas_repo.delete(
            record_id=id_visita_seleccionada
        )

        st.success("✅ Visita eliminada correctamente.")
        st.rerun()
