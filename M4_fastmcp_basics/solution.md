# M4 — လေ့ကျင့်ခန်းများ၏ အဖြေများ (solution)

## လေ့ကျင့်ခန်း ၁ — ပထမဆုံး FastMCP server ကို ရေးခြင်း

```python
# hello_server.py — your first FastMCP server
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

# The name passed to FastMCP is reported to the client during initialize
mcp = FastMCP("course-hello")


@mcp.tool
def hello() -> str:
    """Return a friendly greeting."""
    return "Mingalarpar from MCP!"


def main() -> None:
    # main() is where the transport is chosen
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

`FastMCP("name")` တွင်ပေးသည့် အမည်သည် `initialize` handshake အတွင်း client ထံ အစီရင်ခံခြင်းခံရသောကြောင့် အမည်ကို စနစ်တကျ ပေးရမည်။

**အဓိကအယူအဆ** — server ၏ အမည်သည် လှပမှုအတွက် မဟုတ်ဘဲ `initialize` handshake တွင် client ထံ ပေးပို့သည့် စနစ်တကျ အချက်အလက်တစ်ခု ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — Server object နှင့် tool များကို code ဖြင့် စစ်ခြင်း

```python
# Check the server object and its tools without running the transport
from hello_server import mcp


def main() -> None:
    # The name we gave to FastMCP is stored on the object
    print("server name:", mcp.name)

    # List every tool that has been registered on this server
    tools = mcp.list_tools()
    for tool in tools:
        print("tool:", tool.name, "-", tool.description)


if __name__ == "__main__":
    main()
```

server ကို run မူင်မီဘဲ `mcp.name` နှင့် `mcp.list_tools()` ဖြင့် registration မှန်ကန်မှုကို စစ်ဆေးနိုင်သည်။

**အဓိကအယူအဆ** — transport ကို စတင်ချင်းမပြောင်းနိုင်မီ code အနေဖြင့် server object ထံမှ အချက်အလက်များကို တိုက်ရိုက် ဖတ်နိုင်သည်။

## လေ့ကျင့်ခန်း ၃ — Tool တစ်ခုကို အပြင်ဘက်မှ စစ်ခြင်း (registration audit)

```python
# Registration audit: verify that a tool exists and is callable
from hello_server import mcp


def main() -> None:
    tool_names = [tool.name for tool in mcp.list_tools()]

    # The decorator must have registered our tool under its function name
    if "hello" in tool_names:
        print("hello tool is registered")
    else:
        print("hello tool is MISSING")

    # A wrongly wrapped tool would not appear here
    print("all registered tools:", tool_names)


if __name__ == "__main__":
    main()
```

`@mcp.tool` သည် function ၏ အမည်ဖြင့် tool ကို register လုပ်သောကြောင့် အမည်စာရင်းကို စစ်ခြင်းသည် အတည်ပြုခြင်း၏ အလွယ်ဆုံးနည်း ဖြစ်သည်။

**အဓိကအယူအဆ** — `@mcp.tool` ကို ထိပ်တွင်ထားသည့် wrapper ပုံစံ မှားလျှင် tool သည် ဇယားထဲ လုံးဝ မရောက်တော့သောကြောင့် registration audit သည် အန္တရာယ်အကြီးဆုံး အမှားကို ဖမ်းနိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — stdio round trip နှင့် `print()` ထောင်ချောက်

```python
# Run a stdio round trip and see how one print() can break the protocol
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # Client(Path) spawns the server as a child process
    server_params = StdioServerParameters(command="python", args=["hello_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            result = await session.call_tool("hello", {})
            print("result:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

server က `print()` တစ်ကြောင်း ထုတ်လိုက်လျှင် JSON-RPC message မဟုတ်သည့် data က `stdout` လိုင်းတွင် ရောပြီး protocol ကို ဖျက်ဆီးသည်။

**အဓိကအယူအဆ** — stdio transport တွင် `stdout` သည် protocol ၏ ပိုင်ဆိုင်မှု ဖြစ်သောကြောင့် server အတွင်း `print()` တစ်ကြောင်းကသာ protocol တစ်ခုလုံးကို ဖျက်ဆီးနိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — တူညီသည့် server ကို HTTP ဖြင့် ခေါ်ခြင်း

```python
# Call the same server over HTTP instead of stdio
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    # The server must already be listening on this URL
    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools over HTTP:", [t.name for t in tools.tools])

            result = await session.call_tool("hello", {})
            print("result:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

HTTP transport တွင် server က စောင့်ပြီး client က dial လုပ်၍ `print()` ကိုလည်း ဘေးကင်းစွာ ရေးနိုင်သည်။

**အဓိကအယူအဆ** — transport ပြောင်းလိုက်ရုံသာဖြစ်ပြီး tool များနှင့် ၎င်းတို့၏ schema များမှာ မပြောင်းလဲသောကြောင့် HTTP သည် server တစ်ခုတည်းကို ကွန်ရက်တစ်ခုလုံးသို့ ရောက်စေသည်။

## လေ့ကျင့်ခန်း ၆ — Client တစ်ခု ရေးပြီး server ကို ရှာဖွေခြင်း

```python
# Discover a server from a client: list tools, then call one
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command="python", args=["hello_server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # list_tools tells us what the server publishes
            tools = await session.list_tools()
            for tool in tools.tools:
                print("name:", tool.name)
                print("input_schema:", tool.inputSchema)

            # call_tool actually invokes it
            result = await session.call_tool("hello", {})
            print("output:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

`list_tools` သည် server က ထုတ်ပြသမျှကို ဖော်ပြပြီး `call_tool` သည် ၎င်းတို့ကို တကယ် ခေါ်ဆိုပေးသည်။

**အဓိကအယူအဆ** — client ၏ ရှာဖွေမှုသည် `initialize` → `list_tools` → `call_tool` ဟူသော အစီအစဉ်အတိုင်း လျှောက်လည်းသွားသည့် pattern တစ်ခုသာ ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၇ — `is_error` နှင့် `structured_content` ကို တိုင်းတာခြင်း

```python
# Measure is_error and structured_content on a real call
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command="python", args=["hello_server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("hello", {})

            # A successful call is NOT a raise — it is a result object
            print("is_error:", result.isError)
            print("structured_content:", result.structuredContent)

            # Check is_error BEFORE trusting any output
            if result.isError:
                print("the tool failed:", result.content[0].text)
            else:
                print("the tool succeeded")


if __name__ == "__main__":
    asyncio.run(main())
```

`is_error=False` ဖြစ်စေကာမူ tool ၏ အတွင်းအခြေအနေအရ ဆိုင်ရလဒ် ကျရှုံးနိုင်သောကြောင့် `isError` ကို ယုံကြည်မီ အရင်စစ်ရမည်။

**အဓိကအယူအဆ** — tool ၏ ကျရှုံးမှုကို exception အဖြစ် မမြင်ရဘဲ `is_error` ထဲ ဝင်ရောက်နေတတ်သောကြောင့် result object ကို စစ်ဆေးခြင်းသည် ယုံကြည်မှု၏ ပထမဆုံးအဆင့် ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၈ — Schema ကို နှစ်ဖက်မှ တိုင်းတာ၍ နှိုင်းယှဉ်ခြင်း

```python
# Read .parameters on the server side and .inputSchema on the client side
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from hello_server import mcp


def server_side() -> None:
    # On the server, FastMCP keeps the schema under .parameters
    for tool in mcp.list_tools():
        print("server-side schema:", tool.parameters)


async def client_side() -> None:
    params = StdioServerParameters(command="python", args=["hello_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for tool in tools.tools:
                # On the client, the same schema appears as .inputSchema
                print("client-side schema:", tool.inputSchema)


async def main() -> None:
    server_side()
    await client_side()


if __name__ == "__main__":
    asyncio.run(main())
```

ဇယားတွင် `.parameters` ကို server-side နှင့် `.inputSchema` ကို client-side ဟူ၍ ခေါ်ဆိုသည့် နာမည်များ မတူသော်လည်း schema မှာ တစ်ခုတည်းသာ ဖြစ်သည်။

**အဓိကအယူအဆ** — schema သည် server မှ client အထိ JSON Schema အဖြစ် ခရီးဆက်သွားပြီး နာမည်တစ်ခုစီသည် ကြည့်ရှုနေသည့် ဘက်ပေါ်တွင် မူတည်သည်။

## လေ့ကျင့်ခန်း ၉ — Calculator + Currency server ကို transport နှစ်မျိုးဖြင့် ခေါ်ခြင်း

```python
# Drive the same currency server over both stdio and HTTP
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def via_stdio() -> None:
    params = StdioServerParameters(command="python", args=["lab_5_currency_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("stdio tools:", [t.name for t in tools.tools])


async def main() -> None:
    # First half: stdio (client spawns the server)
    await via_stdio()
    # Second half: start the HTTP server yourself, then run the client again
    # uv run lab_5_currency_server.py --transport http --host 127.0.0.1 --port 8000
    print("now run lab_3_http_client.py against the running HTTP server")


if __name__ == "__main__":
    asyncio.run(main())
```

server တစ်ခုတည်းကို transport နှစ်မျိုးဖြင့် ခေါ်ဆိုခြင်းသည် hybrid ပုံစံဖြစ်ပြီး tool များ လုံးဝ မပြောင်းလဲပါ။

**အဓိကအယူအဆ** — tool များသည် transport နှင့် ဘာသာမကွာသောကြောင့် server တစ်ခုကို လုပ်ငန်းအခြေအနေအလိုက် stdio သို့မဟုတ် HTTP ဖြင့် ကွဲပြားစွာ တွဲဖက်အသုံးပြုနိုင်သည်။
