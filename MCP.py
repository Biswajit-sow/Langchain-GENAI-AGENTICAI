import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_groq import ChatGroq   # <-- make sure this line is present
import os 
import sys


load_dotenv()  # or specify path explicitly below
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found!")


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": sys.executable ,
                "args": [ r"F:\AI\Langchain-GENAI-AGENTICAI\Math_MCP_server.py"],#Ensure correct absolute path
            },

            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp", # ensure the server is running and accessible at this URL and when i give /MCP that will able to get weather MCP server that is running
            }
        }
    )

    tools = await client.get_tools()# get tools means get information of that cleint tool or weather and math here 
    model=ChatGroq(model="openai/gpt-oss-120b")
    '''agent = create_agent(
        model=model,
        tools=tools
    )'''
    agent = create_react_agent(
        model=model,tools=tools
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is 8 plus 5??"}]}
    )

    print("Math_Response",math_response["messages"][-1].content)
    
    


if __name__ == "__main__":
    asyncio.run(main())