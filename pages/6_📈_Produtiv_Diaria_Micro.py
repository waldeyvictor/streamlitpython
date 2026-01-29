import streamlit as st

# ====== CONFIG INICIO DE PAGINA ======

st.set_page_config(page_title="Produtividade", page_icon="📈", layout="wide")

st.markdown(
    """
    <h3 style="
        text-align: center;
        background-color: #060054;
        color: white;
        padding: 10px;
        border-radius: 8px;
    ">
        Produtividade - Capex - Visão Micro
    </h3>
    """,
    unsafe_allow_html=True
    )

st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ====== METAS EQUIPES ======

metas_equipes = {
    "AL-RLU-V204M": 2740.01,
    "AL-PJA-O200M": 3919.14,
    "AL-PCV-O204M": 3919.14,
    "AL-PCV-U201M": 739.26,
    "AL-PCV-T202M": 2095.02,
    "AL-TBM-O201N": 3919.14,
    "AL-TBM-O201M": 3919.14,
    "AL-TBM-O202M": 3919.14,
    "AL-TBM-U202M": 739.26,
    "AL-TBM-V201M": 2740.01
}

# ====== CACHE DE LEITURA ======
@st.cache_data
def load_data():
    return pd.read_excel("Serviços_GPM_atualizado.xlsx")

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):
    df["data_servico"] = pd.to_datetime(df["data_servico"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    def ajustar_coordenada(valor):
        if pd.isna(valor) or valor == 0:
            return valor
        # Se for um inteiro longo (ex: -9000000...)
        if abs(valor) > 100:
            return valor / 1_000_000 # Ajuste a quantidade de zeros conforme seus dados
        return valor

    df["latitude"] = df["latitude"].apply(ajustar_coordenada)
    df["longitude"] = df["longitude"].apply(ajustar_coordenada)

    return df

df = preprocess(df)

# ===== Filtros ======

equipes = list(metas_equipes.keys())
q1,q2 = st.columns([1,6])

with q1:
    data_selecionada = st.date_input("Selecione o Dia", df["data_servico"].max(),format="DD/MM/YYYY")

with q2:
    equipe_selecionada = st.multiselect("Selecione a(s) equipe(s)", options=equipes, default=equipes)


mask_data = (df["data_servico"].dt.date == data_selecionada)
mask_equipe = (df["des_equipe"].isin(equipe_selecionada))
df_final = df[mask_data & mask_equipe].copy()

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

produtividade = df_final["valor_total"].sum()
meta_dia = sum(metas_equipes.get(e,0) for e in equipe_selecionada)
diferenca = produtividade - meta_dia
media = produtividade / len(equipe_selecionada) if equipe_selecionada else 0

s1,s2,s3,s4 = st.columns(4)

with s1:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">PRODUTIVIDADE DO DIA 💸</p>
        <h2 style="margin: 0; font-size: 34px;">R$ {produtividade:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)
    
with s2:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">META DO DIA 📈</p>
        <h2 style="margin: 0; font-size: 34px;">R$ {meta_dia:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)

cor_dif = "#28a745" if diferenca >= 0 else "#dc3545" # Verde se >= 0, Vermelho se < 0
with s3:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">DIF 📊</p>
        <h2 style="margin: 0; font-size: 34px; color:{cor_dif};">R$ {diferenca:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)

with s4:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">MEDIA POR EQUIPE 🚚</p>
        <h2 style="margin: 0; font-size: 34px;">R$ {media:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)
    
df_grafico = df_final.groupby("des_equipe")["valor_total"].sum().reset_index()
df_grafico["meta"] = df_grafico["des_equipe"].map(metas_equipes)
df_grafico = df_grafico.sort_values(by="valor_total", ascending=False)

fig = go.Figure()

d1,d2 = st.columns(2)

with d1:

    fig.add_trace(go.Bar(
        x=df_grafico["des_equipe"],
        y=df_grafico["valor_total"],
        name="Produtividade Equipes",
        marker_color="#060054",
        text=df_grafico["valor_total"].apply(lambda x: f"R${x:,.2f}"),
        textposition="auto"))

    fig.add_trace(go.Scatter(
        x=df_grafico["des_equipe"],
        y=df_grafico["meta"],
        name="Meta Individual",
        mode="markers",
        marker=dict(color="#FF0000", size=15, symbol="line-ew", line=dict(width=4)),
        hovertemplate="Meta: R$ %{y:,.2f}"
    ))

    fig.update_layout(
        title="📊 Produção vs Meta por Equipe",
        xaxis_title="Equipes",
        yaxis_title="Valor (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

with d2:
    st.markdown("### 🗺️ Mapa de Atividades por Equipe")

    df_final["lat_mapa"] = df_final["latitude"]
    df_final["long_mapa"] = df_final["longitude"]

    fig_mapa = px.scatter_mapbox(
        df_final, 
        lat="lat_mapa",     # Apenas o nome da coluna entre aspas
        lon="long_mapa",    # Apenas o nome da coluna entre aspas
        hover_name="des_equipe", 
        hover_data={
            "cod_atividade": True, 
            "valor_total": ":.2f", 
            "lat_mapa": False, 
            "long_mapa": False
        },
        color="des_equipe",
        zoom=6, 
        height=490
    )

    fig_mapa.update_layout(mapbox_style="carto-positron")

    fig_mapa.update_traces(marker=dict(size=8))
    st.plotly_chart(fig_mapa, use_container_width=True)

d3,d4 = st.columns(2)

with d3:

    st.markdown("### 📝 Detalhamento da Produção")

    colunas = ["des_equipe", "data_servico", "cod_atividade","des_atividade","qtd_atividade", "valor_total"]

    # Exibe o DataFrame filtrado
    st.dataframe(
        df_final[colunas], 
        use_container_width=True, # Faz a tabela ocupar a largura toda da tela
        hide_index=True,
        height=400          # Esconde aquela coluna de números à esquerda
    )

with d4:

    st.markdown("### 🏆 Ranking de Equipes")

    # Criando um resumo para a tabela
    ranking = df_final.groupby("des_equipe")["valor_total"].sum().reset_index()
    ranking["Meta"] = ranking["des_equipe"].map(metas_equipes)
    ranking["Atingimento %"] = (ranking["valor_total"] / ranking["Meta"]) * 100

    # Exibindo com formatação de cores e moeda
    st.dataframe(
        ranking.style.format({
            "valor_total": "R$ {:,.2f}",
            "Meta": "R$ {:,.2f}",
            "Atingimento %": "{:.1f}%"}).highlight_max(subset=["valor_total"],
        color="#B2EBF2"), 
        use_container_width=True
    )