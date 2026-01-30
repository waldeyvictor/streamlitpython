import streamlit as st

st.set_page_config(page_title="Avanço Fisico", page_icon="📈", layout="wide")
st.markdown(
    """
    <h3 style="
        text-align: center;
        background-color: #060054;
        color: white;
        padding: 10px;
        border-radius: 8px;
    ">
        Avanço Fisico - Capex
    </h3>
    """,
    unsafe_allow_html=True
    )
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_excel("Base_RD.xlsx")

df = load_data()

df.columns = df.columns.str.strip()

df = df[(df["VALIDAÇÃO"]=="EQUATORIAL")&(df["ORDEM"]=="I")].copy()

df["Ano_PEP"] = (
    df["4nvl"].astype(str).str.slice(3,5).apply(lambda x: 2025 if x == "25" else 2026)
)

Legenda = {
"ABER/ABER":"CANCELADO",
"ABER/CANC":"CANCELADO",
"ABER/LOG":"LOGISTICA",
"ENCE/ENCE":"COMS+",
"ENTE/CKCP":"COMS+",
"LIB/ATEC":"LIBERADO",
"LIB/CANC":"CANCELADO",
"LIB/COMS":"COMS+",
"LIB/CONC":"CONCLUIDO",
"LIB/DEV":"DEVOLVIDO MEDIÇÃO",
"LIB/DFEC":"DEVOLVIDO ENCERRAMENTO",
"LIB/ENER":"ENERGIZADO",
"LIB/ENTE":"COMS+",
"LIB/LOG":"LIBERADO LOGISTICA",
"LIB/MED":"COMS+",
"LIB/PEND":"DEVOLVIDO REGIONAL",
"LIB/CKCP":"COMS+",
"LIB/REC":"COMS+"
}

df["Legenda"] = df["Status"].map(Legenda)

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):

    df["Data_Status_Atual"] = pd.to_datetime(df["Data_Status_Atual"], errors="coerce")

    df['Data_Ener'] = pd.to_datetime(df['Data_Ener'], errors='coerce')

    df['Data_Conc'] = pd.to_datetime(df['Data_Conc'], errors='coerce')

    df["Data_Log"] = pd.to_datetime(df["Data_Log"], errors='coerce')

    df["Mes_Status_Atual"] = df["Data_Status_Atual"].dt.strftime("%m")
    return df

def kpi_card(titulo, valor, cor_borda="#060054"):
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 15px;
            border-left: 7px solid {cor_borda};
            background-color: #f8f9fa;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        ">
            <p style="color: #6c757d; font-size: 14px; margin-bottom: 5px; font-weight: bold;">{titulo}</p>
            <h2 style="color: #212529; margin: 0; font-size: 30px;">{valor}</h2>
        </div>
    """, unsafe_allow_html=True)

df = preprocess(df)

coms = (df["Legenda"]=="COMS+").sum()
logistica = (df["Legenda"]=="LOGISTICA").sum()
cancelado = (df["Legenda"]=="CANCELADO").sum()
liberado = (df["Legenda"]=="LIBERADO").sum()
concluido = (df["Legenda"]=="CONCLUIDO").sum()
liberado_logistica = (df["Legenda"]=="LIBERADO LOGISTICA").sum()
devolvido_regional = (df["Legenda"]=="DEVOLVIDO REGIONAL").sum()
energizado = (df["Legenda"]=="ENERGIZADO").sum()
devolvido_encerramento = (df["Legenda"]=="DEVOLVIDO ENCERRAMENTO").sum()

# Criando uma área de filtros no corpo principal
with st.expander("Expandir Filtros", expanded=False):
    st.markdown("##### 🛠️ Parâmetros")
    
    # 4 colunas de tamanhos diferentes para equilibrar o visual
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        ano = df["Ano_PEP"].unique().tolist()
        ano_sel = st.multiselect(
            "Ano",
            options=ano,
            default=ano
        )
    
    with f2:
        status_opcoes = df["Status"].unique().tolist()
        status_selecionado = st.multiselect(
            "Filtrar por status",
            options=status_opcoes,
            default=status_opcoes
        )
    
    if not isinstance(ano_sel, list):
        anos_filtro = [ano_sel]
    else:
        anos_filtro = ano_sel

    with f3:
        siglas = df["P.I"].unique().tolist()
        siglas_f = st.multiselect(
            "Filtrar P.I",
            options=siglas,
            default=siglas
        )

    with f4:
        legendas = df["Legenda"].unique().tolist()
        legendas_f = st.multiselect(
            "Filtrar Legenda",
            options=legendas,
            default=legendas
        )

st.divider()

q1,q2,q3,q4,q5,q6,q7,q8 = st.columns(8)

with q1:
    kpi_card("AGUARD LOGISTICA",logistica)

with q2:
    kpi_card("LIBERADO LOGISTICA",liberado_logistica)

with q3:
    kpi_card("LIBERADAS",liberado)
        
with q4:
    kpi_card("ENERGIZADAS",energizado)
        
with q5:
    kpi_card("CONCLUIDAS",concluido)
        
with q6:
    kpi_card("DEV REGIONAL",devolvido_regional)
        
with q7:
    kpi_card("DEV ENCERRAMENTO",devolvido_encerramento)

with q8:
    kpi_card("COMISSIONADAS+",coms)

st.divider()

df_ener_filtro = df[
    (df["Data_Ener"].notna()) &
    (df["Data_Ener"].dt.year.isin(ano_sel)) &
    (df["Status"].isin(status_selecionado))
].copy()

df_ener_f = df_ener_filtro.groupby("P.I")["Data_Ener"].count().reset_index()

df_ener_f = df_ener_f.sort_values("Data_Ener", ascending=False)
df_ener_f.columns = ["P.I","Qtd Energizada"]
df_ener_f = df_ener_f.sort_values("Qtd Energizada", ascending=False)

g1,g2= st.columns([1,4])


with g1:
    st.markdown(f"Energização por P.I")

    if df_ener_f.empty:
        st.info("Nennhum dado encontrado para os filtros selecionados.")
    else:
        st.dataframe(
            df_ener_f,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Qtd Energizada": st.column_config.ProgressColumn(
                    "Obras Energizadas",
                    format="%d",
                    min_value=0,
                    max_value=int(df_ener_f["Qtd Energizada"].max())
                )
            },
            height=300
        )

df_status_filtro = df[
    (df["Data_Status_Atual"].dt.year.isin(ano_sel)) &
    (df["P.I"].isin(siglas_f))
].copy()

df_status_f = df_status_filtro.groupby("Status")["4nvl"].count().reset_index()

df_status_f = df_status_f.sort_values("Status", ascending=False)
df_status_f.columns = ["Status","Qtd total"]
df_status_f = df_status_f.sort_values("Qtd total", ascending=False)

df_mensal = df[
    (df["Data_Ener"].notna()) & 
    (df["Data_Ener"].dt.year.isin(ano_sel if isinstance(ano_sel, list) else [ano_sel]))
].copy()

df_mensal["Mes_Num"] = df_mensal["Data_Ener"].dt.month
df_mensal["Mês"] = df_mensal["Data_Ener"].dt.strftime('%m-%b') # Ex: 01 - Jan

resumo_mensal = df_mensal.groupby(["Mes_Num", "Mês"]).size().reset_index(name="Quantidade")
resumo_mensal = resumo_mensal.sort_values("Mes_Num") # Garante ordem cronológica

with g2:
    st.markdown(f"Obras Energizadas por Mês - {ano_sel}")

#Criando o gráfico no Plotly
    fig = px.bar(
        resumo_mensal,
        x="Mês",
        y="Quantidade",
        text="Quantidade",  # <--- Aqui estão os seus RÓTULO
        color_discrete_sequence=["#060054"], # Cor azul padrão
        height=360
    )

    # Ajustes finos no layout
    fig.update_traces(textposition='outside') # Coloca o número acima da barra
    fig.update_layout(
        xaxis_title="Mês de Energização",
        yaxis_title="Qtd Obras",
        plot_bgcolor="rgba(0,0,0,0)", # Fundo transparente
        hovermode="x unified"
    )

    # 5. Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True)

g3,g4 = st.columns([1,4])

df_conc_filtro = df[
    (df["Data_Conc"].notna()) &
    (df["Data_Conc"].dt.year.isin(ano_sel))
].copy()

df_conc_f = df_conc_filtro.groupby("P.I")["Data_Conc"].count().reset_index()

df_conc_f = df_conc_f.sort_values("Data_Conc", ascending=False)
df_conc_f.columns = ["P.I","Qtd Concluida"]
df_conc_f = df_conc_f.sort_values("Qtd Concluida", ascending=False)

with g3:

    st.markdown(f"Conclusão por P.I")

    if df_conc_f.empty:
        st.info("Nennhum dado encontrado para os filtros selecionados.")
    else:
        st.dataframe(
        df_conc_f,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Qtd Concluida": st.column_config.ProgressColumn(
                "Obras Concluidas",
                format="%d",
                min_value=0,
                max_value=int(df_conc_f["Qtd Concluida"].max())
            )
        },
        height=300
    )
        
df_mensal_c = df[
    (df["Data_Conc"].notna()) & 
    (df["Data_Conc"].dt.year.isin(ano_sel if isinstance(ano_sel, list) else [ano_sel]))
].copy()

df_mensal_c["Mes_Num"] = df_mensal_c["Data_Conc"].dt.month
df_mensal_c["Mês"] = df_mensal_c["Data_Conc"].dt.strftime('%m-%b') # Ex: 01 - Jan

resumo_mensal_c = df_mensal_c.groupby(["Mes_Num", "Mês"]).size().reset_index(name="Quantidade")
resumo_mensal_c = resumo_mensal_c.sort_values("Mes_Num") # Garante ordem cronológica

with g4:

    st.markdown(f"Obras Concluidas por Mês - {ano_sel}")

#Criando o gráfico no Plotly
    fig = px.bar(
        resumo_mensal_c,
        x="Mês",
        y="Quantidade",
        text="Quantidade",  # <--- Aqui estão os seus RÓTULO
        color_discrete_sequence=["#060054"], # Cor azul padrão
        height=360
    )

    # Ajustes finos no layout
    fig.update_traces(textposition='outside') # Coloca o número acima da barra
    fig.update_layout(
        xaxis_title="Mês de Conclusão",
        yaxis_title="Qtd Obras",
        plot_bgcolor="rgba(0,0,0,0)", # Fundo transparente
        hovermode="x unified"
    )

    # 5. Exibir no Streamlit
    st.plotly_chart(fig, use_container_width=True)

g5,g6 = st.columns([1,4])

with g5:
    st.markdown(f"Quantidade por Status")

    if df_ener_f.empty:
        st.info("Nennhum dado encontrado para os filtros selecionados.")
    else:
        st.dataframe(
            df_status_f,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Qtd total": st.column_config.ProgressColumn(
                    "Obras total",
                    format="%d",
                    min_value=0,
                    max_value=int(df_status_f["Qtd total"].max())
                )
            },
            height=250
        )

df_legenda_filtro = df[
    (df["Data_Status_Atual"].dt.year.isin(ano_sel)) &
    (df["P.I"].isin(siglas_f)) &
    (df["Status"].isin(status_selecionado))
].copy()

df_legenda_f = df_legenda_filtro.groupby("Legenda")["4nvl"].count().reset_index()

df_legenda_f = df_legenda_f.sort_values("Legenda", ascending=False)
df_legenda_f.columns = ["Legenda","Qtd total"]
df_legenda_f = df_legenda_f.sort_values("Qtd total", ascending=False)

with g6:
    st.markdown(f"Tabela")
    df_exibição = df[["4nvl", "P.I", "DESCRIÇÃO", "Status", "Legenda"]]

    st.dataframe(
    df_exibição,
    hide_index=True,
    height=555
)

g7,g8 = st.columns([1,4])

with g5:
    st.markdown(f"Quantidade por Legenda")

    if df_legenda_f.empty:
        st.info("Nennhum dado encontrado para os filtros selecionados.")
    else:
        st.dataframe(
            df_legenda_f,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Qtd total": st.column_config.ProgressColumn(
                    "Obras total",
                    format="%d",
                    min_value=0,
                    max_value=int(df_legenda_f["Qtd total"].max())
                )
            },
            height=250
        )

st.divider()

w1,w2 = st.columns([4,1])

with w1:

    mapeamento_aic = {
    "ABER/ABER": "ENCERRAR", "LIB/ATEC": "ENCERRAR", "LIB/CONC": "ENCERRAR",
    "LIB/DEV": "ENCERRAR", "LIB/DFEC": "ENCERRAR", "LIB/ENER": "ENCERRAR",
    "LIB/LOG": "ENCERRAR", "LIB/PEND": "ENCERRAR",
    # Todos os outros são ENCERRADO
    }

# Criar coluna de classificação (Padrão 'ENCERRADO', altera se estiver no mapa acima)
    df["Classificacao_AIC"] = df["Status"].map(mapeamento_aic).fillna("ENCERRADO")

# 3. Filtrar pelo Ano Selecionado (Data_Log)
    df_aic = df[
    (df["Data_Log"].notna()) & 
    (df["Data_Log"].dt.year.isin(ano_sel))
    ].copy()

    df_aic["Mes_Num"] = df_aic["Data_Log"].dt.month
    df_aic["Mês"] = df_aic["Data_Log"].dt.strftime('%b')

# 4. Agrupar para o Gráfico
    resumo_aic = df_aic.groupby(["Mes_Num", "Mês", "Classificacao_AIC"]).size().reset_index(name="Qtd")
    resumo_aic = resumo_aic.sort_values("Mes_Num")

    fig_aic = px.bar(
    resumo_aic,
    x="Mês",
    y="Qtd",
    color="Classificacao_AIC",
    text="Qtd",
    title="Evolução de Obras Liberadas: Encerradas vs. Pendentes (AIC)",
    color_discrete_map={"ENCERRAR": "#B62208", "ENCERRADO": "#09BD02"}, # Vermelho para alerta, Azul para ok
    barmode="stack",
    height=475
    )

    fig_aic.update_layout(
    xaxis_title="Mês de Liberação (Logística)",
    yaxis_title="Qtd Obras",
    legend=dict(
        orientation="h",       # Orientação Horizontal
        yanchor="bottom",      # Ancora na base
        y=-0.3,                # Posição vertical (negativo para ficar abaixo do eixo X)
        xanchor="center",      # Ancora no centro
        x=0.5,                 # Posição horizontal centralizada
        title_text=""          # Remove o título da legenda se quiser ganhar espaço
    ),
    margin=dict(b=50)          # Aumenta a margem inferior para a legenda não cortar
    )
    st.plotly_chart(fig_aic, use_container_width=True)

with w2:
    # 1. Criar a tabela base de pendentes
    df_pendente = df_aic[df_aic["Classificacao_AIC"] == "ENCERRAR"]
    tabela_pi_aic = df_pendente.groupby("P.I").agg(
    Qtd_Pendente=("Status", "count")
    ).reset_index().sort_values("Qtd_Pendente", ascending=False)

# 2. Calcular o Total Geral
    total_obras = tabela_pi_aic["Qtd_Pendente"].sum()

# 3. Criar a linha de Total para o DataFrame
    linha_total = pd.DataFrame({
    "P.I": ["TOTAL GERAL"], 
    "Qtd_Pendente": [total_obras]
    })

# 4. Concatenar a tabela com a linha de total
# Usamos o ignore_index para não dar conflito de índices
    tabela_com_total = pd.concat([tabela_pi_aic, linha_total], ignore_index=True)

    st.markdown("##### 📋 Detalhamento AIC por P.I")

# 5. Exibir com formatação especial
    st.dataframe(
        tabela_com_total,
        use_container_width=True,
        hide_index=True,
        column_config={
            "P.I": st.column_config.TextColumn("P.I"),
            "Qtd_Pendente": st.column_config.NumberColumn(
                "Obras a Encerrar",
                format="%d",
                help="Soma total de obras com status de AIC",
                
            )
        }, height=425
    )