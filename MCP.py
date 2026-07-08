import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_groq import ChatGroq   # <-- make sure this line is present
import os


load_dotenv()  # or specify path explicitly below
os.getenv("GROQ_API_KEY")


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [r"F:\AI\Langchain-GENAI-AGENTICAI\MCP_Client.py"],
            },

            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent(
        model=ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
        ),
        tools=tools
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is 8 plus 5??"}]}
    )

    weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(weather_response["messages"][-1].content)
    print(math_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())