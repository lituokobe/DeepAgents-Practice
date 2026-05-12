import asyncio

import yaml
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from agent.my_llm import qwen_llm
from agent.my_tools import web_search
from multi_agent.mcp_tool_config.mcp_tool_config import mcp_client

async def load_subagents(config_path:str):
    """Read configuration file and load subagents"""
    # xsct_tools = await mcp_client.get_tools(server_name="xsct")
    chart_tools = await mcp_client.get_tools(server_name="fenxi")
    # print(xsct_tools)
    available_tools = {
        # "xsct": xsct_tools,
        "fenxi": chart_tools,
        "web_search": [web_search],
    }

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) # load the subagents configuration from YAML

    subagents = []
    for name, spec in config.items():
        subagent = {
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
        }
        if "model" in spec:
            subagent["model"] = spec["model"]

        if "tools" in spec:
            tools = [available_tools[t] for t in spec["tools"]]
            print(tools)
            subagent["tools"] = tools[0]

        # subagent['middleware'] = ToolCallLimitMiddleware(tool_name="execute_python", run_limit=3) # 限制代码执行最多3次
        subagents.append(subagent)
    return subagents

async def create():
    subagents = await load_subagents("/Users/lituokobe/Desktop/Mashibing_LLM_course/37_DeepAgents_practice/multi_agent/subagents.yaml")
    return create_deep_agent(
        model=qwen_llm,
        tools=[web_search],
        # checkpointer=checkpointer,
        memory=["/Users/lituokobe/Desktop/Mashibing_LLM_course/37_DeepAgents_practice/multi_agent/AGENTS.md"], # load with MemoryMiddleware, the system prompt for this one
        backend=FilesystemBackend(root_dir="./agent_workspace"),
        subagents=subagents
    )

agent = asyncio.run(create())