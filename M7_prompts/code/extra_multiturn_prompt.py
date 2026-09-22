"""Extra: a prompt that pre-fills a conversation, not just one instruction.

Prompts may return a list of Messages with mixed roles. The message order becomes the
history the model sees, so a prompt can seed more than one turn.

Run:
    uv run python -m M7_prompts.code.extra_multiturn_prompt
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("multi-turn")


@mcp.prompt
def guided_diagnosis(service: str) -> list[Message]:
    """Walk a diagnosis as an alternating conversation.

    Args:
        service: The service under diagnosis.
    """
    return [
        Message(f"We will diagnose {service} in three turns. Confirm you understand.", role="user"),
        Message("Understood. I will wait for the evidence before concluding.", role="assistant"),
        Message("Turn 1: state which metric you need first, and why.", role="user"),
    ]


async def main() -> None:
    async with Client(mcp) as client:
        print("=== one argument, three messages ===")
        rendered = await client.get_prompt("guided_diagnosis", {"service": "postgres-ha"})
        print(f"  messages={len(rendered.messages)}")
        for index, message in enumerate(rendered.messages, 1):
            print(f"  {index}. role={message.role:9} {message.content.text}")

        print("\n=== the roles survive the wire ===")
        roles = [message.role for message in rendered.messages]
        print(f"  {roles}")
        print(f"  alternates user/assistant: {roles == ['user', 'assistant', 'user']}")

        print("\n=== a host that only reads messages[0] would lose turns 2 and 3 ===")
        print(f"  messages[0].content.text -> {rendered.messages[0].content.text}")
        print(f"  total characters across messages: {sum(len(m.content.text) for m in rendered.messages)}")


if __name__ == "__main__":
    asyncio.run(main())
