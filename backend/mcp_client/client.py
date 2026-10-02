from fastmcp import Client

mcp_client = Client("http://127.0.0.1:8000/mcp")




async with mcp_client:
    tools = await mcp_client.list_tools()

    print(tools)