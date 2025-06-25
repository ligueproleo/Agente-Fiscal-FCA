# tabs/dashboard_tab.py

import streamlit as st
import pandas as pd
import plotly.express as px

def formatar_numero(numero):
    """Função auxiliar para formatar números no padrão brasileiro."""
    if pd.isna(numero) or not isinstance(numero, (int, float)):
        return "N/A"
    return f"{numero:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def render(df):
    """
    Renderiza a aba do Dashboard com mapeamento de colunas interno e botões de "pin" individuais.
    """
    st.header("📊 Painel de Controle de Vendas")
    st.write("Análise dos principais indicadores e insights extraídos das notas fiscais.")

    # --- 1. SEÇÃO DE MAPEAMENTO DE COLUNAS (DENTRO DA ABA) ---
    with st.expander("Configurar Mapeamento de Colunas Essenciais", expanded=True):
        st.info("Para que os KPIs e gráficos principais funcionem, por favor, indique quais colunas correspondem a cada conceito de negócio.")
        
        # Prepara a lista de colunas disponíveis para o usuário escolher
        lista_colunas_disponiveis = ["Selecione uma coluna..."] + sorted(df.columns.tolist())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            col_cliente = st.selectbox(
                "Coluna de **Cliente** (Nome/Razão Social):",
                options=lista_colunas_disponiveis, 
                key="map_cliente"
            )
        with col2:
            col_produto = st.selectbox(
                "Coluna de **Produto** (Descrição):",
                options=lista_colunas_disponiveis, 
                key="map_produto"
            )
        with col3:
            col_quantidade = st.selectbox(
                "Coluna de **Quantidade** de Itens:",
                options=lista_colunas_disponiveis, 
                key="map_quantidade"
            )

    # Converte a seleção placeholder em None para facilitar as verificações lógicas
    coluna_cliente = None if col_cliente == "Selecione uma coluna..." else col_cliente
    coluna_produto = None if col_produto == "Selecione uma coluna..." else col_produto
    coluna_quantidade = None if col_quantidade == "Selecione uma coluna..." else col_quantidade

    st.markdown("---")

    # --- 2. CÁLCULOS E EXIBIÇÃO DOS KPIs ---
    st.subheader("Indicadores Chave de Performance (KPIs)")
    
    valor_total_faturado = df['valor_total'].sum()
    quantidade_total_itens = df[coluna_quantidade].sum() if coluna_quantidade else "N/A"
    num_notas_unicas = df['chave_de_acesso'].nunique()
    num_clientes_unicos = df[coluna_cliente].nunique() if coluna_cliente else "N/A"

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="💰 Faturamento Total", value=f"R$ {formatar_numero(valor_total_faturado)}")
    with kpi2:
        valor_itens = f"{int(quantidade_total_itens):,}".replace(",", ".") if isinstance(quantidade_total_itens, (int, float)) else quantidade_total_itens
        st.metric(label="📦 Itens Vendidos", value=valor_itens)
    with kpi3:
        st.metric(label="🧾 Notas Fiscais Únicas", value=num_notas_unicas)
    with kpi4:
        st.metric(label="👥 Clientes Únicos", value=num_clientes_unicos)

    if not all([coluna_quantidade, coluna_cliente, coluna_produto]):
        st.info("ℹ️ Para visualizar todos os gráficos e KPIs, por favor, mapeie as colunas essenciais na seção acima.")
    
    st.markdown("---")
    
    # --- 3. GRÁFICOS CURADOS COM BOTÕES DE "PIN" INDIVIDUAIS ---
    st.subheader("Análises Relevantes")
    col_a, col_b = st.columns(2)

    with col_a:
        if coluna_cliente:
            top_10_clientes = df.groupby(coluna_cliente)['valor_total'].sum().nlargest(10).sort_values()
            fig_clientes = px.bar(
                top_10_clientes, x='valor_total', y=top_10_clientes.index, orientation='h',
                title="🏆 Top 10 Clientes por Valor de Compra", labels={'valor_total': 'Valor Total (R$)', 'y': 'Cliente'}, text_auto='.2s'
            )
            fig_clientes.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_clientes, use_container_width=True)

            if st.button("📌 Adicionar Gráfico de Clientes ao Relatório", key="pin_clientes"):
                item = {"type": "chart", "category": "dashboard", "title": "Gráfico: Top 10 Clientes", "content": {"titulo": "Top 10 Clientes por Valor de Compra", "dados": top_10_clientes, "metrica": "Valor Total (R$)", "fig": fig_clientes}}
                st.session_state.report_items.append(item)
                st.success("Gráfico de Clientes adicionado!")
                st.rerun()
        else:
            st.info("Selecione a coluna de 'Cliente' no mapeamento para ver o ranking de clientes.")

    with col_b:
        if coluna_produto:
            top_10_produtos = df.groupby(coluna_produto)['valor_total'].sum().nlargest(10).sort_values()
            fig_produtos = px.bar(
                top_10_produtos, x='valor_total', y=top_10_produtos.index, orientation='h',
                title="🛍️ Top 10 Produtos por Faturamento", labels={'valor_total': 'Valor Total (R$)', 'y': 'Produto'}, text_auto='.2s'
            )
            fig_produtos.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_produtos, use_container_width=True)
            
            if st.button("📌 Adicionar Gráfico de Produtos ao Relatório", key="pin_produtos"):
                item = {"type": "chart", "category": "dashboard", "title": "Gráfico: Top 10 Produtos", "content": {"titulo": "Top 10 Produtos por Faturamento", "dados": top_10_produtos, "metrica": "Valor Total (R$)", "fig": fig_produtos}}
                st.session_state.report_items.append(item)
                st.success("Gráfico de Produtos adicionado!")
                st.rerun()
        else:
            st.info("Selecione a coluna de 'Produto' no mapeamento para ver o ranking de produtos.")

    vendas_no_tempo = df.set_index('data_emissao_x').resample('D')['valor_total'].sum()
    fig_tempo = px.line(
        vendas_no_tempo, x=vendas_no_tempo.index, y='valor_total',
        title="📈 Faturamento Diário ao Longo do Tempo", labels={'data_emissao_x': 'Data', 'valor_total': 'Faturamento (R$)'}, markers=True
    )
    st.plotly_chart(fig_tempo, use_container_width=True)
    
    if st.button("📌 Adicionar Gráfico de Tempo ao Relatório", key="pin_tempo"):
        item = {"type": "chart", "category": "dashboard", "title": "Gráfico: Vendas no Tempo", "content": {"titulo": "Faturamento Diário ao Longo do Tempo", "dados": vendas_no_tempo, "metrica": "Faturamento (R$)", "fig": fig_tempo}}
        st.session_state.report_items.append(item)
        st.success("Gráfico de Vendas no Tempo adicionado!")
        st.rerun()

    st.markdown("---")

    # --- 4. FERRAMENTA DE ANÁLISE DETALHADA ---
    with st.expander("🔬 Análise Detalhada e Personalizada (Deep Dive)"):
        st.write("Use as opções abaixo para cruzar diferentes dimensões e métricas dos dados.")
        
        colunas_numericas_expander = df.select_dtypes(include='number').columns.tolist()
        colunas_categoricas_expander = df.select_dtypes(include=['object', 'category']).columns.tolist()
        colunas_a_remover_num = ['modelo_x', 'serie_x', 'numero_x', 'numero_produto', 'modelo_y', 'serie_y', 'numero_y']
        colunas_numericas_expander = [col for col in colunas_numericas_expander if col not in colunas_a_remover_num]
        
        if colunas_categoricas_expander and colunas_numericas_expander:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                default_dimensao = coluna_cliente if coluna_cliente in colunas_categoricas_expander else colunas_categoricas_expander[0]
                dimensao = st.selectbox("Agrupar por (Dimensão):", options=colunas_categoricas_expander, index=colunas_categoricas_expander.index(default_dimensao))
            with c2:
                metrica = st.selectbox("Calcular (Métrica):", options=colunas_numericas_expander, index=colunas_numericas_expander.index('valor_total'))
            with c3:
                top_n = st.slider("Ver Top N:", min_value=3, max_value=20, value=5, key="slider_detalhado")
            with c4:
                tipo_grafico = st.selectbox("Tipo de Gráfico:", options=["Barras", "Pizza"], key="grafico_detalhado")

            dados_agrupados = df.groupby(dimensao)[metrica].sum().nlargest(top_n)
            titulo_grafico = f"Top {top_n} {dimensao} por Soma de {metrica}"
            
            fig_detalhada = None
            if tipo_grafico == "Barras":
                fig_detalhada = px.bar(dados_agrupados, x=dados_agrupados.index, y=dados_agrupados.values, title=titulo_grafico, labels={'x': dimensao, 'y': metrica})
            elif tipo_grafico == "Pizza":
                fig_detalhada = px.pie(dados_agrupados, names=dados_agrupados.index, values=dados_agrupados.values, title=titulo_grafico)
            
            if fig_detalhada:
                st.plotly_chart(fig_detalhada, use_container_width=True)

                if st.button("📌 Adicionar Gráfico ao Relatório", key="pin_chart_detalhado"):
                    item_para_adicionar = {"type": "chart", "category": "dashboard", "title": f"Gráfico: {titulo_grafico[:40]}...", "content": {"titulo": titulo_grafico, "dados": dados_agrupados, "metrica": metrica, "fig": fig_detalhada}}
                    if item_para_adicionar not in st.session_state.report_items:
                        st.session_state.report_items.append(item_para_adicionar)
                        st.success("Gráfico adicionado ao relatório!")
                        st.rerun()
                    else:
                        st.warning("Este gráfico já foi adicionado ao relatório.")