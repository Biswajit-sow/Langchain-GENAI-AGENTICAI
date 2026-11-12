import asyncio
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from utcp.utcp_client import UtcpClient

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Groq API key not found!")


async def build_tools(client: UtcpClient):
    """Turn UTCP tools into LangChain tools."""
    utcp_tools = await client.search_tools("", limit=50)  # empty query = list tools
    lc_tools = []

    for t in utcp_tools:
        # UTCP names look like "math.add"; LLM function names can't contain "."
        safe_name = t.name.replace(".", "__")

        def make_coro(utcp_name):
            async def _call(**kwargs):
                result = await client.call_tool(utcp_name, kwargs)
                return str(result)
            return _call

        lc_tools.append(
            StructuredTool(
                name=safe_name,
                description=t.description,
                args_schema=t.inputs.model_dump(by_alias=True, exclude_none=True),
                coroutine=make_coro(t.name),
            )
        )
    return lc_tools


async def main():
    client = await UtcpClient.create(config={
        "manual_call_templates": [
            {
                "name": "math",
                "call_template_type": "http",
                "http_method": "GET",
                "url": "http://localhost:8001/utcp",   # math manual
            },
            {
                "name": "weather",
                "call_template_type": "http",
                "http_method": "GET",
                "url": "http://localhost:8000/utcp",   # weather manual
            },
        ]
    })

    tools = await build_tools(client)
    model = ChatGroq(model="openai/gpt-oss-120b")
    agent = create_agent(model=model, tools=tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is 8 plus 5??"}]}
    )
    print("Math_Response", math_response["messages"][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in California??"}]}
    )
    print("Weather_Response", weather_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())