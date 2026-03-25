from fastmcp import FastMCP
from tools.sql import run

mcp = FastMCP(
  name = "各种助手",
  instructions="""
    这个服务提供了一系列工具。
  """,
)
mcp.add_tool(run)

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
