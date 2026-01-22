import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

df = pd.read_excel("Base_RD_16_01_26.xlsx")

st.set_page_config(page_title="Dashboard Obras RD", layout="wide")

st.title("""Dashboard Teste
         Esta pagina servirá para testes com Streamlit""")

#=========FILTROS==========

regional = st.multiselect(
    "Selecione a Regional",
    options=sorted(df["REGIONAL"].dropna().unique())
)

df_f = df.copy()
if regional:
    df_f = df_f[df_f["REGIONAL"].isin(regional)]


Situação = st.multiselect(
    "Selecione a Situação",
    options=sorted(df["Execução"].dropna().unique())
)

df_f = df.copy()
if Situação:
    df_f = df_f[df_f["Execução"].isin(Situação)]


parceira = st.multiselect(
    "Selecione a parceira",
    options=sorted(df["PARCEIRA"].dropna().unique())
)

df_f = df.copy()
if parceira:
    df_f = df_f[df_f["PARCEIRA"].isin(parceira)]



# ====== GRÁFICO DE BARRAS ======
st.subheader("Obras por Status")

graf = px.bar(
    df_f.groupby("Status").size().reset_index(name="Quantidade"),
    x="Status",
    y="Quantidade",
    text="Quantidade"
)

graf.update_traces(textposition="outside")

st.plotly_chart(graf, use_container_width=True)

st.button("Re-run")