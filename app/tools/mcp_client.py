from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            "banking_mcp": {
                "url": "http://mcp_server:8001/mcp",
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()
    return tools