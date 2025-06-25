# utils/callbacks.py

from typing import Any
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
import re

# A classe de cores permanece a mesma, apenas a forma como a usamos vai mudar.
class BColors:
    HEADER = '\033[95m'    # Magenta
    OKBLUE = '\033[94m'    # Azul
    OKCYAN = '\033[96m'    # Ciano
    OKGREEN = '\033[92m'   # Verde
    WARNING = '\033[93m'   # Amarelo
    FAIL = '\033[91m'      # Vermelho (reservado para erros)
    ENDC = '\033[0m'       # Fim da formatação
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Callback Handler com cores padronizadas e profissionais
class PolishedCallbackHandler(BaseCallbackHandler):
    """
    Formata os logs com um esquema de cores semântico e profissional.
    """
    def __init__(self, agent_name="Analista de Dados"):
        super().__init__()
        self.agent_name = agent_name
        # ALTERADO: Cor do cabeçalho padronizada para Ciano.
        print(f"\n{BColors.BOLD}{BColors.OKCYAN}🚀 Iniciando nova execução para o agente: {self.agent_name}{BColors.ENDC}")
        print("─" * 80)

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """
        Formata o Pensamento (Azul) e a Ação (Verde).
        """
        thought = re.split(r'Action:|Thought:', action.log)[1].strip()
        
        # ALTERADO: Cor do Pensamento padronizada para Azul.
        print(f"{BColors.BOLD}{BColors.OKBLUE}🤔 PENSAMENTO{BColors.ENDC}")
        print(thought)
        
        # Cor da Ação permanece Verde.
        print(f"\n{BColors.BOLD}{BColors.OKGREEN}⚡ AÇÃO{BColors.ENDC}")
        print(f"   - Ferramenta: {BColors.BOLD}{action.tool}{BColors.ENDC}")
        
        clean_input = action.tool_input.strip().strip("```python").strip("```").strip()
        # ALTERADO: Cor do bloco de código padronizada para Amarelo.
        print(f"   - Código a executar:\n{BColors.WARNING}```python\n{clean_input}\n```{BColors.ENDC}")

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """
        Formata a Observação (Magenta).
        """
        # ALTERADO: Cor da Observação padronizada para Magenta.
        print(f"\n{BColors.BOLD}{BColors.HEADER}📝 OBSERVAÇÃO{BColors.ENDC}")
        print(output)
        print("─" * 80)

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """
        Formata a Resposta Final (Ciano, igual ao cabeçalho).
        """
        final_answer = finish.return_values.get('output', 'N/A')
        # ALTERADO: Cor da Resposta Final padronizada para Ciano.
        print(f"\n{BColors.BOLD}{BColors.OKCYAN}✅ RESPOSTA FINAL{BColors.ENDC}")
        print(final_answer)
        print("\n" + "="*80 + "\n")