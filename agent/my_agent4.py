import os
import sys

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langgraph.checkpoint.memory import InMemorySaver

from agent.my_backend import DictBackend
from agent.my_llm import qwen_llm
from agent.my_tools import web_search

checkpointer = InMemorySaver()

agent = create_deep_agent(  # a more advanced version of LangChain's create_agent
    model=qwen_llm,
    tools=[web_search],
    checkpointer=checkpointer,
    backend=DictBackend(),
    system_prompt="""You are a helpful assistant. Please act per user's instruction.""",
)

if __name__ == '__main__':
    print(os.path.dirname(sys.executable))
    print(os.environ.get('PATH', ''))
    print(f"{os.path.dirname(sys.executable)};{os.environ.get('PATH', '')}")