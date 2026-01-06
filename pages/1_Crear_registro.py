import streamlit as st
import pandas as pd
from datetime import date, timedelta

#==============================================================
# CARGAR CATÁLOGOS
#==============================================================
from database.loaders import cargar_catalogos

df_clientes, df_personas, df_actividades = cargar_catalogos()

# ============================================================
# UI PRINCIPAL
# ============================================================
st.title("📆 Registrar visita")
st.divider()

lista_usuarios = df_personas["nombre"].tolist()
lista_clientes = df_clientes["nombre"].tolist()
lista_tipos_actividad = df_actividades["tipo_actividad"].unique().tolist()

st.markdown("#### 🧾 Información del registro")

agregado_por = st.selectbox(
    "✍️ Agregado por",
    lista_usuarios    
)

persona = st.selectbox("👤 Persona", lista_usuarios, key="persona_input")
cliente = st.selectbox("⛏️ Unidad Minera", lista_clientes, key="cliente_input")

tipo_actividad = st.selectbox("ℹ️ Tipo de Actividad", lista_tipos_actividad, key="tipo_actividad_input")
df_actividades_filtrado = df_actividades[df_actividades["tipo_actividad"]==tipo_actividad]
lista_actividades = df_actividades_filtrado["nombre"].tolist()
actividad = st.selectbox(
    "✈️ Actividad",
    lista_actividades,
    key="actividad_input"
)


# Selección de rango
rango = st.date_input("📅 Seleccionar rango de fechas:", [])

# ============================================================
# REGISTRO EN LA BASE DE DATOS 
# ============================================================

def expandir_rango(rango):
    if len(rango) != 2:
        return []

    inicio, fin = rango
    dias = []
    d = inicio
    while d <= fin:
        dias.append(d)
        d += timedelta(days=1)

    return dias


from database.repos_supabase import visitas_repo, visita_dias_repo

@st.cache_data(ttl=300)
def cargar_visitas():
    return (
        pd.DataFrame(visitas_repo.get_all()),
        pd.DataFrame(visita_dias_repo.get_all())
    )


df_visitas, df_visitas_dias = cargar_visitas()

st.divider()

if st.button("💾 Guardar registro", type="secondary"):
    
    # ----------------------------
    # Validaciones básicas
    # ----------------------------
    if not agregado_por:
        st.error("Debes indicar quién agrega el registro.")
        st.stop()

    if not rango or len(rango) != 2:
        st.error("Debes seleccionar un rango de fechas.")
        st.stop()

    if not tipo_actividad:
        st.error("Debes seleccionar el tipo de actividad.")
        st.stop()

    if not actividad:
        st.error("Debes seleccionar una actividad")
        st.stop()

    fechas = expandir_rango(rango)

    if not fechas:
        st.error("Rango de fechas inválido.")
        st.stop()

    fechas_str = [f.isoformat() for f in fechas]


    # Ids para insert
    id_persona = int(
        df_personas
            .loc[df_personas["nombre"] == persona, "id_persona"]
            .iloc[0]
    )
    id_cliente = int(
        df_clientes
            .loc[df_clientes["nombre"] == cliente, "id_cliente"]
            .iloc[0]
    )
    id_agregado_por = int(
        df_personas
            .loc[df_personas["nombre"] == agregado_por, "id_persona"]
            .iloc[0]
    )  

    id_actividad = int(
    df_actividades_filtrado
        .loc[df_actividades_filtrado["nombre"] == actividad, "id_actividad"]
        .iloc[0]
    )



    # ---------------------------------------------------------------------------------
    # Validar disponibilidad
    # ---------------------------------------------------------------------------------
    def existe_conflicto(
        id_persona,
        fechas_str,
        df_visitas,
        df_visitas_dias,
        df_clientes
    ):
        
        # -------------------------------
        # 0. Tablas vacías → no hay conflicto
        # -------------------------------
        if df_visitas.empty or df_visitas_dias.empty:
            return []
        
        # ----------------------------------------
        # 1. Visitas existentes de la persona
        # ----------------------------------------
        visitas_persona = (
            df_visitas
                .loc[df_visitas["id_persona"] == id_persona,
                    ["id_visita", "id_cliente"]]
        )

        if visitas_persona.empty:
            return []

        # ----------------------------------------
        # 2. Días de esas visitas
        # ----------------------------------------
        dias_persona = (
            df_visitas_dias
                .merge(visitas_persona, on="id_visita", how="inner")
        )

        # ----------------------------------------
        # 3. Choque de fechas
        # ----------------------------------------
        dias_conflicto = dias_persona[
            dias_persona["fecha"].isin(fechas_str)
        ]

        if dias_conflicto.empty:
            return []

        # ----------------------------------------
        # 4. Agregar nombre del cliente
        # ----------------------------------------
        dias_conflicto = (
            dias_conflicto
                .merge(
                    df_clientes[["id_cliente", "nombre"]],
                    on="id_cliente",
                    how="left"
                )
                .rename(columns={"nombre": "cliente"})
                [["fecha", "cliente", "id_visita"]]
                .sort_values("fecha")
        )

        return dias_conflicto.to_dict(orient="records")
    


    conflictos = existe_conflicto(
        id_persona=id_persona,
        fechas_str=fechas_str,
        df_visitas=df_visitas,
        df_visitas_dias=df_visitas_dias,
        df_clientes=df_clientes
    )


    if conflictos:
        df_conf = pd.DataFrame(conflictos)

        st.error("🚫 La persona ya tiene visitas programadas que se cruzan con el rango seleccionado.")
        resumen_conflictos = (
            df_conf
                .groupby(["id_visita", "cliente"])
                .agg(
                    fecha_inicio=("fecha", "min"),
                    fecha_fin=("fecha", "max")
                )
                .reset_index()
        )


        st.markdown("***Visitas en conflicto:***")
        for _, row in resumen_conflictos.iterrows():
            st.markdown(
                f"""
                **Cliente:** {row['cliente']}  
                **Fechas:** {row['fecha_inicio']} → {row['fecha_fin']}
                """
            )
        

        st.stop()
    #--------------------------------------
    # PREPARAMOS LA DATA e insertamos
    #--------------------------------------

    # VISITAS 
    visita = {
        "id_persona": id_persona,
        "id_cliente": id_cliente,
        "id_agregado_por": id_agregado_por,
        "id_actividad": id_actividad
    }


    #VISITA-DIAS
    id_visita = visitas_repo.insert_and_return_id(visita)

    # Agregamos los dias en la tabla para días----------------------------------------
    
    registros_dias = []

    for f in fechas:
        registros_dias.append({
            "id_visita": id_visita,
            "fecha": str(f)
        })

    visita_dias_repo.insert(registros_dias)
    


    st.success(
        f"✅ Visita registrada para {persona} "
        f"({len(fechas)} día(s)"
    )













