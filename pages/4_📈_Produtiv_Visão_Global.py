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
inicio_mes = hoje.replace(day=1)
calendario_D = pd.DataFrame({
     "data_servico": pd.date_range(start=inicio_mes, end=hoje, freq="D")
})

calendario_B = pd.DataFrame({
    "data_servico": pd.date_range(
        start=inicio_mes,
        end=hoje,
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

alrluv204m = ["AL-PJA-O200M","AL-PCV-O204M","AL-TBM-O201N","AL-TBM-O201M","AL-TBM-O202M","AL-RLU-V204M","AL-TBM-V201M","AL-PCV-T202M","AL-PCV-U201M","AL-TBM-U202M"]
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

meta_diaria = 28649.28
calendario_B["Meta_Dia"] = meta_diaria
calendario_B["Meta_Acumulada"] = calendario_B["Meta_Dia"].cumsum()

base_final = calendario_B.merge(
diario,
on="data_servico",
how="left"
)

# ====== CRIA A META ACUMULADA DIARIA ======

#diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)
base_final["Produtividade_Dia"] = base_final["Produtividade_Dia"].fillna(0)
base_final["Produtividade_Acumulada"] = base_final["Produtividade_Dia"].cumsum()

# ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

if base_final.empty:
    realizado = 0
    meta = calendario_B["Meta_Acumulada"].iloc[-1]
    base_final_plot = pd.DataFrame({
    "data_servico": [],
    "Produtividade_Acumulada": [],
    "Meta_Acumulada": []
})
    
else:
    base_final_plot = base_final.copy()
    realizado = base_final_plot["Produtividade_Acumulada"].iloc[-1]
    meta = base_final_plot["Meta_Acumulada"].iloc[-1]
    
# ====== CRIA O KPI PARA ACOMPANHAMENTO ======

delta = round(realizado - meta, 2)
media = base_final["Produtividade_Dia"].mean()

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

fig = px.line(
    base_final_plot,
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


e1, e2 = st.columns(2)

with e1:

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
        LINHA MORTA
    </h5>
    """,
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alrluv204m = ["AL-PJA-O200M","AL-PCV-O204M","AL-TBM-O201N","AL-TBM-O201M","AL-TBM-O202M"]
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

    meta_diaria = 19595.72
    calendario_B["Meta_Dia"] = meta_diaria
    calendario_B["Meta_Acumulada"] = calendario_B["Meta_Dia"].cumsum()

    base_final = calendario_B.merge(
    diario,
    on="data_servico",
    how="left"
    )

    # ====== CRIA A META ACUMULADA DIARIA ======

    #diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)
    base_final["Produtividade_Dia"] = base_final["Produtividade_Dia"].fillna(0)
    base_final["Produtividade_Acumulada"] = base_final["Produtividade_Dia"].cumsum()

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if base_final.empty:
        realizado = 0
        meta = calendario_B["Meta_Acumulada"].iloc[-1]
        base_final_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        base_final_plot = base_final.copy()
        realizado = base_final_plot["Produtividade_Acumulada"].iloc[-1]
        meta = base_final_plot["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)
    media = base_final["Produtividade_Dia"].mean()

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

    fig = px.line(
        base_final_plot,
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
    """
    <h5 style="
        text-align: center;
        background-color: #060054;
        color: white;
        padding: 10px;
        border-radius: 8px;
    ">
        LINHA VIVA
    </h5>
    """,
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alrluv204m = ["AL-RLU-V204M","AL-TBM-V201M"]
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

    meta_diaria = 5480.02
    calendario_B["Meta_Dia"] = meta_diaria
    calendario_B["Meta_Acumulada"] = calendario_B["Meta_Dia"].cumsum()

    base_final = calendario_B.merge(
    diario,
    on="data_servico",
    how="left"
    )

    # ====== CRIA A META ACUMULADA DIARIA ======

    #diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)
    base_final["Produtividade_Dia"] = base_final["Produtividade_Dia"].fillna(0)
    base_final["Produtividade_Acumulada"] = base_final["Produtividade_Dia"].cumsum()

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if base_final.empty:
        realizado = 0
        meta = calendario_B["Meta_Acumulada"].iloc[-1]
        base_final_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        base_final_plot = base_final.copy()
        realizado = base_final_plot["Produtividade_Acumulada"].iloc[-1]
        meta = base_final_plot["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)
    media = base_final["Produtividade_Dia"].mean()

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

    fig = px.line(
        base_final_plot,
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

e3, e4 = st.columns(2)

with e3:

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
        TAT
    </h5>
    """,
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    alrluv204m = ["AL-PCV-T202M"]
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

    meta_diaria = 2095.02
    calendario_B["Meta_Dia"] = meta_diaria
    calendario_B["Meta_Acumulada"] = calendario_B["Meta_Dia"].cumsum()

    base_final = calendario_B.merge(
    diario,
    on="data_servico",
    how="left"
    )

    # ====== CRIA A META ACUMULADA DIARIA ======

    #diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)
    base_final["Produtividade_Dia"] = base_final["Produtividade_Dia"].fillna(0)
    base_final["Produtividade_Acumulada"] = base_final["Produtividade_Dia"].cumsum()

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if base_final.empty:
        realizado = 0
        meta = calendario_B["Meta_Acumulada"].iloc[-1]
        base_final_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        base_final_plot = base_final.copy()
        realizado = base_final_plot["Produtividade_Acumulada"].iloc[-1]
        meta = base_final_plot["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)
    media = base_final["Produtividade_Dia"].mean()

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

    fig = px.line(
        base_final_plot,
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

with e4:
    
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
        EQUIPE LEVE
    </h5>
    """,
    unsafe_allow_html=True
    )

    # ====== DEFINE FILTRO FIXO ======

    equipe_leve = ["AL-PCV-U201M","AL-TBM-U202M"]
    df_equipe_leve = df_f[df_f["des_equipe"].isin(equipe_leve)]

    # ====== CRIA UM NOVO DF PARA SOMAR AS PRODUTIVIDAS DIARIAS ======

    diario = (
        df_equipe_leve
        .groupby("data_servico")["valor_total"]
        .sum()
        .reset_index(name="Produtividade_Dia")
        .sort_values("data_servico")
    )

    # ====== CRIA UMA NOVA COLUNA QUE SOMA AS PRODUTIVIDADES DIARIAS, GERANDO ASSIM O ACUMULADO ======

    diario["Produtividade_Acumulada"] = diario["Produtividade_Dia"].cumsum()

    # ====== META DIARIA DEFINIDA MANUALMENTE ======

    meta_diaria = 1480
    calendario_B["Meta_Dia"] = meta_diaria
    calendario_B["Meta_Acumulada"] = calendario_B["Meta_Dia"].cumsum()

    base_final = calendario_B.merge(
    diario,
    on="data_servico",
    how="left"
    )

    # ====== CRIA A META ACUMULADA DIARIA ======

    #diario["Meta_Acumulada"] = meta_diaria*np.arange(1, len(diario) + 1)
    base_final["Produtividade_Dia"] = base_final["Produtividade_Dia"].fillna(0)
    base_final["Produtividade_Acumulada"] = base_final["Produtividade_Dia"].cumsum()

    # ====== ARMAZENA O UTILMO VALOR DO ACUMULADO DENTRO DA VARIAVEL ======

    if base_final.empty:
        realizado = 0
        meta = calendario_B["Meta_Acumulada"].iloc[-1]
        base_final_plot = pd.DataFrame({
        "data_servico": [],
        "Produtividade_Acumulada": [],
        "Meta_Acumulada": []
    })
        
    else:
        base_final_plot = base_final.copy()
        realizado = base_final_plot["Produtividade_Acumulada"].iloc[-1]
        meta = base_final_plot["Meta_Acumulada"].iloc[-1]
        
    # ====== CRIA O KPI PARA ACOMPANHAMENTO ======

    delta = round(realizado - meta, 2)
    media = base_final["Produtividade_Dia"].mean()

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

    fig = px.line(
        base_final_plot,
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
