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
    return df

df = preprocess(df)

coms = (df["Legenda"]=="COMS+").sum()
logistica = (df["Legenda"]=="LOGISTICA").sum()
cancelado = (df["Legenda"]=="CANCELADO").sum()
liberado = (df["Legenda"]=="LIBERADO").sum()
concluido = (df["Legenda"]=="CONCLUIDO").sum()
liberado_logistica = (df["Legenda"]=="LIBERADO LOGISTICA").sum()
devolvido_regional = (df["Legenda"]=="DEVOLVIDO REGIONAL").sum()

q1,q2,q3,q4,q5,q6,q7 = st.columns(7)

with q1:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Obras Coms</p>
        <h2 style="margin: 0; font-size: 34px;">{coms}</h2>
    </div>
    """, unsafe_allow_html=True)

with q2:
    st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Logisitica</p>
        <h2 style="margin: 0; font-size: 34px;">{logistica}</h2>
    </div>
    """, unsafe_allow_html=True)

with q3:
        st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Canceladas</p>
        <h2 style="margin: 0; font-size: 34px;">{cancelado}</h2>
    </div>
    """, unsafe_allow_html=True)
        
with q4:
        st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Liberadas</p>
        <h2 style="margin: 0; font-size: 34px;">{liberado}</h2>
    </div>
    """, unsafe_allow_html=True)
        
with q5:
        st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Concluidas</p>
        <h2 style="margin: 0; font-size: 34px;">{concluido}</h2>
    </div>
    """, unsafe_allow_html=True)
        
with q6:
        st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Lib Logistica</p>
        <h2 style="margin: 0; font-size: 34px;">{liberado_logistica}</h2>
    </div>
    """, unsafe_allow_html=True)
        
with q7:
        st.markdown(f"""
    <div style="
        background-color: #060054; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        color: white;
    ">
        <p style="margin: 0; font-size: 20px; font-weight: bold; opacity: 0.9;">Dev Regional</p>
        <h2 style="margin: 0; font-size: 34px;">{devolvido_regional}</h2>
    </div>
    """, unsafe_allow_html=True)