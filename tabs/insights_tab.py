# tabs/insights_tab.py

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from utils.callbacks import PolishedCallbackHandler
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Lista de perguntas pré-definidas para a análise automática
PERGUNTAS_RELEVANTES = [
    "Qual o faturamento total neste conjunto de dados?",
    "Qual o número total de notas fiscais únicas (baseado na 'chave_de_acesso')?",
    "Qual o valor médio por nota fiscal? (calcule o faturamento total dividido pelo número de notas fiscais únicas)",
    "Quem foi o cliente (use a coluna que representa a razão social do destinatário) que mais comprou em valor?",
    "Quais são os 5 produtos (use a coluna de descrição do produto) mais vendidos em valor total? Responda em formato de lista.",
    "Quais são os 5 produtos mais vendidos em quantidade (use a coluna de quantidade)? Responda em formato de lista.",
    "Qual o número total de clientes únicos (destinatários)?",
    "Quais os 3 estados (use a coluna de UF do destinatário) que mais receberam valor em mercadorias? Responda em formato de lista.",
    "Qual a principal operação fiscal (CFOP) em termos de valor total?",
    "Faça um resumo executivo sobre os dados em 2 frases."
]

# NOVO: Função com "retry" para a chamada do agente
# Esta função tentará executar a chamada à API até 3 vezes, com 10 segundos de espera,
# caso ocorra um erro genérico (Exception), que inclui os erros de rede e servidor.
@retry(wait=wait_fixed(10), stop=stop_after_attempt(3), reraise=True)
def invocar_agente_com_retry(agent, pergunta, handler):
    """Invoca o agente com uma política de nova tentativa para torná-lo mais resiliente a erros de rede."""
    print(f"Tentando responder à pergunta: {pergunta[:50]}...")
    return agent.invoke({"input": pergunta}, config={"callbacks": [handler]})


def render(df, google_api_key):
    st.header("💡 Insights Automáticos Gerados por IA")
    st.write("Clique no botão abaixo para que o agente de IA responda a um conjunto de perguntas de negócio fundamentais sobre seus dados.")

    if st.button("Gerar Relatório de Insights", type="primary", use_container_width=True):
        if 'insights_gerados' in st.session_state:
            del st.session_state['insights_gerados']
        
        with st.spinner("O agente está analisando os dados... Isso pode levar um momento e inclui novas tentativas em caso de falha de conexão."):
            try:
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, temperature=0)
                agent = create_pandas_dataframe_agent(llm, df, verbose=False, allow_dangerous_code=True, handle_parsing_errors=True)
                
                resultados = []
                progress_bar = st.progress(0, text="Iniciando análise...")

                for i, pergunta in enumerate(PERGUNTAS_RELEVANTES):
                    progresso_texto = f"Analisando pergunta {i+1}/{len(PERGUNTAS_RELEVANTES)}: {pergunta[:40]}..."
                    progress_bar.progress((i + 1) / len(PERGUNTAS_RELEVANTES), text=progresso_texto)
                    
                    handler = PolishedCallbackHandler(agent_name=f"Analista de Insights #{i+1}")
                    
                    # ALTERADO: Chamamos nossa nova função com retry em vez de .invoke() diretamente
                    resposta = invocar_agente_com_retry(agent, pergunta, handler)
                    
                    resultados.append({"pergunta": pergunta, "resposta": resposta['output']})

                progress_bar.empty()
                st.session_state.insights_gerados = resultados
                st.rerun()

            except Exception as e:
                st.error(f"Ocorreu um erro persistente durante a geração dos insights, mesmo após tentar novamente: {e}")
                st.session_state.insights_gerados = None

    if 'insights_gerados' in st.session_state and st.session_state.insights_gerados is not None:
        st.markdown("---")
        st.subheader("Resultados da Análise Automática")
        
        for i, resultado in enumerate(st.session_state.insights_gerados):
            with st.expander(f"**{i+1}. {resultado['pergunta']}**"):
                st.success(f"**Resposta do Agente:** {resultado['resposta']}")
                
                if st.button("📌 Adicionar Insight ao Relatório", key=f"pin_insight_{i}"):
                    item = {"type": "qa", "category": "insight_ia", "title": f"Insight IA: {resultado['pergunta'][:40]}...", "content": resultado}
                    if item not in st.session_state.report_items:
                        st.session_state.report_items.append(item)
                        st.success("Insight adicionado ao relatório!")
                        st.rerun()
                    else:
                        st.warning("Este insight já foi adicionado ao relatório.")