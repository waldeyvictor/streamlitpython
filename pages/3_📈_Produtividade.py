import streamlit as st

# ====== CONFIG INICIO DE PAGINA ======

st.set_page_config(page_title="Produtividade", page_icon="📈", layout="wide")
st.markdown("### Produtividade - Primarizada")

import time
import numpy as np
import pandas as pd
import plotly.express as px

# ====== CACHE DE LEITURA ======
@st.cache_data
def load_data():
    return pd.read_excel("Serviços_GPM.xlsx")

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):
    df["data_servico"] = pd.to_datetime(df["data_servico"], errors="coerce")

    return df

df = preprocess(df)
# ====== FILTROS ======

w1, w2, w3 = st.columns(3)

with w1:
    prefixo = st.multiselect("des_equipe", sorted(df["des_equipe"].dropna().unique()))

with w2:
    meses = sorted(df["data_servico"].dropna().dt.month.unique())
    mes = st.multiselect("Mês", meses)

with w3:
    anos = sorted(df["data_servico"].dropna().dt.year.unique())
    ano = st.multiselect("Ano", anos)

df_f = df.copy()
if prefixo :
    df_f = df_f[df_f["des_equipe"].isin(prefixo)]

df_f = df.copy()
if mes :
    df_f = df_f[df_f["data_servico"].isin(mes)]


df_f = df.copy()
if mes :
    df_f = df_f[df_f["data_servico"].isin(mes)]

# ====== CONTEUDO ======
st.sidebar.header("Avanço Financeiro")

# ====== KPI ======

# ====== GRAFICOS ======

# q1, q2, q3 = st.columns(3)

# with q1:
#     alrluv204m = ["AL-RLU-V204M"]
#     df_alrluv204m = df_f[df_f["des_equipe"].isin(alrluv204m)]

#     st.markdown("### AL-RLU-V204M")

#     produtividade = (
#         df_alrluv204m.groupby("data_servico")["valor_total"]
#         .sum()
#         .reset_index(name="Produtividade")
#     )

#     fig = px.line(
#         produtividade,
#         x="data_servico",
#         y="Produtividade",
#         markers=True,
#         text=produtividade["Produtividade"].map(lambda x: f"{x:,.2f}")
#     )

#     fig.update_traces(textposition="top center")

#     st.plotly_chart(fig, use_container_width=True)

# with q2:
#     alpjao200m = ["AL-PJA-O200M"]
#     df_alpjao200m = df_f[df_f["des_equipe"].isin(alpjao200m)]

#     st.markdown("### AL-PJA-O200M")

#     produtividade = (
#         df_alpjao200m.groupby("data_servico")["valor_total"]
#         .sum()
#         .reset_index(name="Produtividade")
#     )

#     fig = px.line(
#         produtividade,
#         x="data_servico",
#         y="Produtividade",
#         markers=True,
#         text=produtividade["Produtividade"].map(lambda x: f"{x:,.2f}")
#     )

#     fig.update_traces(textposition="top center")

#     st.plotly_chart(fig, use_container_width=True)

# with q3:
#     alpcvo204m = ["AL-PCV-O204M"]
#     df_alpcvo204m = df_f[df_f["des_equipe"].isin(alpcvo204m)]

#     st.markdown("### AL-PCV-O204M")

#     produtividade = (
#         df_alpcvo204m.groupby("data_servico")["valor_total"]
#         .sum()
#         .reset_index(name="Produtividade")
#     )

#     fig = px.line(
#         produtividade,
#         x="data_servico",
#         y="Produtividade",
#         markers=True,
#         text=produtividade["Produtividade"].map(lambda x: f"{x:,.2f}")
#     )

#     fig.update_traces(textposition="top center")

#     st.plotly_chart(fig, use_container_width=True)


e1, e2 = st.columns(2)

with e1:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-RLU-V204M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alrluv204m = ["AL-RLU-V204M"]
    df_alrluv204m = df_f[df_f["des_equipe"].isin(alrluv204m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_alrluv204m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

with e2:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-PJA-O200M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alpjao200m = ["AL-PJA-O200M"]
    df_alpjao200m = df_f[df_f["des_equipe"].isin(alpjao200m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_alpjao200m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

r1, r2 = st.columns(2)

with r1:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-PCV-O204M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alpcvo204m = ["AL-PCV-O204M"]
    df_alpcvo204m = df_f[df_f["des_equipe"].isin(alpcvo204m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_alpcvo204m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

        # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

with r2:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-PCV-U201M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alpcvu201m = ["AL-PCV-U201M"]
    df_alpcvu201m = df_f[df_f["des_equipe"].isin(alpcvu201m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_alpcvu201m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

t1, t2 = st.columns(2)

with t1:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-TBM-O201N</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    altbmo201n = ["AL-TBM-O201N"]
    df_altbmo201n = df_f[df_f["des_equipe"].isin(altbmo201n)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_altbmo201n
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

with t2:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-TBM-O201M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    altbmo201m = ["AL-TBM-O201M"]
    df_altbmo201m = df_f[df_f["des_equipe"].isin(altbmo201m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_altbmo201m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

        # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

y1, y2 = st.columns(2)

with y1:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-TBM-O202M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    altbmo202m = ["AL-TBM-O202M"]
    df_altbmo202m = df_f[df_f["des_equipe"].isin(altbmo202m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_altbmo202m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

with y2:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-TBM-U202M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    altbmu202m = ["AL-TBM-U202M"]
    df_altbmu202m = df_f[df_f["des_equipe"].isin(altbmu202m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_altbmu202m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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

u1, u2 = st.columns(2)

with u1:

    # ====== TITULO ======

    st.markdown(
    "<h3 style='text-align: center;'>Produtividade Acumulada AL-TBM-V201M</h3>",
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    altbmv201m = ["AL-TBM-V201M"]
    df_altbmv201m = df_f[df_f["des_equipe"].isin(altbmv201m)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_altbmv201m
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 5000

    # ====== CRIA A META ACUMULADA DIARIA ======

    diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if diario.empty:
        realizado = 0
        meta = 0
        diario_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        diario_plot = diario.copy()
        realizado = diario["Produtividade_Acumulada"].iloc[-1]
        meta = diario["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)

    st.metric(
        "Produtividade Acumulada",
        f"R$ {realizado:,.2f}",
        delta=delta,
        delta_color="normal"
    )

    st.caption(f"Variação em relação à meta: R$ {delta:,.2f}")

     # ====== CRIA O GRAFICO ======

    fig = px.line(
        diario_plot,
        x="data_servico",
        y=["Produtividade_Acumulada", "Meta_Acumulada"],
        markers=True,
        labels={
            "value": "Valor (R$)",
            "variable": "Indicador"
        },
    )

    # ====== ADICIONA OS ROTULOS SOMENTE NO UTILMO PONTO DO GRAF ======

    for trace in fig.data:
        trace.text = [None] * (len(trace.y) - 1) + [f"{trace.y[-1]:,.2f}"]
        trace.textposition = "top center"
        trace.mode = trace.mode + "+text" 

    # ====== PONTILHAR LINHA DE META ======

    fig.update_traces(
        selector=dict(name="Meta_Acumulada"),
        line=dict(dash="dash")
    )

    # ====== CORRIGI POSIÇÃO DO INDICADOR DE LEGENDA ======

    fig.update_layout(
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
