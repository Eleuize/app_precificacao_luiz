import json
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Calc Markup - Gestão de Precificação",
    page_icon="📊",
    layout="wide",
)

# Arquivos de Persistência
USERS_FILE = "users.json"
PRODUCTS_FILE = "produtos_markup.csv"
MANUAL_FILE = "Manual_CALC_MARKUP.pdf"


# Inicialização de Arquivos e Assets
def init_files():
  if not os.path.exists(USERS_FILE):
    default_users = {"admin": "123456"}
    with open(USERS_FILE, "w", encoding="utf-8") as f:
      json.dump(default_users, f, ensure_ascii=False, indent=4)

  if not os.path.exists(PRODUCTS_FILE):
    df_empty = pd.DataFrame(
        columns=[
            "Produto",
            "SKU",
            "Custo_USD",
            "Dolar",
            "Frete_Impostos",
            "Embalagem",
            "Custo_Fixo_Pct",
            "Comissao_Mkt",
            "Imposto_Venda",
            "Lucro_Desejado",
            "Tarifa_Fixa",
            "Preco_Venda",
            "Markup",
            "Tipo",
        ]
    )
    df_empty.to_csv(PRODUCTS_FILE, index=False)


init_files()


# Funções de Autenticação
def load_users():
  with open(USERS_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def save_user(username, password):
  users = load_users()
  users[username] = password
  with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=4)


# Função de Cálculo de Preço (Core)
def calcular_preco(
    custo_usd,
    dolar,
    frete_impostos_brl,
    embalagem,
    custo_fixo_pct,
    comissao_mkt_pct,
    imposto_venda_pct,
    lucro_desejado_pct,
    tarifa_fixa,
):
  custo_produto_brl = (custo_usd * dolar) + frete_impostos_brl + embalagem

  soma_aliquotas = (
      comissao_mkt_pct + imposto_venda_pct + custo_fixo_pct + lucro_desejado_pct
  ) / 100

  if soma_aliquotas >= 1:
    return 0, 0

  divisor = 1 - soma_aliquotas
  preco_venda = (custo_produto_brl + tarifa_fixa) / divisor

  markup = preco_venda / custo_produto_brl if custo_produto_brl > 0 else 0
  return round(preco_venda, 2), round(markup, 2)


# Controle de Sessão de Login
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["user"] = ""

# Tela de Login
if not st.session_state["logged_in"]:
  st.markdown(
      "<h2 style='text-align: center;'>🔐 Calc Markup - Acesso Restrito</h2>",
      unsafe_allow_html=True,
  )
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar Usuário"])

    with tab1:
      username = st.text_input("Usuário", key="login_user")
      password = st.text_input("Senha", type="password", key="login_pass")
      if st.button("Entrar no Sistema", use_container_width=True):
        users = load_users()
        if username in users and users[username] == password:
          st.session_state["logged_in"] = True
          st.session_state["user"] = username
          st.success("Login realizado com sucesso!")
          st.rerun()
        else:
          st.error("Usuário ou senha incorretos.")

    with tab2:
      new_user = st.text_input("Novo Usuário", key="new_user")
      new_pass = st.text_input("Nova Senha", type="password", key="new_pass")
      if st.button("Cadastrar", use_container_width=True):
        if new_user and new_pass:
          users = load_users()
          if new_user in users:
            st.warning("Usuário já existe.")
          else:
            save_user(new_user, new_pass)
            st.success(
                "Usuário cadastrado com sucesso! Faça login na aba ao lado."
            )
        else:
          st.warning("Preencha todos os campos.")
  st.stop()

# Menu Lateral e Navegação
st.sidebar.markdown(f"### Olá, **{st.session_state['user']}**!")
menu = st.sidebar.selectbox(
    "Navegação",
    [
        "📊 Dashboard",
        "➕ Cadastro & Precificação",
        "📦 Estoque e Produtos",
        "🏷️ Simulador Atacado",
        "📖 Manual & Documentação",
    ],
)

if st.sidebar.button("Sair da Conta", use_container_width=True):
  st.session_state["logged_in"] = False
  st.session_state["user"] = ""
  st.rerun()

# Carregar Dados de Produtos
df_produtos = pd.read_csv(PRODUCTS_FILE)

# -------------------------------------------------------------
# 1. DASHBOARD
# -------------------------------------------------------------
if menu == "📊 Dashboard":
  st.title("📊 Painel de Controle Financeiro")
  st.markdown("Visão geral da sua operação, margens e portfólio cadastrado.")

  col1, col2, col3 = st.columns(3)
  col1.metric("Total de Produtos Cadastrados", len(df_produtos))

  if not df_produtos.empty:
    media_markup = (
        df_produtos["Markup"].mean() if "Markup" in df_produtos.columns else 0
    )
    media_preco = (
        df_produtos["Preco_Venda"].mean()
        if "Preco_Venda" in df_produtos.columns
        else 0
    )
    col2.metric("Markup Médio Geral", f"{media_markup:.2f}x")
    col3.metric("Preço Médio de Venda", f"R$ {media_preco:.2f}")

    st.markdown("---")
    st.subheader("Últimos Produtos Cadastrados")
    st.dataframe(df_produtos.tail(5), use_container_width=True)
  else:
    st.info("Nenhum produto cadastrado no momento.")

# -------------------------------------------------------------
# 2. CADASTRO & PRECIFICAÇÃO
# -------------------------------------------------------------
elif menu == "➕ Cadastro & Precificação":
  st.title("➕ Calculadora & Cadastro de Produtos")
  st.markdown(
      "Insira os custos de importação e taxas para calcular o preço ideal de"
      " venda."
  )

  with st.form("form_precificacao"):
    col1, col2 = st.columns(2)

    with col1:
      st.subheader("Custos de Aquisição")
      produto = st.text_input("Nome do Produto")
      sku = st.text_input("SKU / Código")
      custo_usd = st.number_input(
          "Custo Unitário (USD / RMB)", min_value=0.0, value=10.0, step=0.1
      )
      dolar = st.number_input(
          "Cotação da Moeda (R$)", min_value=0.0, value=5.50, step=0.01
      )
      frete_impostos_brl = st.number_input(
          "Frete Proporcional + Impostos BR (R$)",
          min_value=0.0,
          value=5.0,
          step=0.5,
      )
      embalagem = st.number_input(
          "Custo de Embalagem (R$)", min_value=0.0, value=2.0, step=0.1
      )

    with col2:
      st.subheader("Taxas e Margens (%)")
      custo_fixo_pct = st.number_input(
          "Custo Fixo Operacional (%)", min_value=0.0, value=5.0, step=0.5
      )
      comissao_mkt_pct = st.number_input(
          "Comissão do Marketplace (%)", min_value=0.0, value=16.0, step=0.5
      )
      imposto_venda_pct = st.number_input(
          "Imposto sobre Venda (ME/Simples) (%)",
          min_value=0.0,
          value=6.0,
          step=0.5,
      )
      lucro_desejado_pct = st.number_input(
          "Lucro Líquido Desejado (%)", min_value=0.0, value=15.0, step=0.5
      )
      tarifa_fixa = st.number_input(
          "Tarifa Fixa do Marketplace (R$)", min_value=0.0, value=6.0, step=0.5
      )

    submitted = st.form_submit_button("Calcular e Salvar Produto")

    if submitted:
      if produto:
        p_venda, markup = calcular_preco(
            custo_usd,
            dolar,
            frete_impostos_brl,
            embalagem,
            custo_fixo_pct,
            comissao_mkt_pct,
            imposto_venda_pct,
            lucro_desejado_pct,
            tarifa_fixa,
        )

        novo_registro = {
            "Produto": produto,
            "SKU": sku if sku else "N/A",
            "Custo_USD": custo_usd,
            "Dolar": dolar,
            "Frete_Impostos": frete_impostos_brl,
            "Embalagem": embalagem,
            "Custo_Fixo_Pct": custo_fixo_pct,
            "Comissao_Mkt": comissao_mkt_pct,
            "Imposto_Venda": imposto_venda_pct,
            "Lucro_Desejado": lucro_desejado_pct,
            "Tarifa_Fixa": tarifa_fixa,
            "Preco_Venda": p_venda,
            "Markup": markup,
            "Tipo": "Varejo",
        }

        df_produtos = pd.concat(
            [df_produtos, pd.DataFrame([novo_registro])], ignore_index=True
        )
        df_produtos.to_csv(PRODUCTS_FILE, index=False)

        st.success(
            f"Produto salvo com sucesso! Preço de Venda: R$ {p_venda:.2f} |"
            f" Markup: {markup}x"
        )
      else:
        st.warning("Por favor, informe pelo menos o nome do produto.")

# -------------------------------------------------------------
# 3. ESTOQUE E PRODUTOS
# -------------------------------------------------------------
elif menu == "📦 Estoque e Produtos":
  st.title("📦 Gerenciamento de Produtos Cadastrados")
  st.markdown("Consulte, analise e gerencie sua base de itens salvos.")

  if not df_produtos.empty:
    st.dataframe(df_produtos, use_container_width=True)

    if st.button("Limpar Todos os Registros", type="primary"):
      df_empty = pd.DataFrame(columns=df_produtos.columns)
      df_empty.to_csv(PRODUCTS_FILE, index=False)
      st.success("Base de dados limpa com sucesso!")
      st.rerun()
  else:
    st.info("Nenhum produto cadastrado até o momento.")

# -------------------------------------------------------------
# 4. SIMULADOR ATACADO
# -------------------------------------------------------------
elif menu == "🏷️ Simulador Atacado":
  st.title("🏷️ Simulador de Precificação para Atacado")
  st.markdown(
      "Calcule margens e preços diferenciados para vendas em volume/atacado,"
      " reduzindo taxas de marketplace ou aplicando descontos progressivos."
  )

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Parâmetros do Lote")
    custo_unit_base = st.number_input(
        "Custo Base do Produto (R$)", min_value=0.0, value=25.0, step=0.5
    )
    quantidade_lote = st.number_input(
        "Quantidade de Peças no Atacado", min_value=1, value=10, step=1
    )
    desconto_atacado_pct = st.slider(
        "Desconto / Redução de Margem Varejo (%)", 0.0, 50.0, 15.0, 1.0
    )

  with col2:
    st.subheader("Estrutura de Custos Operacionais")
    comissao_atacado = st.number_input(
        "Comissão Canal Atacado (%)", min_value=0.0, value=5.0, step=0.5
    )
    imposto_atacado = st.number_input(
        "Imposto Venda Atacado (%)", min_value=0.0, value=4.0, step=0.5
    )
    lucro_almejado_atacado = st.number_input(
        "Lucro Almejado no Atacado (%)", min_value=0.0, value=10.0, step=0.5
    )

  if st.button("Calcular Condições de Atacado", use_container_width=True):
    soma_aliquotas_atacado = (
        comissao_atacado + imposto_atacado + lucro_almejado_atacado
    ) / 100

    if soma_aliquotas_atacado >= 1:
      st.error(
          "A soma das alíquotas ultrapassa 100%. Ajuste os percentuais informados."
      )
    else:
      divisor_atacado = 1 - soma_aliquotas_atacado
      preco_venda_unit_atacado = custo_unit_base / divisor_atacado

      st.markdown("---")
      st.subheader("Resultados da Simulação")

      res_col1, res_col2, res_col3 = st.columns(3)
      res_col1.metric("Custo Unitário", f"R$ {custo_unit_base:.2f}")
      res_col2.metric(
          "Preço Sugerido Unitário (Atacado)",
          f"R$ {preco_venda_unit_atacado:.2f}",
      )
      res_col3.metric(
          "Faturamento Total do Lote",
          f"R$ {preco_venda_unit_atacado * quantidade_lote:.2f}",
      )

      st.info(
          f"💡 **Dica de Negócio:** Para um lote com {quantidade_lote} unidades,"
          f" o preço final sugerido por peça é de **R$"
          f" {preco_venda_unit_atacado:.2f}** (mantendo a margem de lucro de"
          f" {lucro_almejado_atacado}% após impostos e comissões reduzidas)."
      )

# -------------------------------------------------------------
# 5. MANUAL & DOCUMENTAÇÃO (Incluindo Download do PDF)
# -------------------------------------------------------------
elif menu == "📖 Manual & Documentação":
  st.title("📖 Manual do Sistema e Documentação de Precificação")
  st.markdown(
      "Consulte o guia operacional do aplicativo ou faça o download do manual"
      " oficial em PDF para consulta offline."
  )

  st.markdown("---")

  # Seção de Download do Manual
  st.subheader("📥 Download do Manual Oficial")
  if os.path.exists(MANUAL_FILE):
    with open(MANUAL_FILE, "rb") as pdf_file:
      pdf_bytes = pdf_file.read()

    st.download_button(
        label="📄 Baixar Manual_CALC_MARKUP.pdf",
        data=pdf_bytes,
        file_name="Manual_CALC_MARKUP.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
  else:
    st.warning(
        f"⚠️ O arquivo `{MANUAL_FILE}` não foi encontrado no diretório raiz do"
        " projeto. Certifique-se de colocá-lo na mesma pasta do script"
        " `app.py` para habilitar o download direto."
    )

  st.markdown("---")

  # Guia Rápido Integrado
  st.subheader("💡 Guia Rápido de Utilização")
  st.markdown("""
  1. **Dashboard:** Acompanhe o volume total de itens e os indicadores médios da sua esteira comercial.
  2. **Cadastro & Precificação:** Preencha os custos unitários em moeda estrangeira, fretes proporcionais e taxas. O algoritmo calcula de forma exata o Markup multiplicador e o Preço de Venda ideal com base no divisor de receitas.
  3. **Estoque e Produtos:** Centraliza o histórico de tudo o que foi calculado, permitindo exportação e gerenciamento direto.
  4. **Simulador Atacado:** Ferramenta dedicada para modelar vendas em grande volume, ajustando comissões menores de canais corporativos ou lotes fechados.
  """)
