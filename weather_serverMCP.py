from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather", port=8000)

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the weather for a given location (mocked example)"""
    return f"It's sunny a nd 25°C in California."
# here I just et's say that this is output of my API that I am getting here.you can write any code with respect to interacting with some kind of API

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

#when I run this in terminal it run a particular URL  as we use Streamable-http as an API service itself.Similary if I run the math server in STDIO it will not run like this 