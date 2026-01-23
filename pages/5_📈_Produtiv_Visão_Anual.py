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
        Produtividade - Capex - Visão Global
    </h3>
    """,
    unsafe_allow_html=True
    )
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ====== CACHE DE LEITURA ======
@st.cache_data
def load_data():
    return pd.read_excel("Serviços_GPM_atualizado.xlsx")

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):
    df["data_servico"] = pd.to_datetime(df["data_servico"], errors="coerce")
    return df

df = preprocess(df)

hoje = pd.Timestamp.today().normalize()
ano_ref = hoje.year
inicio_ano = pd.Timestamp(year=ano_ref, month=1, day=1)
fim_ano = pd.Timestamp(year=ano_ref, month=12, day=31)
inicio_mes = hoje.replace(day=1)
calendario_D = pd.DataFrame({
     "data_servico": pd.date_range(start=inicio_mes, end=hoje, freq="D")
})

calendario_B = pd.DataFrame({
    "data_servico": pd.date_range(
        start=inicio_ano,
        end=fim_ano,
        freq="B"  # B = Business Day (Seg–Sex)
    )
})

# ====== FILTROS ======

w1, w2, w3, w4 = st.columns(4)

with w1:
    meses = sorted(df["data_servico"].dropna().dt.month.unique())
    mes = st.multiselect("Mês", meses)

with w2:
    anos = sorted(df["data_servico"].dropna().dt.year.unique())
    ano = st.multiselect("Ano", anos)

df_f = df.copy()

if mes :
    df_f = df_f[df_f["data_servico"].dt.month.isin(mes)]

if ano :
    df_f = df_f[df_f["data_servico"].dt.year.isin(ano)]

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ====== CONTEUDO ======

# ====== KPI ======

# ====== GRAFICOS =======

# ====== TITULO ======

st.markdown(
"""
<h5 style="
    text-align: center;
    background-color: #060054;
    color: white;
    padding: 10px;
    border-radius: 8px;
">
    VISÃO GLOBAL
</h5>
""",
unsafe_allow_html=True
)

# ====== DEFINE FILTRO FIXO ======

equipes = ["AL-PJA-O200M","AL-PCV-O204M","AL-TBM-O201N","AL-TBM-O201M","AL-TBM-O202M","AL-RLU-V204M","AL-TBM-V201M","AL-PCV-T202M","AL-PCV-U201M","AL-TBM-U202M"]
df_equipes = df_f[df_f["des_equipe"].isin(equipes)]

# ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

df_equipes = df_f[df_f["des_equipe"].isin(equipes)].copy()

df_equipes["ano"] = df_equipes["data_servico"].dt.year
df_equipes["mes"] = df_equipes["data_servico"].dt.month
df_equipes["mes_nome"] = df_equipes["data_servico"].dt.strftime("%b")

# ====== PRODUTIVIDADE MENSAL ======
mensal = (
    df_equipes
    .groupby(["ano", "mes", "mes_nome"], as_index=False)
    .agg(Produtividade_Mes=("valor_total", "sum"))
    .sort_values("mes")
)

mensal["Produtividade_Acumulada"] = mensal["Produtividade_Mes"].cumsum()

# ====== PRODUTIVIDADE ACUMULADA NO ANO ======
mensal["Produtividade_Acumulada"] = mensal["Produtividade_Mes"].cumsum()

# ====== DIAS ÚTEIS POR MÊS ======

dias_uteis_mes = (
    df_equipes
    .drop_duplicates("data_servico")
    .groupby("mes")["data_servico"]
    .count()
    .reset_index(name="dias_uteis")
)

base_meses = pd.DataFrame({
    "mes": range(1, 13),
    "mes_nome": pd.date_range(
        start=f"{ano_ref}-01-01",
        periods=12,
        freq="MS"
    ).strftime("%b")
})

# ====== META MENSAL ======
meta_mensal = 787855.44
base_meses["Meta_Mes"] = meta_mensal
base_meses["Meta_Acumulada"] = base_meses["Meta_Mes"].cumsum()

# ====== JUNTA COM BASE MENSAL ======
mensal = base_meses.merge(
    mensal,
    on=["mes", "mes_nome"],
    how="left"
)

mensal["Produtividade_Mes"] = mensal["Produtividade_Mes"].fillna(0)
mensal["Produtividade_Acumulada"] = mensal["Produtividade_Mes"].cumsum()

# ====== META ACUMULADA NO ANO ======
mensal["Meta_Acumulada"] = mensal["Meta_Mes"].cumsum()

# ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

if df_equipes.empty:
    realizado = 0
    meta = calendario_B["Meta_Acumulada"].iloc[-1]
    base_final_plot = pd.DataFrame({
    "data_servico": [],
    "Produtividade_Acumulada": [],
    "Meta_Acumulada": []
})
    
else:
    base_final_plot = df_equipes.copy()
    realizado = mensal.loc[mensal["Produtividade_Mes"] > 0,"Produtividade_Acumulada"].iloc[-1]
    meta = mensal["Meta_Acumulada"].iloc[-1]
    
# ====== CRIA O KPI PARA ACOMPANHAMENTO ======

delta = round(realizado - meta, 2)
media = mensal.loc[mensal["Produtividade_Mes"] > 0,"Produtividade_Mes"].mean()

a1, a2, a3 = st.columns(3)

with a1:
    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )
with a2:
    st.metric(
        "Meta Acumulada",
        f"R$ {meta:,.2f}"
    )
with a3:
    st.metric(
        "Media de produtividade",
        f"R$ {media:,.2f}"
    )
st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

    # ====== CRIA O GRAFICO ======
fig = go.Figure()

fig.add_bar(
    x=mensal["mes_nome"],
    y=mensal["Produtividade_Acumulada"],
    name="Produtividade Acumulada",
    text=[f"{v:,.2f}" if v > 0 else "" for v in mensal["Produtividade_Acumulada"]],
    textposition="outside"
)

fig.add_trace(
    go.Scatter(
        x=mensal["mes_nome"],
        y=mensal["Meta_Acumulada"],
        mode="lines+markers",
        name="Meta Acumulada",
        line=dict(dash="dash")
    )
)

# ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

fig.update_layout(
    yaxis_title="Valor (R$)",
    xaxis_title="Mês",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5,
        title_text=""
    )
)

# ====== RENDERIZA O GRAFICO NO STREAMLIT ======

st.plotly_chart(fig, use_container_width=True)