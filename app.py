# app.py

import streamlit as st
import pandas as pd
from utils.processing import processar_zip 
# Importa todos os módulos de abas, incluindo a nova de insights
from tabs import agent_tab, insights_tab, dashboard_tab, report_tab, fiscal_tab

# Configuração da página
st.set_page_config(page_title="Plataforma de Análise de NF-e", layout="wide")
st.title("🚀 Plataforma de Análise e Relatórios de Notas Fiscais")

# --- ESTADO DA SESSÃO ---
# Inicializa as variáveis no estado da sessão para persistirem entre as interações.
if 'report_items' not in st.session_state:
    st.session_state.report_items = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'insights_gerados' not in st.session_state:
    st.session_state.insights_gerados = None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuração")
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Chave de API do Google carregada!")
    except (FileNotFoundError, KeyError):
        st.error("Chave de API não encontrada. Verifique o arquivo .streamlit/secrets.toml")
        google_api_key = None

    st.markdown("---")
    st.header("🛒 Itens para o Relatório")
    if st.session_state.report_items:
        for i, item in enumerate(st.session_state.report_items):
            st.info(f"Item {i+1}: {item['title']}")
        if st.button("Limpar Itens do Relatório"):
            st.session_state.report_items = []
            st.rerun()
    else:
        st.info("Nenhum item adicionado.")

# --- LÓGICA DE UPLOAD E PROCESSAMENTO DO ARQUIVO ---
upload_container = st.container(border=True)
with upload_container:
    uploaded_file = st.file_uploader("Selecione o arquivo .ZIP com as notas fiscais", type=["zip"])

    if uploaded_file is not None:
        if st.session_state.df is None:
            try:
                with st.spinner("Processando e analisando os dados..."):
                    st.session_state.df = processar_zip(uploaded_file)
                st.success("Dados carregados! Navegue pelas abas ou use os filtros abaixo para refinar sua análise.")
            except Exception as e:
                st.error(f"Falha ao processar o arquivo: {e}")
                st.session_state.df = None
    elif st.session_state.df is None:
        st.info("Aguardando o upload do arquivo .ZIP para começar a análise.")

# --- SEÇÃO PRINCIPAL COM FILTROS E ABAS ---
if st.session_state.df is not None:
    df_original = st.session_state.df
    
    # --- SEÇÃO DE FILTROS GLOBAIS ---
    filter_container = st.container(border=True)
    with filter_container:
        st.subheader("Filtros Globais")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            ufs_disponiveis = sorted(df_original['uf_destinatario_x'].unique())
            ufs_selecionadas = st.multiselect("Filtrar por UF do Destinatário:", options=ufs_disponiveis, default=ufs_disponiveis)
        
        with col2:
            data_min = df_original['data_emissao_x'].min()
            data_max = df_original['data_emissao_x'].max()
            data_selecionada = st.date_input(
                "Filtrar por Período de Emissão:",
                value=(data_min.date(), data_max.date()),
                min_value=data_min.date(),
                max_value=data_max.date(),
            )

    # Aplica os filtros para criar um DataFrame filtrado para as abas visuais
    if len(data_selecionada) == 2:
        df_filtrado = df_original[
            (df_original['uf_destinatario_x'].isin(ufs_selecionadas)) &
            (df_original['data_emissao_x'].dt.date >= data_selecionada[0]) &
            (df_original['data_emissao_x'].dt.date <= data_selecionada[1])
        ]
    else: 
        df_filtrado = df_original[df_original['uf_destinatario_x'].isin(ufs_selecionadas)]

    st.write(f"Exibindo {len(df_filtrado)} de {len(df_original)} registros após a filtragem.")
    st.markdown("---")

    # Criação das abas, incluindo a nova "Insights da IA"
    tab_agent, tab_insights, tab_dashboard, tab_fiscal, tab_report = st.tabs([
        "💬 Agente Q&A", 
        "💡 Insights da IA",
        "📊 Dashboard", 
        "✅ Análise Fiscal", 
        "📄 Montador de Relatório"
    ])

    # Renderiza cada aba, passando o DataFrame apropriado para cada uma
    with tab_agent:
        # O Agente Q&A usa o DataFrame original para responder perguntas sobre todos os dados
        agent_tab.render(df_original, google_api_key)
    
    with tab_insights:
        # A nova aba de Insights também usa o DataFrame original para gerar uma análise completa
        insights_tab.render(df_original, google_api_key)
        
    with tab_dashboard:
        # O Dashboard visual reflete os filtros que o usuário selecionou
        dashboard_tab.render(df_filtrado) 
        
    with tab_fiscal:
        # A Análise Fiscal visual também reflete os filtros
        fiscal_tab.render(df_filtrado)
        
    with tab_report:
        # O Montador de Relatório usa os dados originais para o sumário da IA
        report_tab.render(df_original, google_api_key)