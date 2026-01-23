import pandas as pd

# ====== LEITURA DAS PLANILHAS ======
servicos = pd.read_excel("Serviços_GPM.xlsx")
caderno = pd.read_excel("Caderno.xlsx")

# ====== NORMALIZA NOMES (SEGURANÇA) ======
servicos["cod_atividade"] = servicos["cod_atividade"].astype(str).str.strip()
caderno["Código Serviço"] = caderno["Código Serviço"].astype(str).str.strip()

# ====== GARANTE NUMÉRICOS ======
servicos["qtd_atividade"] = pd.to_numeric(
    servicos["qtd_atividade"], errors="coerce"
)

servicos["valor_unitario"] = pd.to_numeric(
    servicos["valor_unitario"], errors="coerce"
)

caderno["valor_servico"] = pd.to_numeric(
    caderno.iloc[:, 2],  # coluna C
    errors="coerce"
)

# ====== CRIA MAPA CÓDIGO → VALOR ======
mapa_valores = dict(zip(
    caderno["Código Serviço"],
    caderno["valor_servico"]
))

# ====== NOVO VALOR (PODE SER NaN) ======
novo_valor = servicos["cod_atividade"].map(mapa_valores)

# ====== MANTÉM O VALOR ANTIGO SE NÃO EXISTIR NO CADERNO ======
servicos["valor_unitario"] = novo_valor.combine_first(
    servicos["valor_unitario"]
)

# ====== RECALCULA O VALOR TOTAL (AK) ======
servicos["valor_total"] = (
    servicos["valor_unitario"] * servicos["qtd_atividade"]
)

# ====== SALVA O ARQUIVO FINAL ======
servicos.to_excel("Serviços_GPM_atualizado.xlsx", index=False)