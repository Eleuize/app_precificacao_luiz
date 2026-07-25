importar fluxo de luz como rua
importar pandas como pd
importar plotly.expressar como px
importar json
importar os
de data e hora importar data e hora

rua.definir_configuração_da_página(
    título_da_página="LM - Importação 2U | Precificação",
    ícone_da_página="📦",
    layout="largo",
    estado_inicial_da_barra_lateral="expandido"
)

rua.markdown("""
<style>
    .stButton > botão { largura: 100%; altura: 50px; peso da fonte: negrito; tamanho da fonte: 16px; raio da borda: 10px; cor de fundo: #4CAF50; cor: branco; }
    .stButton > botão:hover { cor de fundo: #45a049; }
    .stTextInput > div > div > entrada { raio da borda: 8px; }
    .stSelectbox > div > div > selecionar { raio da borda: 8px; }
    .cartão { cor de fundo: #f0f2f6; preenchimento: 20px; raio da borda: 10px; sombra da caixa: 2px 2px 10px rgba(0,0,0,0.1); margem inferior: 20px; }
</style>
""", unsafe_allow_html=True)

def carregar_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        config = {
            "custos_fixos": {"aluguel": 90, "pro_labore": 120, "contabilidade": 352, "internet": 90, "logistica": 250, "outros": 300},
            "impostos": {"ii": 0, "ipi": 0, "icms": 4.5, "pis": 0, "cofins": 0, "iof": 0},
            "marketplaces": {"Mercado Livre": {"comissao": 6.75, "taxa_fixa": 0.13}, "Shopee": {"comissao": 4.0, "taxa_fixa": 0.20}, "Amazon": {"comissao": 4.5, "taxa_fixa": 0.15}},
            "cotacao_dolar": 5.30
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        return config

def carregar_produtos():
    if os.path.exists("produtos.csv"):
        return pd.read_csv("produtos.csv")
    else:
        df = pd.DataFrame(columns=["ID", "Nome", "Custo_USD", "Frete_USD", "Embalagem_R$", "II_%", "IPI_%", "ICMS_%", "PIS_%", "COFINS_%", "IOF_%", "Marketplace"])
        df.to_csv("produtos.csv", index=False)
        return df

def salvar_produtos(df):
    df.to_csv("produtos.csv", index=False)

def calcular_preco(row, config, vendas_mes):
    cotacao = config["cotacao_dolar"]
    custo_brl = (row["Custo_USD"] + row["Frete_USD"]) * cotacao * (1 + config["impostos"]["iof"] / 100)
    impostos = custo_brl * (row["II_%"] + row["IPI_%"] + row["ICMS_%"] + row["PIS_%"] + row["COFINS_"]) / 100
    custo_fixo_total = sum(config["custos_fixos"].values())
    custo_fixo_unit = custo_fixo_total / vendas_mes if vendas_mes > 0 else 0
    custo_total = custo_brl + impostos + row["Embalagem_R$"] + custo_fixo_unit
    marketplace = row["Marketplace"]
    if marketplace in config["marketplaces"]:
        taxa_percentual = config["marketplaces"][marketplace]["comissao"]
        taxa_fixa = config["marketplaces"][marketplace]["taxa_fixa"]
    else:
        taxa_percentual = 0
        taxa_fixa = 0
    lucro_desejado = 0.20
    preco_final = (custo_total * (1 + lucro_desejado) + taxa_fixa) / (1 - taxa_percentual / 100)
    lucro_real = preco_final - custo_total - (preco_final * taxa_percentual / 100) - taxa_fixa
    lucro_percentual = (lucro_real / preco_final) * 100 if preco_final > 0 else 0
    roi = (lucro_real / custo_total) * 100 if custo_total > 0 else 0
    return {"Custo_Total_R$": round(custo_total, 2), "Preco_Final_R$": round(preco_final, 2), "Lucro_R$": round(lucro_real, 2), "Lucro_%": round(lucro_percentual, 1), "ROI_%": round(roi, 1)}

# ========== BARRA LATERAL (USANDO A IMAGEM QUE VOCÊ ACABOU DE CORRIGIR) ==========
rua.barra_lateral.imagem("logo.jpg", largura=120)

rua.barra_lateral.markdown("""
<h1 style='font-size: 24px; margin-bottom: 0px; text-align: center;'>App de Precificação</h1>
<p style='font-size: 14px; color: gray; margin-top: 0px; text-align: center;'>LM - Importing 2U</p>
""", unsafe_allow_html=True)

pagina = rua.barra_lateral.radio(
    "Navegação",
    ["🏠 Dashboard", "📦 Produtos", "📝 Cadastrar Produto", "📥 Importar CSV", 
     "🧮 Simulador", "📊 Relatório", "⚙️ Configurações"]
)

config = carregar_config()
df_produtos = carregar_produtos()
vendas_mes = rua.barra_lateral.number_input("Vendas estimadas no mês", min_value=1, value=100, step=10)

if pagina == "🏠 Dashboard":
    rua.title("🏠 Dashboard - Resumo Financeiro")
    if not df_produtos.empty:
        resultados = []
        for _, row in df_produtos.iterrows():
            res = calcular_preco(row, config, vendas_mes)
            resultados.append(res)
        df_res = pd.DataFrame(resultados)
        col1, col2, col3, col4 = rua.columns(4)
        col1.metric("Total Produtos", len(df_produtos))
        col2.metric("Faturamento Estimado", f"R$ {df_res['Preco_Final_R$'].sum():,.2f}")
        col3.metric("Lucro Total", f"R$ {df_res['Lucro_R$'].sum():,.2f}")
        col4.metric("ROI Médio", f"{df_res['ROI_%'].mean():.1f}%")
        fig = px.bar(df_res, x=df_produtos["Nome"], y=["Preco_Final_R$", "Lucro_R$"], barmode="group", title="Preço Final vs Lucro por Produto")
        rua.plotly_chart(fig, use_container_width=True)
    else:
        rua.info("Nenhum produto cadastrado.")

elif pagina == "📦 Produtos":
    rua.title("📦 Lista de Produtos")
    if not df_produtos.empty:
        rua.dataframe(df_produtos, use_container_width=True, height=400)
        if rua.button("📥 Exportar para Excel"):
            df_produtos.to_excel("produtos_exportados.xlsx", index=False)
            rua.success("Arquivo exportado!")
        with rua.expander("🗑️ Deletar Produto"):
            produto_del = rua.selectbox("Selecione o produto", df_produtos["Nome"].tolist())
            if rua.button("Deletar", type="primary"):
                df_produtos = df_produtos[df_produtos["Nome"] != produto_del]
                salvar_produtos(df_produtos)
                rua.rerun()
    else:
        rua.info("Nenhum produto cadastrado.")

elif pagina == "📝 Cadastrar Produto":
    rua.title("📝 Cadastrar Novo Produto")
    with rua.form("form_produto"):
        col1, col2 = rua.columns(2)
        with col1:
            nome = rua.text_input("Nome do Produto")
            custo_usd = rua.number_input("Custo em USD", min_value=0.01, step=0.01)
            frete_usd = rua.number_input("Frete em USD", min_value=0.0, step=0.01)
            embalagem = rua.number_input("Embalagem em R$", min_value=0.0, step=0.01)
        with col2:
            marketplace = rua.selectbox("Marketplace", ["Mercado Livre", "Shopee", "Amazon"])
            ii = rua.number_input("II %", min_value=0.0, step=0.1)
            ipi = rua.number_input("IPI %", min_value=0.0, step=0.1)
            icms = rua.number_input("ICMS %", min_value=0.0, step=0.1)
            pis = rua.number_input("PIS %", min_value=0.0, step=0.1)
            cofins = rua.number_input("COFINS %", min_value=0.0, step=0.1)
            iof = rua.number_input("IOF %", min_value=0.0, step=0.1)
        submit = rua.form_submit_button("✅ Cadastrar Produto", use_container_width=True)
        if submit:
            novo_id = df_produtos["ID"].max() + 1 if not df_produtos.empty else 1
            novo_produto = pd.DataFrame({
                "ID": [novo_id], "Nome": [nome], "Custo_USD": [custo_usd], "Frete_USD": [frete_usd],
                "Embalagem_R$": [embalagem], "II_%": [ii], "IPI_%": [ipi], "ICMS_%": [icms],
                "PIS_%": [pis], "COFINS_%": [cofins], "IOF_%": [iof], "Marketplace": [marketplace]
            })
            df_produtos = pd.concat([df_produtos, novo_produto], ignore_index=True)
            salvar_produtos(df_produtos)
            rua.success(f"✅ Produto '{nome}' cadastrado!")

elif pagina == "📥 Importar CSV":
    rua.title("📥 Importar Produtos via CSV")
    rua.markdown("Formato: Nome,Custo_USD,Frete_USD,Embalagem_R$,II_%,IPI_%,ICMS_%,PIS_%,COFINS_%,IOF_%,Marketplace")
    arquivo = rua.file_uploader("Escolha o CSV", type="csv")
    if arquivo:
        try:
            df_import = pd.read_csv(arquivo)
            ultimo_id = df_produtos["ID"].max() if not df_produtos.empty else 0
            df_import["ID"] = range(ultimo_id + 1, ultimo_id + 1 + len(df_import))
            df_import = df_import[["ID", "Nome", "Custo_USD", "Frete_USD", "Embalagem_R$", "II_%", "IPI_%", "ICMS_%", "PIS_%", "COFINS_%", "IOF_%", "Marketplace"]]
            df_produtos = pd.concat([df_produtos, df_import], ignore_index=True)
            salvar_produtos(df_produtos)
            rua.success(f"✅ {len(df_import)} produtos importados!")
        except Exception as e:
            rua.error(f"Erro: {e}")

elif pagina == "🧮 Simulador":
    rua.title("🧮 Simulador de Preço e Margem")
    if not df_produtos.empty:
        produto_sel = rua.selectbox("Selecione um produto", df_produtos["Nome"].tolist())
        row = df_produtos[df_produtos["Nome"] == produto_sel].iloc[0]
        col1, col2 = rua.columns(2)
        with col1:
            preco_sugerido = rua.number_input("Preço sugerido (R$)", min_value=1.0, step=1.0)
        with col2:
            quantidade = rua.number_input("Quantidade", min_value=1, value=1, step=1)
        res = calcular_preco(row, config, vendas_mes)
        custo_total = res["Custo_Total_R$"]
        preco_calculado = res["Preco_Final_R$"]
        if preco_sugerido > 0:
            marketplace = row["Marketplace"]
            if marketplace in config["marketplaces"]:
                taxa_percentual = config["marketplaces"][marketplace]["comissao"]
                taxa_fixa = config["marketplaces"][marketplace]["taxa_fixa"]
            else:
                taxa_percentual = 0
                taxa_fixa = 0
            lucro_real = preco_sugerido - custo_total - (preco_sugerido * taxa_percentual / 100) - taxa_fixa
            lucro_percentual = (lucro_real / preco_sugerido) * 100 if preco_sugerido > 0 else 0
            roi = (lucro_real / custo_total) * 100 if custo_total > 0 else 0
            col1, col2, col3, col4 = rua.columns(4)
            col1.metric("Custo Total", f"R$ {custo_total:.2f}")
            col2.metric("Preço Sugerido", f"R$ {preco_sugerido:.2f}")
            col3.metric("Lucro R$", f"R$ {lucro_real:.2f}", delta=f"{(lucro_real/preco_sugerido)*100:.1f}%")
            col4.metric("ROI", f"{roi:.1f}%")
            if lucro_real < 0:
                rua.warning("⚠️ Prejuízo! Aumente o preço.")
            rua.info(f"💡 Preço ideal calculado: **R$ {preco_calculado:.2f}**")
    else:
        rua.info("Nenhum produto cadastrado.")

elif pagina == "📊 Relatório":
    rua.title("📊 Relatório Completo")
    if not df_produtos.empty:
        resultados = []
        for _, row in df_produtos.iterrows():
            res = calcular_preco(row, config, vendas_mes)
            resultados.append({"Produto": row["Nome"], "Marketplace": row["Marketplace"], "Custo Total": res["Custo_Total_R$"], "Preço Final": res["Preco_Final_R$"], "Lucro R$": res["Lucro_R$"], "Lucro %": res["Lucro_%"], "ROI %": res["ROI_%"]})
        df_rel = pd.DataFrame(resultados)
        rua.dataframe(df_rel, use_container_width=True, height=400)
        if rua.button("📥 Exportar para Excel"):
            df_rel.to_excel("relatorio_precos.xlsx", index=False)
            rua.success("Relatório exportado!")
    else:
        rua.info("Nenhum produto cadastrado.")

elif pagina == "⚙️ Configurações":
    rua.title("⚙️ Configurações")
    rua.subheader("💰 Custos Fixos Mensais")
    col1, col2 = rua.columns(2)
    with col1:
        config["custos_fixos"]["aluguel"] = rua.number_input("Aluguel", value=config["custos_fixos"]["aluguel"])
        config["custos_fixos"]["pro_labore"] = rua.number_input("Pró-labore", value=config["custos_fixos"]["pro_labore"])
        config["custos_fixos"]["contabilidade"] = rua.number_input("Contabilidade", value=config["custos_fixos"]["contabilidade"])
    with col2:
        config["custos_fixos"]["internet"] = rua.number_input("Internet", value=config["custos_fixos"]["internet"])
        config["custos_fixos"]["logistica"] = rua.number_input("Logística", value=config["custos_fixos"]["logistica"])
        config["custos_fixos"]["outros"] = rua.number_input("Outros", value=config["custos_fixos"]["outros"])
    rua.subheader("📊 Impostos (%)")
    col1, col2 = rua.columns(2)
    with col1:
        config["impostos"]["ii"] = rua.number_input("II", value=config["impostos"]["ii"])
        config["impostos"]["ipi"] = rua.number_input("IPI", value=config["impostos"]["ipi"])
        config["impostos"]["icms"] = rua.number_input("ICMS", value=config["impostos"]["icms"])
    with col2:
        config["impostos"]["pis"] = rua.number_input("PIS", value=config["impostos"]["pis"])
        config["impostos"]["cofins"] = rua.number_input("COFINS", value=config["impostos"]["cofins"])
        config["impostos"]["iof"] = rua.number_input("IOF", value=config["impostos"]["iof"])
    rua.subheader("🏪 Marketplaces")
    for mp in config["marketplaces"]:
        col1, col2 = rua.columns(2)
        with col1:
            config["marketplaces"][mp]["comissao"] = rua.number_input(f"{mp} - Comissão %", value=config["marketplaces"][mp]["comissao"])
        with col2:
            config["marketplaces"][mp]["taxa_fixa"] = rua.number_input(f"{mp} - Taxa Fixa R$", value=config["marketplaces"][mp]["taxa_fixa"])
    rua.subheader("💱 Cotação")
    config["cotacao_dolar"] = rua.number_input("Cotação do Dólar (R$)", value=config["cotacao_dolar"], step=0.01)
    if rua.button("💾 Salvar Configurações", use_container_width=True):
        with open("config.json", "w") as f:
            json.dump(config, f)
        rua.success("✅ Configurações salvas!")
