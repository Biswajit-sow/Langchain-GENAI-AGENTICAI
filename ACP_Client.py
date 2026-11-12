import asyncio
import sys
from typing import Any
from uuid import uuid4

from acp import PROTOCOL_VERSION, spawn_agent_process, text_block
from acp.interfaces import Client


class SimpleClient(Client):
    async def request_permission(self, options, session_id, tool_call, **kwargs: Any):
        # auto-approve the first offered option
        return {"outcome": {"outcome": "selected", "optionId": options[0].option_id}}

    async def session_update(self, session_id, update, **kwargs):
        if update.session_update == "agent_message_chunk":
            print(update.content.text, end="", flush=True)
        elif update.session_update == "tool_call":
            print(f"\n[tool call: {update.title}]", flush=True)
        elif update.session_update == "tool_call_update":
            print(f"\n[tool update: {update.status}]", flush=True)


async def main() -> None:
    async with spawn_agent_process(
        SimpleClient(),
        sys.executable,
        "ACP.py",
    ) as (conn, _proc):
        await conn.initialize(protocol_version=PROTOCOL_VERSION)

        session = await conn.new_session(cwd=".", mcp_servers=[])

        await conn.prompt(
            session_id=session.session_id,
            prompt=[text_block("Create a file called notes.txt with the text 'hello from ACP'")],
            message_id=str(uuid4()),
        )
        print()  # newline at the end


if __name__ == "__main__":
    asyncio.run(main())