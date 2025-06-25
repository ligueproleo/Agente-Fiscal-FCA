
# 🚀 Plataforma de Análise de Notas Fiscais com Agentes de IA

Esta é uma plataforma de Business Intelligence (BI) e Análise de Dados inovadora, que emprega o poder de agentes de Inteligência Artificial para transformar dados brutos de Notas Fiscais (em formato CSV) em dashboards interativos, análises fiscais automáticas e relatórios profissionais em formato `.docx`.

---

## ✨ Funcionalidades Principais

A aplicação é organizada em cinco abas principais, cada uma projetada com um propósito claro para otimizar sua análise fiscal:

### 💬 Agente Q&A

Uma interface de chat intuitiva que permite fazer perguntas específicas em linguagem natural diretamente ao conjunto de dados. Ideal para investigações pontuais e obtenção rápida de informações.

### 💡 Insights da IA

Ferramenta de "um clique" que instrui o agente a responder a 10 perguntas de negócio fundamentais. Gera um relatório de insights automáticos que pode ser facilmente adicionado ao documento final.

### 📊 Dashboard

Um painel de controle visual e interativo que oferece uma visão abrangente dos seus dados:

- **Mapeamento de Colunas:** Permite ao usuário mapear as colunas do seu arquivo para conceitos de negócio essenciais (Cliente, Produto, Quantidade), garantindo a adaptabilidade da ferramenta a diversas fontes de dados.
- **KPIs Dinâmicos:** Exibe os principais indicadores de performance (Faturamento Total, Itens Vendidos, etc.).
- **Gráficos Curados:** Apresenta análises visuais automáticas dos Top 10 Clientes, Top 10 Produtos e Vendas ao Longo do Tempo.

### ✅ Análise Fiscal

Um painel dedicado à auditoria fiscal, que executa análises cruciais baseadas nas colunas disponíveis no arquivo. Inclui verificações de consistência de valores e análise detalhada de operações por CFOP.

### 📄 Montador de Relatório

Área de preparação para o relatório final:

- **Preview Interativo:** Exibe todos os itens "pinados" (gráficos, tabelas, insights) para revisão.
- **Gerenciamento:** Permite remover itens individualmente antes da exportação.
- **Exportação Profissional:** Gera um documento `.docx` de alta qualidade, com capa, títulos e gráficos renderizados como imagens nítidas.

---

## 🛠️ Stack de Tecnologias

- **Linguagem:** Python 3.11+
- **Framework Web/UI:** Streamlit
- **Análise de Dados:** Pandas
- **Inteligência Artificial (LLM):** Google Gemini Pro / Flash
- **Orquestração de Agentes:** LangChain, LangChain Experimental
- **Visualização de Dados:** Plotly Express
- **Geração de Documentos:** `python-docx`
- **Exportação de Gráficos:** `Kaleido`
- **Mecanismo de Retry:** `Tenacity`

---

## 📂 Estrutura do Projeto
