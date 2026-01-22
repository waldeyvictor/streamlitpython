import streamlit as st

# ====== CONFIG INICIO DE PAGINA ======

st.set_page_config(page_title="Avanço Financeiro", page_icon="📈", layout="wide")
st.markdown("### Avanço Financeiro - Primarizada")

import time
import numpy as np
import pandas as pd
import plotly.express as px

# ====== CACHE DE LEITURA ======
@st.cache_data
def load_data():
    return pd.read_excel("Base_RD.xlsx")

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):
    df["Data_Ener"] = pd.to_datetime(df["Data_Ener"], errors="coerce")
    df["Data_Status_Atual"] = pd.to_datetime(df["Data_Status_Atual"], errors="coerce")
    df["Data_Conc"] = pd.to_datetime(df["Data_Conc"], errors="coerce")
    return df

df = preprocess(df)

# ====== FILTROS ======

col1,col2,col3,col4 = st.columns(4)


with col1:
    status = st.multiselect("Status", sorted(df["Status"].dropna().unique()))
with col2:
    parceira = st.multiselect("PARCEIRA", sorted(df["PARCEIRA"].dropna().unique()))
with col3:
    anos = sorted(df["Data_Ener"].dropna().dt.year.unique())
    ano = st.multiselect("Ano", anos)
with col4:
    meses = sorted(df["Data_Ener"].dropna().dt.month.unique())
    mes = st.multiselect("Mês", meses)

df_f = df.copy()
if status :
    df_f = df_f[df_f["Status"].isin(status)]

if parceira :
    df_f = df_f[df_f["PARCEIRA"].isin(parceira)]

if ano :
    df_f = df_f[df_f["Data_Ener"].dt.year.isin(ano)]

if mes :
    df_f = df_f[df_f["Data_Ener"].dt.month.isin(mes)]



# ====== CONTEUDO ======
st.sidebar.header("Avanço Financeiro")

# ====== KPI ======

def kpi(titulo, valor, icone=""):
    st.markdown(
        f"""
        <div style="
            background:#060054;
            padding:0px;
            border-radius:15px;
            text-align:center;
            box-shadow:0 0 10px rgba(0,0,0,0.3);
        ">
            <h4 style="color:#9CA3AF;margin-bottom:0px;">{icone} {titulo}</h4>
            <h1 style="color:#F9FAFB;margin:0;">{valor}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

k1, k2 = st.columns(2)
obras_ener = df_f.groupby("Data_Ener")["4nvl"].nunique().reset_index(name="Quantidade")
#k1.metric("Obras Energizadas", obras_ener["Quantidade"].sum())
obras_conc = df_f.groupby("Data_Conc")["4nvl"].nunique().reset_index(name="Quantidade1")
#k2.metric("Obras concluidas", obras_conc["Quantidade1"].sum())

with k1:
    kpi("Obras Energizadas", obras_ener["Quantidade"].sum(), "⚡")

with k2:
    kpi("Obras Concluidas", obras_conc["Quantidade1"].sum(), "🏁")

# ====== GRAFICOS ======

q1, q2 = st.columns(2)

with q1:
    st.title("Energização por mês")
    fig = px.line(
        df_f.groupby("Data_Ener")["4nvl"].nunique().reset_index(name="Quantidade"),
        x="Data_Ener",
        y="Quantidade",
        markers=True,
        text="Quantidade"
    )

    fig.update_traces(textposition="top center")

    st.plotly_chart(fig, use_container_width=True)

with q2:
    st.title("Conclusão por mês")
    base = df_f.groupby("Data_Conc")["4nvl"].nunique().reset_index(name="Quantidade")
    fig = px.bar(base, x="Data_Conc", y="Quantidade", text="Quantidade")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    