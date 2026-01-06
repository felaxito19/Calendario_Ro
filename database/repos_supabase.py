from database.base_repo_supabase import BaseRepoSupabase

# CATALOGOS
catalogo_actividades_repo = BaseRepoSupabase("catalogo_actividades", id_field="id_actividad")
catalogo_clientes_repo    = BaseRepoSupabase("catalogo_clientes", id_field="id_cliente")
catalogo_personas_repo    = BaseRepoSupabase("catalogo_personas", id_field="id_persona")

# TABLAS DE HECHOS
visitas_repo            = BaseRepoSupabase("visitas", id_field="id_visita")
visita_dias_repo = BaseRepoSupabase("visita_dias", id_field="id_visita_dia")

# VISTA PARA ALIMENTAR EL CALENDARIO
vista_calendario_repo = BaseRepoSupabase("vw_calendario_visitas")