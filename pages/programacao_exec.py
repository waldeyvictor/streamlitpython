import streamlit as st

st.set_page_config(page_title="Programação Execução", page_icon="📈", layout="wide")
st.markdown(
    """
    <h3 style="
        text-align: center;
        background-color: #060054;
        color: white;
        padding: 10px;
        border-radius: 8px;
    ">
        Programação - Capex - Execução
    </h3>
    """,
    unsafe_allow_html=True
    )
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_excel("Programacao.xlsx", skiprows=1)

df = load_data()

# ====== CACHE DE PRÉ-PROCESSAMENTO ======
@st.cache_data
def preprocess(df):

    df.columns = df.columns.str.strip() # Remove espaços dos nomes das colunas
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"]) # Remove linhas sem data
    df["Equipe"] = df["Equipe"].astype(str).str.strip()
    df["Serviço"] = df["Serviço"].fillna("DISPONÍVEL / VAZIO").astype(str).str.strip()
    return df

df = preprocess(df)

# ====== FILTROS ======

st.markdown("Selecione mês e ano para facilitar as visualizações:")

w1, w2, w3, w4, w5, w6 = st.columns(6)

with w1:
    meses = sorted(df["Data"].dropna().dt.month.unique())
    mes = st.multiselect("Mês", meses)

with w2:
    anos = sorted(df["Data"].dropna().dt.year.unique())
    ano = st.multiselect("Ano", anos)

df_f = df.copy()

if mes :
    df_f = df_f[df_f["Data"].dt.month.isin(mes)]

if ano :
    df_f = df_f[df_f["Data"].dt.year.isin(ano)]

inicio = df_f["Data"].min()
fim = df_f["Data"].max()
calendario_B = pd.DataFrame({
    "Data": pd.date_range(
        start=inicio,
        end=fim,
        freq="D"
    )
})

# st.subheader("📅 Matriz de Ocupação da Semana")

# # Criar uma tabela dinâmica (Pivot Table)
equipes = ["AL-PJA-O200M","AL-PCV-O204M","AL-TBM-O201N","AL-TBM-O201M","AL-TBM-O202M","AL-RLU-V204M","AL-TBM-V201M","AL-PCV-T202M","AL-PCV-U201M","AL-TBM-U202M"]

df_f = df_f[df_f["Equipe"].isin(equipes)].copy()

df_pivot = df_f.pivot_table(
    index="Equipe",
    columns=df_f["Data"].dt.strftime('%d/%m/%y'), 
    values="Serviço", 
    aggfunc=lambda x: "✅" if any(i != "DISPONÍVEL / VAZIO" for i in x) else "⬜"
).fillna("⬜")

# st.dataframe(df_pivot, use_container_width=True)
# st.caption("✅ Programado | ⬜ Disponível")

st.subheader("📅 Matriz de Ocupação da Semana")

# 2. Resetar o índice para que 'Equipe' seja a coluna 0 e as Datas comecem na coluna 1
df_exibicao = df_pivot.reset_index()

# 3. Exibir com seleção de coluna
evento_selecao = st.dataframe(
    df_exibicao, 
    use_container_width=True,
    on_select="rerun", 
    selection_mode="single-column",
    hide_index=True # Esconde o índice numérico do pandas
)

st.caption("✅ Programado | ⬜ Disponível")


# --- LÓGICA DE DETALHAMENTO CORRIGIDA E SIMPLIFICADA ---
if len(evento_selecao.selection.columns) > 0:
    # O Streamlit retorna o nome da coluna (ex: "27/01/26") diretamente
    data_selecionada = evento_selecao.selection.columns[0]
    
    # Se o usuário clicar na coluna 'Equipe', ignoramos o detalhamento
    if data_selecionada == 0:
        st.info("Clique em uma data (coluna com ✅ ou ⬜) para ver a programação do dia.")
    else:
        
        st.markdown(f"### 📋 Programação Geral - Dia **{data_selecionada}**")
        
        # Filtramos no DataFrame original usando a string da data formatada
        df_dia = df_f[
            (df_f["Data"].dt.strftime('%d/%m/%y') == data_selecionada) & 
            (df_f["Serviço"] != "DISPONÍVEL / VAZIO")
        ]
        
        if not df_dia.empty:
            st.dataframe(
                df_dia[["Equipe", "Responsável pela programação", "Serviço", "Status do Serviço", "Quantidade Programada","Quantidade Executada", "Valor MO Previsto"]],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning(f"Sem serviços programados para as equipes selecionadas no dia {data_selecionada}.")
else:
    st.info("Selecione uma coluna, referente a uma data, para ver o detalhe da programação no dia.")

st.divider()

st.subheader("📈 Tendência de Valor MO Previsto")

# Agrupando por data
df_evolucao = df_f.groupby("Data")["Valor MO Previsto"].sum().reset_index()
df_f["Valor MO Previsto"] = pd.to_numeric(df_f["Valor MO Previsto"], errors="coerce").fillna(0)
total_mo_previsto = df_f["Valor MO Previsto"].sum()

valor_meta = 28500
delta = 859478.66

delta =  round(total_mo_previsto - delta,2)

st.metric(
        label="Soma MO Programada", 
        value=f"R$ {total_mo_previsto:,.2f}",
        help="Soma total do valor de mão de obra previsto para as equipes e período selecionados.",
        delta=f"R$ {delta}",
        delta_color="inverse"
    )

fig_linha = px.line(
    df_evolucao, 
    x="Data", 
    y="Valor MO Previsto",
    title="Valor Total Previsto por Dia",
    markers=True, # Adiciona pontos na linha
    line_shape="spline", # Deixa a linha curvada/suave
    color_discrete_sequence=["#060054"]
)

fig_linha.add_hline(
    y=valor_meta, 
    line_dash="dot", # Estilo pontilhado
    annotation_text=f"Meta Diária: R$ {valor_meta:,.2f}", 
    annotation_position="top left",
    line_color="red"
)

# Ajuste para mostrar Real (R$) no eixo Y
fig_linha.update_layout(yaxis_tickprefix="R$ ", yaxis_tickformat=",.2f",hovermode="x unified")
st.plotly_chart(fig_linha, use_container_width=True)
