
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from acp import run_agent
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from deepagents_acp.server import AgentServerACP
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Log to a file instead of ACP stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("acp_server.log", encoding="utf-8")
    ],
    force=True,
)

async def main():
    logging.info("Starting ACP server")

    try:
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY is missing")

        logging.info("GROQ_API_KEY loaded")

        model = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
        )

        logging.info("Creating Deep Agent")

        agent = create_deep_agent(
            model=model,
            system_prompt="You are a helpful coding assistant",
            checkpointer=MemorySaver(),
            backend=FilesystemBackend(
                root_dir=r"F:\AI\Langchain-GENAI-AGENTICAI",
                virtual_mode=True,
            ),
        )

        logging.info("Deep Agent created")

        server = AgentServerACP(agent)

        logging.info("ACP server starting")

        await run_agent(server)

    except Exception:
        logging.exception("ACP server encountered an error")
        raise

if __name__ == "__main__":
    asyncio.run(main())
