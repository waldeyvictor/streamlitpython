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

df = df[df["VALIDAÇÃO"]=="EQUATORIAL"].copy()
df = df[df["ORDEM"]=="I"].copy()

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

# df["Legenda"] = df["Status"].map(Legenda)

df_apoio = pd.DataFrame.from_dict(Legenda)

df_final = df.merge(df_apoio, on="Status", how="left")

df_final.to_excel(r"teste.xlsx", index=False)