import streamlit as st
import pandas as pd
from database.repos_supabase import catalogo_clientes_repo, catalogo_personas_repo, catalogo_actividades_repo

@st.cache_data
def cargar_catalogos():
    df_clientes = pd.DataFrame(catalogo_clientes_repo.get_all())
    df_personas = pd.DataFrame(catalogo_personas_repo.get_all())
    df_actividades = pd.DataFrame(catalogo_actividades_repo.get_all())

    return df_clientes,  df_personas, df_actividades
