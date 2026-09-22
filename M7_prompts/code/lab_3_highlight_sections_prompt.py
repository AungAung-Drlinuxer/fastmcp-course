"""LAB 3 — highlight_sections_prompt: the measured anchor lab for Lesson 2.4.

Builds the `highlight_sections` prompt from M7_prompts/code/highlight.py into a standalone
host contract, then checks the two things that matter:

  * the declared arguments match the function signature exactly (the host form is generated,
    never hand-written), and
  * the rendered text contains the count the user asked for, and refuses to pad.

Run:
    uv run python -m M7_prompts.code.lab_3_highlight_sections_prompt
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab3-highlight-sections")


@mcp.prompt
def highlight_sections_prompt(article: str, count: int = 3) -> str:
    """Ask for the most important sections of an article, and justify each choice.

    Args:
        article: The article title to summarise.
        count: How many sections to highlight.
    """
    return (
        f"Read the article {article!r}. Choose the {count} sections that matter most to "
        "someone who has ten minutes and needs the operative content — not the history, not "
        "the trivia.\n\n"
        "For each one, give: the section title, a two-sentence summary, and one line saying "
        "WHY it beats the sections you left out. If the article has fewer than "
        f"{count} substantive sections, say so instead of padding."
    )


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the declared contract ===")
        prompt = (await client.list_prompts())[0]
        declared = [a.name for a in (prompt.arguments or [])]
        print(f"  name:        {prompt.name}")
        print(f"  description: {prompt.description}")
        print(f"  arguments:   {declared}")
        for argument in prompt.arguments or []:
            print(f"    {argument.name:10} required={argument.required}  {argument.description}")

        print("\n=== render with count=2 ===")
        rendered = await client.get_prompt("highlight_sections_prompt",
                                           {"article": "Postgres 17 release notes", "count": 2})
        text = rendered.messages[0].content.text
        print(f"  messages={len(rendered.messages)} chars={len(text)}")
        print(f"  mentions '2 sections': {'the 2 sections' in text}")
        print(f"  refuses to pad:        {'instead of padding' in text}")
        print(f"  anti-padding guard at: index {text.index('If the article has fewer')}")

        print("\n=== render with the default (count not sent) ===")
        rendered = await client.get_prompt("highlight_sections_prompt",
                                           {"article": "Postgres 17 release notes"})
        text = rendered.messages[0].content.text
        print(f"  mentions '3 sections': {'the 3 sections' in text}")

        print("\n=== the exact text the model would receive ===")
        print(rendered.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
