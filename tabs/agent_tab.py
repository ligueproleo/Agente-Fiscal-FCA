# tabs/agent_tab.py

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Importa o nosso handler de callback final, com o estilo polido
from utils.callbacks import PolishedCallbackHandler

def render(df, google_api_key):
    """
    Renderiza a aba do Agente de Q&A (Perguntas e Respostas).
    """
    st.header("💬 Converse com seus Dados")
    st.write("Faça perguntas em linguagem natural. O processo de raciocínio do agente será exibido no terminal.")
    
    # Formulário para o usuário inserir a pergunta
    with st.form(key="qa_form"):
        pergunta_usuario = st.text_input("Sua pergunta sobre os dados:", key="pergunta_input")
        submitted = st.form_submit_button("Perguntar ao Agente 🤖")

    # Lógica executada apenas quando o formulário é enviado com uma pergunta
    if submitted and pergunta_usuario:
        # Verifica se a chave de API foi fornecida
        if google_api_key:
            # Mostra um spinner na interface enquanto o agente trabalha
            with st.spinner("O Gemini está pensando... 🧠 (verifique o terminal para o log detalhado)"):
                
                # Define o prompt de sistema para guiar o agente
                AGENT_PREFIX = "Você é um especialista em análise de dados de arquivos CSV, com foco em notas fiscais. Sua principal função é extrair, interpretar e apresentar insights claros e precisos a partir dos dados fornecidos. Você deve responder às perguntas do usuário utilizando as informações contidas no DataFrame, sem fazer suposições ou extrapolações."
                
                # Inicializa o modelo de linguagem
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, temperature=0)

                # Cria a instância do agente, passando o LLM e o DataFrame
                agent = create_pandas_dataframe_agent(
                    llm, 
                    df, 
                    prefix=AGENT_PREFIX, 
                    verbose=False, # Desliga o logger padrão do LangChain
                    allow_dangerous_code=True
                )
                
                try:
                    # Instancia nosso handler final, dando um nome profissional ao agente
                    handler = PolishedCallbackHandler(agent_name="Analista de Dados de NF-e")

                    # Executa o agente com a pergunta do usuário usando o método mais recente
                    resposta = agent.invoke(
                        {"input": pergunta_usuario},
                        config={"callbacks": [handler]}
                    )

                    # Adiciona a conversa ao histórico e atualiza a interface
                    st.session_state.chat_history.insert(0, {"pergunta": pergunta_usuario, "resposta": resposta['output']})
                    st.rerun()

                except Exception as e:
                    # Exibe uma mensagem de erro na interface em caso de falha
                    st.error(f"Ocorreu um erro ao executar o agente: {e}")
        else:
            st.warning("A chave de API do Google é necessária para esta funcionalidade.")

    st.markdown("---")

    # Exibe o histórico de conversas da sessão atual
    if st.session_state.chat_history:
        st.subheader("Histórico da Sessão Atual")
        for i, conversa in enumerate(st.session_state.chat_history):
            with st.container(border=True):
                st.info(f"**Você perguntou:** {conversa['pergunta']}")
                st.success(f"**Resposta do Agente:** {conversa['resposta']}")
                
                # Botão para adicionar a conversa ao relatório final
                if st.button("📌 Adicionar ao Relatório", key=f"pin_qa_{i}"):
                    item_para_adicionar = {
                        "type": "qa", 
                        "category": "q&a",
                        "title": f"Pergunta: {conversa['pergunta'][:50]}...",
                        "content": conversa
                    }
                    if item_para_adicionar not in st.session_state.report_items:
                        st.session_state.report_items.append(item_para_adicionar)
                        st.success("Adicionado ao relatório! Veja na barra lateral.")
                        st.rerun()
                    else:
                        st.warning("Este item já foi adicionado ao relatório.")