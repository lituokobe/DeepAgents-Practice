from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

from llm.my_llm import qwen_llm
from agent.my_tools import web_search

checkpointer = InMemorySaver()

agent = create_deep_agent(  # a more advanced version of LangChain's create_agent
    model=qwen_llm,
    tools=[web_search],
    checkpointer=checkpointer,
    system_prompt="""You are a helpful assistant. Please act per user's instruction.""",
)