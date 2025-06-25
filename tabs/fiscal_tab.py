# tabs/fiscal_tab.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Dicionário e função para enriquecer a análise de CFOP
CFOP_DESCRICOES = {
    '5102': 'Venda de mercadoria de terceiros', '6102': 'Venda de mercadoria de terceiros (outro estado)',
    '5405': 'Venda com ST (substituto)', '6404': 'Venda com ST (fora do estado)',
    '1202': 'Devolução de venda', '2202': 'Devolução de venda (outro estado)',
    '5910': 'Remessa em bonificação/brinde', '6910': 'Remessa em bonificação/brinde (outro estado)',
    '5949': 'Outra saída não especificada', '6949': 'Outra saída não especificada (outro estado)',
    '5101': 'Venda de produção própria', '6101': 'Venda de produção própria (outro estado)',
}
def get_cfop_categoria(cfop):
    cfop_str = str(cfop)
    if cfop_str.startswith(('51', '61')): return "Venda"
    if cfop_str.startswith(('12', '22')): return "Devolução"
    if cfop_str.startswith(('59', '69')): return "Outras Saídas"
    if cfop_str.startswith(('54', '64')): return "Venda com ST"
    return "Outras Operações"

# --- FUNÇÕES DE ANÁLISE ---
def analisar_consistencia(df):
    if not all(col in df.columns for col in ['chave_de_acesso', 'valor_nota_fiscal', 'valor_total']):
        return None
    check_df = df.groupby('chave_de_acesso').agg(valor_declarado_nota=('valor_nota_fiscal', 'first'), soma_calculada_itens=('valor_total', 'sum')).reset_index()
    check_df['diferenca'] = (check_df['valor_declarado_nota'] - check_df['soma_calculada_itens']).round(2)
    return check_df[check_df['diferenca'].abs() > 0.01]

def analisar_operacoes_geo(df):
    if not all(col in df.columns for col in ['uf_emitente_x', 'uf_destinatario_x', 'valor_total']):
        return None
    df_operacao = df.copy()
    df_operacao['tipo_de_operacao'] = np.where(df['uf_emitente_x'] == df['uf_destinatario_x'], 'Interna', 'Interestadual')
    return df_operacao.groupby('tipo_de_operacao')['valor_total'].sum()

def analisar_cfop(df):
    if 'cfop' not in df.columns:
        return None
    df['cfop'] = df['cfop'].astype(str)
    cfop_analysis = df.groupby('cfop')['valor_total'].agg(['sum', 'count']).rename(columns={'sum': 'Valor Total', 'count': 'Qtd. de Itens'}).sort_values(by='Valor Total', ascending=False)
    cfop_analysis['descricao'] = cfop_analysis.index.map(CFOP_DESCRICOES).fillna('Descrição não encontrada')
    cfop_analysis['label_grafico'] = cfop_analysis.index + ' - ' + cfop_analysis['descricao']
    cfop_analysis['categoria'] = cfop_analysis.index.map(get_cfop_categoria)
    return cfop_analysis.head(15)

# --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO DA ABA ---
def render(df):
    st.header("✅ Painel de Auditoria e Análise Fiscal")
    st.write("Visualizações e análises automáticas baseadas nas colunas encontradas no seu arquivo.")
    
    # Análise 1: Consistência de Valores
    st.markdown("---")
    st.subheader("1. Consistência de Valores (Total da Nota vs. Soma dos Itens)")
    inconsistencias_df = analisar_consistencia(df)
    if inconsistencias_df is not None:
        if inconsistencias_df.empty:
            st.success("✅ Nenhuma inconsistência de valores encontrada.")
        else:
            st.warning(f"🚨 Encontradas {len(inconsistencias_df)} notas com divergência de valor!")
            st.dataframe(inconsistencias_df)
            if st.button("📌 Adicionar Tabela de Inconsistências ao Relatório", key="pin_inconsistencias"):
                item = {"type": "dataframe", "category": "fiscal", "title": "Tabela: Inconsistências de Valor", "content": {"titulo": "Notas com Divergência entre Valor Declarado e Soma dos Itens", "dados": inconsistencias_df}}
                st.session_state.report_items.append(item); st.success("Adicionado!"); st.rerun()
    else:
        st.info("Análise indisponível. Colunas necessárias não encontradas.")

    # Análise 2: Natureza das Operações
    st.markdown("---")
    st.subheader("2. Análise de Operações (Internas vs. Interestaduais)")
    operacoes_df = analisar_operacoes_geo(df)
    if operacoes_df is not None and not operacoes_df.empty:
        fig_operacoes = px.pie(operacoes_df, names=operacoes_df.index, values=operacoes_df.values, title='Proporção de Valor por Tipo de Operação', hole=0.3)
        st.plotly_chart(fig_operacoes, use_container_width=True)
        if st.button("📌 Adicionar Gráfico de Operações ao Relatório", key="pin_operacoes_chart"):
            item = {"type": "chart", "category": "fiscal", "title": "Gráfico: Proporção por Tipo de Operação", "content": {"titulo": "Proporção de Valor por Tipo de Operação", "fig": fig_operacoes}}
            st.session_state.report_items.append(item); st.success("Adicionado!"); st.rerun()
    else:
        st.info("Análise indisponível. Colunas necessárias não encontradas.")
        
    # Análise 3: Análise por CFOP
    st.markdown("---")
    st.subheader("3. Análise por Tipo de Operação (CFOP)")
    cfop_df = analisar_cfop(df)
    if cfop_df is not None and not cfop_df.empty:
        fig_cfop = px.bar(cfop_df, x='Valor Total', y='label_grafico', orientation='h', title='Top 15 Operações (CFOPs) por Valor Total', color='categoria', hover_data=['Qtd. de Itens'])
        fig_cfop.update_layout(yaxis={'categoryorder':'total ascending'}, legend_title_text='Categoria')
        st.plotly_chart(fig_cfop, use_container_width=True)
        if st.button("📌 Adicionar Gráfico de CFOP ao Relatório", key="pin_cfop_chart"):
            item = {"type": "chart", "category": "fiscal", "title": "Gráfico: Top 15 CFOPs", "content": {"titulo": "Top 15 Operações (CFOPs) por Valor Total", "fig": fig_cfop}}
            st.session_state.report_items.append(item); st.success("Adicionado!"); st.rerun()
        with st.expander("Ver tabela de dados detalhada"):
            st.dataframe(cfop_df)
    else:
        st.info("Análise indisponível. Coluna 'cfop' não encontrada.")