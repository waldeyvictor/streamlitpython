import streamlit as st

st.set_page_config(page_title="Programação Validação", page_icon="📈", layout="wide")
st.markdown(
    """
    <h3 style="
        text-align: center;
        background-color: #060054;
        color: white;
        padding: 10px;
        border-radius: 8px;
    ">
        Programação - Capex - Validação
    </h3>
    """,
    unsafe_allow_html=True
    )
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_excel("Carteira.xlsx", sheet_name="Carteira - CAPEX")

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):

    #df.columns = df.columns.str.strip() # Remove espaços dos nomes das colunas
    df["Data programação inspeção"] = pd.to_datetime(df["Data programação inspeção"], errors="coerce")
    df = df.dropna(subset=["Data programação inspeção"]) # Remove linhas sem data
    return df

df = preprocess(df)


