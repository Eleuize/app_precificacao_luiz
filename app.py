import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="CALC MARKUP | LM Importing",
    page_icon="https://raw.githubusercontent.com/Eleuize/app_precificacao_luiz/main/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CONFIGURAÇÃO DE ÍCONE E MANIFESTO PARA CELULAR/TABLET/PWA =====
st.markdown("""
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/Eleuize/app_precificacao_luiz/main/logo.png">
<link rel="icon" type="image/png" href="https://raw.githubusercontent.com/Eleuize/app_precificacao_luiz/main/logo.png">
""", unsafe_allow_html=True)

# ================== ESTILOS GLOBAIS ==================
st.markdown("""
<style>
    .stButton > button { width: 100%; height: 50px; font-weight: bold; font-size: 16px; border-radius: 10px; background-color: #4CAF50; color: white; }
    .stButton > button:hover { background-color: #45a049; }
    .stTextInput > div > div > input { border-radius: 8px; }
    .stSelectbox > div > div > select { border-radius: 8px; }
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }

    /* ===== MENU LATERAL (CINZA CHUMBO COM LETRAS BRANCAS) ===== */
    [data-testid="stSidebar"] {
        background-color: #2c2c2c !important;
    }
    /* Força as letras do menu a serem BRANCAS */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Mantém o subtítulo em cinza claro para dar elegância */
    [data-testid="stSidebar"] p {
        color: #cccccc !important;
    }

    /* ===== TARJA PRETA NO MENU (SEM NENHUMA BORDA VISÍVEL) ===== */
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        background-color: #2c2c2c !important;
        padding: 0px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stNumberInput"] {
        background-color: #111111 !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0px !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #111111 !important;
        border: none !important;
        outline: none !important;
        caret-color: #ffffff !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[data-testid="stNumberInput"] button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] button:hover {
        background-color: #2c2c2c !important;
    }
</style>
""", unsafe_allow_html=True)

# ================== GERENCIAMENTO DE USUÁRIOS (PERSISTENTE) ==================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def carregar_usuarios():
    # Base padrão garantida sempre que reiniciar
    usuarios_padrao = {
        "admin": {
            "nome": "Administrador",
            "senha": hash_senha("admin123"),
            "tipo": "Administrador"
        },
        "eleuize": {
            "nome": "Eleuize",
            "senha": hash_senha("X@drez21"),
            "tipo": "Administrador"
        }
    }
    
    if os.path.exists("usuarios.json"):
        try:
            with open("usuarios.json", "r") as f:
                dados = json.load(f)
                # Garante que os admins padrão sempre existam
                for k, v in usuarios_padrao.items():
                    if k not in dados:
                        dados[k] = v
                return dados
        except:
            pass
            
    salvar_usuarios(usuarios_padrao)
    return usuarios_padrao

def salvar_usuarios(usuarios_db):
    with open("usuarios.json", "w") as f:
        json.dump(usuarios_db, f, indent=4)

# Inicializa session_state para usuários
if "usuarios_db_v3" not in st.session_state:
    st.session_state.usuarios_db_v3 = carregar_usuarios()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_atual = None
    st.session_state.nome_usuario_atual = None
    st.session_state.tipo_usuario = None

# ================== TELA DE LOGIN ==================
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito - CALC MARKUP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Entre com suas credenciais para continuar.</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário (Login)")
            senha_input = st.text_input("Senha", type="password")
            botao_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if botao_login:
                usuarios_db = st.session_state.usuarios_db_v3
                if usuario_input in usuarios_db and usuarios_db[usuario_input]["senha"] == hash_senha(senha_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_atual = usuario_input
                    st.session_state.nome_usuario_atual = usuarios_db[usuario_input].get("nome", usuario_input)
                    st.session_state.tipo_usuario = usuarios_db[usuario_input]["tipo"]
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("⚠️ Usuário ou senha incorretos.")
        
        st.stop()

# ================== FUNÇÕES DE CONFIGURAÇÃO E DADOS ==================
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
        df = pd.DataFrame(columns=["ID", "Nome", "Custo_USD", "Frete_USD", "Embalagem_R$", "II_%", "IPI_%", "ICMS_%", "PIS_%", "COFINS_", "IOF_", "Marketplace", "Registrado_Por", "Data_Hora"])
        df.to_csv("produtos.csv", index=False)
        return df

def salvar_produtos(df):
    df.to_csv("produtos.csv", index=False)

def calcular_preco(row, config, vendas_mes):
    cotacao = config["cotacao_dolar"]
    custo_brl = (row["Custo_USD"] + row["Frete_USD"]) * cotacao * (1 + config["impostos"]["iof"] / 100)
    impostos = custo_brl * (row["II_%"] + row["IPI_%"] + row["ICMS_%"] + row["PIS_%"] + row["COFINS_"] + row["IOF_"]) / 100
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

# ================== MENU LATERAL E SESSÃO ==================
st.sidebar.image("logo.png", width=220)

st.sidebar.markdown(f"""
<h1 style='font-size: 28px; margin-bottom: 0px; line-height: 1.0; text-align: center; letter-spacing: 1px;'>CALC MARKUP</h1>
<p style='font-size: 14px; color: #cccccc; margin-top: -5px; text-align: center;'>LM - Importing 2U®</p>
<hr style='margin: 10px 0; border-color: #444;'>
<p style='font-size: 13px; color: #ffffff; text-align: center;'>👤 <b>{st.session_state.nome_usuario_atual}</b><br><span style='color: #4CAF50; font-size: 11px;'>({st.session_state.tipo_usuario})</span></p>
""", unsafe_allow_html=True)

# ========== BOTÃO SAIR / TROCAR USUÁRIO (MODIFICADO) ==========
if st.sidebar.button("📓 Sair / Trocar Usuário"):
    st.session_state.autenticado = False
    st.session_state.usuario_atual = None
    st.session_state.nome_usuario_atual = None
    st.session_state.tipo_usuario = None
    st.rerun()

# ========== ESTILO PERSONALIZADO PARA O BOTÃO (CINZA CHUMBO E LETRA BRANCA) ==========
st.markdown("""
<style>
    /* Força o botão de sair a ter fundo cinza chumbo e letras brancas */
    div[data-testid="stSidebar"] div.stButton > button {
        background-color: #2c2c2c !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #3c3c3c !important;
        color: #ffffff !important;
        border-color: #666666 !important;
    }
</style>
""", unsafe_allow_html=True)

pagina = st.sidebar.radio(
    "Navegação",
    ["🏠 Início", "📝 Cadastrar Produto", "📥 Importar CSV", "📦 Produtos", "🏠 Dashboard", "🧮 Simulador", "📊 Relatório", "⚙️ Configurações"]
)

config = carregar_config()
df_produtos = carregar_produtos()
vendas_mes = st.sidebar.number_input("Vendas estimadas no mês", min_value=1, value=100, step=10)

# ================== PÁGINAS DO APLICATIVO ==================
if pagina == "🏠 Início":
    st.markdown("""
    <style>
        .stApp {
            background-image: url("https://raw.githubusercontent.com/Eleuize/app_precificacao_luiz/main/P%C3%A1gina%20Inicial.png");
            background-size: 55% auto;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding-top: 300px;'>
        <div style='background-color: rgba(255, 255, 255, 0.88); padding: 25px 45px; border-radius: 20px; display: inline-block; box-shadow: 0 8px 30px rgba(0,0,0,0.2);'>
            <h1 style='color: #1a1a1a; font-size: 42px; font-weight: bold; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.05);'>Bem-vindo ao CALC MARKUP</h1>
            <p style='color: #222; font-size: 20px; margin-top: 2px; font-weight: 500;'>Sua ferramenta inteligente para precificar importações.</p>
            <p style='color: #444; font-size: 16px; margin-top: 2px;'>Clique em '📝 Cadastrar Produto' no menu para começar.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif pagina == "📝 Cadastrar Produto":
    st.title("📝 Cadastrar Novo Produto")
    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            custo_usd = st.number_input("Custo em USD", min_value=0.01, step=0.01)
            frete_usd = st.number_input("Frete em USD", min_value=0.0, step=0.01)
            embalagem = st.number_input("Embalagem em R$", min_value=0.0, step=0.01)
        with col2:
            marketplace = st.selectbox("Marketplace", ["Mercado Livre", "Shopee", "Amazon"])
            ii = st.number_input("II %", min_value=0.0, step=0.1)
            ipi = st.number_input("IPI %", min_value=0.0, step=0.1)
            icms = st.number_input("ICMS %", min_value=0.0, step=0.1)
            pis = st.number_input("PIS %", min_value=0.0, step=0.1)
            cofins = st.number_input("COFINS", min_value=0.0, step=0.1)
            iof = st.number_input("IOF", min_value=0.0, step=0.1)
        submit = st.form_submit_button("✅ Cadastrar Produto", use_container_width=True)
        if submit:
            novo_id = df_produtos["ID"].max() + 1 if not df_produtos.empty else 1
            novo_produto = pd.DataFrame({
                "ID": [novo_id], 
                "Nome": [nome], 
                "Custo_USD": [custo_usd], 
                "Frete_USD": [frete_usd],
                "Embalagem_R$": [embalagem], 
                "II_%": [ii], 
                "IPI_%": [ipi], 
                "ICMS_%": [icms],
                "PIS_%": [pis], 
                "COFINS_": [cofins], 
                "IOF_": [iof], 
                "Marketplace": [marketplace],
                "Registrado_Por": [st.session_state.nome_usuario_atual],
                "Data_Hora": [datetime.now().strftime("%d/%m/%Y %H:%M")]
            })
            df_produtos = pd.concat([df_produtos, novo_produto], ignore_index=True)
            salvar_produtos(df_produtos)
            st.success(f"✅ Produto '{nome}' cadastrado por {st.session_state.nome_usuario_atual}!")

elif pagina == "📥 Importar CSV":
    st.title("📥 Importar Produtos via CSV")
    st.markdown("Formato: Nome,Custo_USD,Frete_USD,Embalagem_R$,II_%,IPI_%,ICMS_%,PIS_%,COFINS_,IOF_,Marketplace")
    arquivo = st.file_uploader("Escolha o CSV", type="csv")
    if arquivo:
        try:
            df_import = pd.read_csv(arquivo)
            ultimo_id = df_produtos["ID"].max() if not df_produtos.empty else 0
            df_import["ID"] = range(ultimo_id + 1, ultimo_id + 1 + len(df_import))
            df_import["Registrado_Por"] = st.session_state.nome_usuario_atual
            df_import["Data_Hora"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            df_import = df_import[["ID", "Nome", "Custo_USD", "Frete_USD", "Embalagem_R$", "II_%", "IPI_%", "ICMS_%", "PIS_%", "COFINS_", "IOF_", "Marketplace", "Registrado_Por", "Data_Hora"]]
            df_produtos = pd.concat([df_produtos, df_import], ignore_index=True)
            salvar_produtos(df_produtos)
            st.success(f"✅ {len(df_import)} produtos importados por {st.session_state.nome_usuario_atual}!")
        except Exception as e:
            st.error(f"Erro: {e}")

elif pagina == "📦 Produtos":
    st.title("📦 Lista de Produtos e Auditoria")
    if not df_produtos.empty:
        st.dataframe(df_produtos, use_container_width=True, height=400)
        if st.button("📥 Exportar para Excel"):
            df_produtos.to_excel("produtos_exportados.xlsx", index=False)
            st.success("Arquivo exportado!")
        with st.expander("🗑️ Deletar Produto"):
            produto_del = st.selectbox("Selecione o produto", df_produtos["Nome"].tolist())
            if st.button("Deletar", type="primary"):
                df_produtos = df_produtos[df_produtos["Nome"] != produto_del]
                salvar_produtos(df_produtos)
                st.success(f"Produto deletado por {st.session_state.nome_usuario_atual}")
                st.rerun()
    else:
        st.info("Nenhum produto cadastrado.")

elif pagina == "🏠 Dashboard":
    st.title("🏠 Dashboard - Resumo Financeiro")
    if not df_produtos.empty:
        resultados = []
        for _, row in df_produtos.iterrows():
            res = calcular_preco(row, config, vendas_mes)
            resultados.append(res)
        df_res = pd.DataFrame(resultados)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Produtos", len(df_produtos))
        col2.metric("Faturamento Estimado", f"R$ {df_res['Preco_Final_R$'].sum():,.2f}")
        col3.metric("Lucro Total", f"R$ {df_res['Lucro_R$'].sum():,.2f}")
        col4.metric("ROI Médio", f"{df_res['ROI_%'].mean():.1f}%")
        
        st.subheader("📊 Preço Final vs Lucro por Produto")
        fig = px.bar(df_res, x=df_produtos["Nome"], y=["Preco_Final_R$", "Lucro_R$"], barmode="group", title="Preço Final vs Lucro por Produto")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Participação de cada Marketplace no Lucro Total")
        df_pizza = df_res.groupby(df_produtos["Marketplace"])["Lucro_R$"].sum().reset_index()
        df_pizza.columns = ["Marketplace", "Lucro_R$"]
        
        cores_marketplace = {"Mercado Livre": "#FFD700", "Shopee": "#FF8C00", "Amazon": "#1A1A1A"}
        
        fig_pizza = go.Figure(data=[go.Pie(
            labels=df_pizza["Marketplace"],
            values=df_pizza["Lucro_R$"],
            marker=dict(colors=[cores_marketplace[m] for m in df_pizza["Marketplace"]], line=dict(color='#FFFFFF', width=3)),
            textinfo='label+percent', textfont=dict(size=20, color='white'), sort=False, pull=[0.05, 0.05, 0.05]
        )])
        fig_pizza.update_layout(height=600, width=900, margin=dict(l=20, r=20, t=40, b=20), showlegend=True)
        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

elif pagina == "🧮 Simulador":
    st.title("🧮 Simulador de Preço e Margem")
    if not df_produtos.empty:
        produto_sel = st.selectbox("Selecione um produto", df_produtos["Nome"].tolist())
        row = df_produtos[df_produtos["Nome"] == produto_sel].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            preco_sugerido = st.number_input("Preço sugerido (R$)", min_value=1.0, step=1.0)
        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
        res = calcular_preco(row, config, vendas_mes)
        custo_total = res["Custo_Total_R$"]
        preco_calculado = res["Preco_Final_R$"]
        if preco_sugerido > 0:
            marketplace = row["Marketplace"]
            taxa_percentual = config["marketplaces"][marketplace]["comissao"] if marketplace in config["marketplaces"] else 0
            taxa_fixa = config["marketplaces"][marketplace]["taxa_fixa"] if marketplace in config["marketplaces"] else 0
            lucro_real = preco_sugerido - custo_total - (preco_sugerido * taxa_percentual / 100) - taxa_fixa
            roi = (lucro_real / custo_total) * 100 if custo_total > 0 else 0
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Custo Total", f"R$ {custo_total:.2f}")
            col2.metric("Preço Sugerido", f"R$ {preco_sugerido:.2f}")
            col3.metric("Lucro R$", f"R$ {lucro_real:.2f}", delta=f"{(lucro_real/preco_sugerido)*100:.1f}%")
            col4.metric("ROI", f"{roi:.1f}%")
            if lucro_real < 0:
                st.warning("⚠️ Prejuízo! Aumente o preço.")
            st.info(f"💡 Preço ideal calculado: **R$ {preco_calculado:.2f}**")
    else:
        st.info("Nenhum produto cadastrado.")

elif pagina == "📊 Relatório":
    st.title("📊 Relatório Completo com Auditoria")
    if not df_produtos.empty:
        resultados = []
        for _, row in df_produtos.iterrows():
            res = calcular_preco(row, config, vendas_mes)
            resultados.append({
                "Produto": row["Nome"], 
                "Marketplace": row["Marketplace"], 
                "Custo Total": res["Custo_Total_R$"], 
                "Preço Final": res["Preco_Final_R$"], 
                "Lucro R$": res["Lucro_R$"], 
                "Lucro %": res["Lucro_%"], 
                "ROI %": res["ROI_%"],
                "Cadastrado Por": row.get("Registrado_Por", "N/D"),
                "Data/Hora": row.get("Data_Hora", "N/D")
            })
        df_rel = pd.DataFrame(resultados)
        st.dataframe(df_rel, use_container_width=True, height=400)
        if st.button("📥 Exportar para Excel"):
            df_rel.to_excel("relatorio_precos.xlsx", index=False)
            st.success("Relatório exportado!")
    else:
        st.info("Nenhum produto cadastrado.")

elif pagina == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    
    # Gerenciamento de Usuários (EXCLUSIVO PARA ADMINISTRADORES)
    if st.session_state.tipo_usuario == "Administrador":
        st.subheader("👥 Gerenciamento de Usuários e Acessos")
        with st.form("form_novo_usuario"):
            st.markdown("**Adicionar Novo Usuário**")
            nome_completo_novo = st.text_input("Nome Completo do Usuário (Ex: Luiz, Maria...)")
            login_novo = st.text_input("Nome de Usuário para Login (Ex: luiz, maria...)")
            senha_novo = st.text_input("Senha Inicial", type="password")
            tipo_novo = st.selectbox("Tipo de Acesso", ["Usuário Comum", "Administrador"])
            btn_criar_user = st.form_submit_button("➕ Criar Usuário")
            
            if btn_criar_user:
                if nome_completo_novo and login_novo and senha_novo:
                    if login_novo in st.session_state.usuarios_db_v3:
                        st.error("⚠️ Este login de usuário já existe.")
                    else:
                        st.session_state.usuarios_db_v3[login_novo] = {
                            "nome": nome_completo_novo,
                            "senha": hash_senha(senha_novo),
                            "tipo": tipo_novo
                        }
                        salvar_usuarios(st.session_state.usuarios_db_v3)
                        st.success(f"✅ Usuário '{nome_completo_novo}' ({login_novo}) criado com sucesso!")
                else:
                    st.warning("Por favor, preencha todos os campos do novo usuário.")
        
        st.markdown("---")
        
        # Alterar Senha de Qualquer Usuário
        with st.form("form_alterar_senha"):
            st.markdown("**🔑 Alterar Senha de Usuário**")
            usuarios_lista = list(st.session_state.usuarios_db_v3.keys())
            usuario_alvo = st.selectbox("Selecione o usuário para alterar a senha", usuarios_lista)
            nova_senha_input = st.text_input("Nova Senha", type="password")
            btn_alt_senha = st.form_submit_button("🔄 Atualizar Senha")
            
            if btn_alt_senha:
                if nova_senha_input:
                    st.session_state.usuarios_db_v3[usuario_alvo]["senha"] = hash_senha(nova_senha_input)
                    salvar_usuarios(st.session_state.usuarios_db_v3)
                    st.success(f"✅ Senha do usuário '{usuario_alvo}' alterada com sucesso!")
                else:
                    st.warning("Digite a nova senha.")
        
        st.markdown("---")
        st.markdown("**Usuários Cadastrados no Sistema:**")
        for usr, info in list(st.session_state.usuarios_db_v3.items()):
            col_u1, col_u2, col_u3, col_u4 = st.columns([2, 2, 2, 1])
            col_u1.write(f"👤 **{info.get('nome', usr)}**")
            col_u2.write(f"Login: `{usr}`")
            col_u3.write(f"Tipo: {info['tipo']}")
            if usr != "admin" or len(st.session_state.usuarios_db_v3) > 1:
                if col_u4.button("🗑️ Deletar", key=f"del_{usr}"):
                    if usr == st.session_state.usuario_atual:
                        st.error("⚠️ Você não pode deletar o seu próprio usuário logado.")
                    else:
                        del st.session_state.usuarios_db_v3[usr]
                        salvar_usuarios(st.session_state.usuarios_db_v3)
                        st.success(f"Usuário {usr} removido!")
                        st.rerun()
        st.markdown("---")
    else:
        st.info("ℹ️ Apenas o Administrador pode cadastrar novos usuários, alterar senhas ou remover acessos.")

    st.subheader("💰 Custos Fixos Mensais")
    col1, col2 = st.columns(2)
    with col1:
        config["custos_fixos"]["aluguel"] = st.number_input("Aluguel", value=config["custos_fixos"]["aluguel"])
        config["custos_fixos"]["pro_labore"] = st.number_input("Pró-labore", value=config["custos_fixos"]["pro_labore"])
        config["custos_fixos"]["contabilidade"] = st.number_input("Contabilidade", value=config["custos_fixos"]["contabilidade"])
    with col2:
        config["custos_fixos"]["internet"] = st.number_input("Internet", value=config["custos_fixos"]["internet"])
        config["custos_fixos"]["logistica"] = st.number_input("Logística", value=config["custos_fixos"]["logistica"])
        config["custos_fixos"]["outros"] = st.number_input("Outros", value=config["custos_fixos"]["outros"])
    
    st.subheader("📊 Impostos (%)")
    col1, col2 = st.columns(2)
    with col1:
        config["impostos"]["ii"] = st.number_input("II", value=config["impostos"]["ii"])
        config["impostos"]["ipi"] = st.number_input("IPI", value=config["impostos"]["ipi"])
        config["impostos"]["icms"] = st.number_input("ICMS", value=config["impostos"]["icms"])
    with col2:
        config["impostos"]["pis"] = st.number_input("PIS", value=config["impostos"]["pis"])
        config["impostos"]["cofins"] = st.number_input("COFINS", value=config["impostos"]["cofins"])
        config["impostos"]["iof"] = st.number_input("IOF", value=config["impostos"]["iof"])
        
    st.subheader("🏪 Marketplaces")
    for mp in config["marketplaces"]:
        col1, col2 = st.columns(2)
        with col1:
            config["marketplaces"][mp]["comissao"] = st.number_input(f"{mp} - Comissão %", value=config["marketplaces"][mp]["comissao"])
        with col2:
            config["marketplaces"][mp]["taxa_fixa"] = st.number_input(f"{mp} - Taxa Fixa R$", value=config["marketplaces"][mp]["taxa_fixa"])
            
    st.subheader("💱 Cotação")
    config["cotacao_dolar"] = st.number_input("Cotação do Dólar (R$)", value=config["cotacao_dolar"], step=0.01)
    
    if st.button("💾 Salvar Configurações", use_container_width=True):
        with open("config.json", "w") as f:
            json.dump(config, f)
        st.success(f"✅ Configurações salvas por {st.session_state.nome_usuario_atual}!")

    # ===== MANUAL DO USUÁRIO =====
    st.markdown("---")
    st.subheader("📘 Manual do Usuário")
    try:
        with open("Manual_CALC_MARKUP.pdf", "rb") as f:
            st.download_button(
                label="📥 Baixar Manual do Usuário (PDF)",
                data=f,
                file_name="Manual_CALC_MARKUP.pdf",
                mime="application/pdf"
            )
    except FileNotFoundError:
        st.warning("⚠️ Arquivo 'Manual_CALC_MARKUP.pdf' não encontrado.")
