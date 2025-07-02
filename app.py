"""Aplicativo Streamlit para 
controle de lucros reais de motoristas de aplicativos."""

import streamlit as st          # Interface web
import pandas as pd             # Manipulação de dados tabulares - Diario de Bordo
import os                       # Operating System permite interações com o sistema operacional.
from datetime import datetime   # Registro da data atual

# Configura o título da aba e o layout centralizado da interface web.
st.set_page_config(page_title="LucroCerto", layout="centered")

# Título e introdução do app
st.title("📊 Lucro certo – Controle de Ganhos para Motoristas de Aplicativos")
st.write("Bem-vindo ao seu painel de controle de ganhos diários!")
st.markdown("Insira seus dados para acompanhar o lucro real e o quanto falta para bater sua meta.")

# Inicializando campos no session_state
# Aqui, garantimos que todos os campos comecem vazios sempre que o app for aberto ou atualizado.
for campo in ["faturamento", "km_rodado", "combustivel", "outros_custos", "meta_diaria"]:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# Entradas como texto para permitir campos vazios
faturamento = st.text_input("Faturamento Bruto (R$)", value=st.session_state.faturamento, key="faturamento")
km_rodado = st.text_input("Total de KM rodados", value=st.session_state.km_rodado, key="km_rodado")
combustivel = st.text_input("Gasto com combustível (R$)", value=st.session_state.combustivel, key="combustivel")
outros_custos = st.text_input("Outros custos (R$)", value=st.session_state.outros_custos, key="outros_custos")
meta_diaria = st.text_input("Meta de Faturamento Diário (R$)", value=st.session_state.meta_diaria, key="meta_diaria")

# Passa a controlar o valor digitado usando st.session_state,
# que é como uma memória temporária do app.
# Agora conseguimos:
# Limpar os campos usando st.session_state["faturamento"] = ""
# Recuperar os dados depois que o usuário clicou em salvar ou calcular
# Preencher automaticamente os campos, caso necessário


# Validação e Cálculos
# Cria um botão para ativar os cálculos. O código dentro dele só roda quando esse botão for clicado.
if st.button("💰 Calcular Lucro Diário"):
    campos = [faturamento, km_rodado, combustivel, outros_custos, meta_diaria]

# Valida se todos os campos foram preenchidos.
    if "" in campos:
        st.error("🚨 Por favor, preencha todos os campos antes de calcular.")
    else:
        # Conversão de str para float
        faturamento = float(faturamento)
        km_rodado = float(km_rodado)
        combustivel = float(combustivel)
        outros_custos = float(outros_custos)
        meta_diaria = float(meta_diaria)
        # Cálculos
        custo_total = combustivel + outros_custos
        lucro = faturamento - custo_total
        falta_meta = max(meta_diaria - faturamento, 0)

        # Respostas do app
        st.success(f"🧾 Lucro do dia: R$ {lucro:.2f}")
        if km_rodado > 0:
            lucro_km = lucro / km_rodado
            st.info(f"💸 Lucro por KM: R$ {lucro_km:.2f}")
        st.success(f"💰 Lucro Real: R$ {lucro:.2f}")
        st.info(f"📉 Ainda faltam R$ {falta_meta:.2f} para bater sua meta.")

# Salvar os resultados no session_state para salvar depois
        st.session_state.resultado = {
            "data": datetime.today().strftime('%Y-%m-%d'),
            "faturamento": faturamento,
            "km": km_rodado,
            "combustivel": combustivel,
            "outros_custos": outros_custos,
            "lucro": lucro,
            "lucro_km": round(lucro_km, 2) if km_rodado > 0 else 0,
            "meta_diaria": meta_diaria,
            "falta_meta": falta_meta
        }
# Botão para salvar no diário
if "resultado" in st.session_state and st.button("💾 Salvar no diário"):
    df_novo = pd.DataFrame([st.session_state.resultado])
    caminho_csv = "diario.csv"
    
    if os.path.exists(caminho_csv):
        df_existente = pd.read_csv(caminho_csv)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    df_final.to_csv(caminho_csv, index=False)
    st.success("✅ Entrada salva com sucesso no diário!")

# Botão para limpar os campos
if st.button("🧹 Limpar campos"):
    # Usa o método .pop() para remover do session_state ANTES de redesenhar os widgets
    for campo in ["faturamento", "km_rodado", "combustivel", "outros_custos", "meta_diaria"]:
        st.session_state.pop(campo, None)
    st.rerun()

# --- Diário de Bordo Visual ---
st.markdown("---")
st.subheader("📅 Diário de Bordo")

caminho_csv = "diario.csv"

if os.path.exists(caminho_csv):
    df = pd.read_csv(caminho_csv)

    st.dataframe(df, use_container_width=True)

    # Totais
    faturamento_total = df["faturamento"].sum()
    lucro_total = df["lucro"].sum()
    km_total = df["km"].sum()
    lucro_km_medio = lucro_total / km_total if km_total > 0 else 0
    dias_registrados = df.shape[0]
    meta_total = df["meta_diaria"].iloc[-1] * dias_registrados  # Usa a meta mais recente como base
    progresso = (faturamento_total / meta_total) * 100 if meta_total > 0 else 0

    st.markdown("📊 Total acumulado:")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧾 Faturamento Total", f"R$ {faturamento_total:.2f}")
    col2.metric("💰 Lucro Total", f"R$ {lucro_total:.2f}")
    col3.metric("🚗 KM Total", f"{km_total:.0f} km")

    col4, col5 = st.columns(2)
    col4.metric("💸 Lucro Médio por KM", f"R$ {lucro_km_medio:.2f}")
    col5.metric("📈 Progresso da Meta", f"{progresso:.1f}%")
else:
    st.info("📭 Nenhuma entrada encontrada ainda. Salve um dia para visualizar o diário.")
