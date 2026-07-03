import asyncio

from acp import run_agent
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

from deepagents_acp.server import AgentServerACP
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()
import os

print("GROQ_API_KEY loaded:", os.getenv("GROQ_API_KEY") is not None)


async def main():
    print("Creating Deep Agent...")

    agent = create_deep_agent(
        model=ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0,
        ),
        system_prompt="You are a helpful coding assistant",
        checkpointer=MemorySaver(),
        backend=FilesystemBackend(
            root_dir=r"F:\AI\Langchain-GENAI-AGENTICAI",
            virtual_mode=True,
        ),
    )

    print("Deep Agent created!")

    server = AgentServerACP(agent)

    print("ACP Server is starting...")

    await run_agent(server)

    print("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())