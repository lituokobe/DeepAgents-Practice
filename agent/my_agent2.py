import os

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import InMemorySaver

from llm.my_llm import qwen_llm
from agent.my_tools import web_search

checkpointer = InMemorySaver()

temp_workspace = "./agent_workspace"
os.makedirs(temp_workspace, exist_ok=True)

agent = create_deep_agent(  # a more advanced version of LangChain's create_agent
    model=qwen_llm,
    tools=[web_search],
    checkpointer=checkpointer,
    backend=FilesystemBackend(
      root_dir=temp_workspace,
      virtual_mode=True #prevent agents to visit outside path
    ),
    system_prompt="""You are a helpful assistant. Please act per user's instruction.""",
)