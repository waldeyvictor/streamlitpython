import streamlit as st


pg_inicio = st.Page("pages/👋_Inicio.py", title="Home", url_path="inicio")

pg_acumulado_equipe = st.Page("pages/Produtiv_Diaria_x_Equipe.py", title="Acumulado por Equipe", url_path="Acumulado_equipe", icon="🚚")

pg_prod_diaria = st.Page("pages/6_📈_Produtiv_Diaria_Micro.py", title="Acompanhamento Diario", url_path="Acomp_dia", icon="📒")

pg_global_ano = st.Page("pages/5_📈_Produtiv_Visão_Anual.py", title="Acompanhamento Global - Ano", url_path="Acomp_ano", icon="📊")

pg_global_mes = st.Page("pages/4_📈_Produtiv_Visão_Global.py", title="Acompanhamento Global - Mês", url_path="Acomp_mes")

pg_prog_exec = st.Page("pages/programacao_exec.py", title="Programação de Execução", url_path="Prog_exec", icon="📅")

pg_prog_valid = st.Page("pages/programacao_valid.py", title="Programação de Validação", url_path="Prog_valid", icon="📆")

pg_fisico = st.Page("pages/1_📈_Avanço_Fisico.py", title="Avanço Fisico", url_path="torre_fisico", icon="💪")

pg_financeiro = st.Page("pages/2_📈_Avanço_Financeiro.py", title="Avanço Financeiro", url_path="torre_financeiro", icon="💸")

paginas_agrupadas = {
    "⚫ Incio": [pg_inicio],
    "⚫ Produtividade": [pg_prod_diaria, pg_acumulado_equipe, pg_global_mes, pg_global_ano],
    "⚫ Programação": [pg_prog_exec, pg_prog_valid],
    "⚫ Torre": [pg_fisico, pg_financeiro]
}

pg = st.navigation(paginas_agrupadas)
pg.run()