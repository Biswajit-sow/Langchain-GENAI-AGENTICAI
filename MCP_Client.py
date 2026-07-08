from mcp.server.fastmcp import FastMCP
from typing import Union

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a) + int(b)

@mcp.tool()
def multiply(a: Union[int, str], b: Union[int, str]) -> int:
    """Multiply two numbers"""
    return int(a) * int(b)

if __name__ == "__main__":
    mcp.run(transport="stdio")