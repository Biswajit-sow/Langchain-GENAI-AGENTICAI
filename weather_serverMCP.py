from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather", port=8000)

@mcp.tool()
def get_weather(location: str) -> str:
    """Get the weather for a given location (mocked example)"""
    return f"It's sunny and 25°C in {location}."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")