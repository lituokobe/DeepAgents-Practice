import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
load_dotenv(override=True)

# 数据分析报表的MCP服务端（工具的配置）
analysis_mcp_server_config = {
    "url": "https://mcp.api-inference.modelscope.net/39d9031d0b7144/mcp", # MCP from https://www.modelscope.cn/mcp/servers/antvis/mcp-server-chart
    "transport": "streamable_http",
}

# 创建一个mcp的客户端
mcp_client = MultiServerMCPClient({
    "fenxi": analysis_mcp_server_config,
})

if __name__ == '__main__':
    print( f"Bearer {os.getenv('MODELSCOPE_API_KEY')}")
