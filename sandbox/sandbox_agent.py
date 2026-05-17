import asyncio
import yaml
from deepagents import create_deep_agent
from deepagents.middleware import SummarizationToolMiddleware
from langchain.agents.middleware import SummarizationMiddleware

from llm.my_llm import qwen_llm
from agent.my_tools import web_search
from multi_agent.mcp_tool_config.mcp_tool_config import mcp_client
from sandbox.OpenSandboxBackend_by_Tuo import OpenSandboxBackend
from sandbox.opensandbox_opt import get_or_create_sandbox, config, sync_skills_to_sandbox


async def load_subagents(config_path:str):
    """Read configuration file and load subagents"""
    chart_tools = await mcp_client.get_tools(server_name="fenxi")
    available_tools = {
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
    sandbox=get_or_create_sandbox(config)
    backend = OpenSandboxBackend(sandbox=sandbox)
    sandbox_skills_path = "/workspace/skills"
    local_skills_path = "/Users/lituokobe/Desktop/Mashibing_LLM_course/37_DeepAgents_practice/skills"

    # 智能同步技能到沙箱
    uploaded_count = sync_skills_to_sandbox(backend, local_skills_path, sandbox_skills_path)

    with open("/Users/lituokobe/Desktop/Mashibing_LLM_course/37_DeepAgents_practice/multi_agent/AGENTS.md", 'r', encoding='utf-8') as f:
        content = f.read()

    # 上传到沙箱
    result = backend.upload_files([('/AGENTS.md', content.encode("utf-8"))])

    if uploaded_count > 0:
        print(f"✅ 成功上传了 {uploaded_count} 个新技能到沙箱")
    else:
        print("✅ 所有技能已存在于沙箱中，无需上传")

    return create_deep_agent(
        model=qwen_llm,
        skills=[sandbox_skills_path],
        tools=[web_search],
        memory=["/AGENTS.md"], # load with MemoryMiddleware, the system prompt for this one
        backend=backend,
        subagents=subagents
    )

agent = asyncio.run(create())