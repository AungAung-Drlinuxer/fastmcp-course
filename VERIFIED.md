# VERIFIED — every claim in this course, checked against the real API

Every lesson here was **executed** against the pinned version before it was written. This file
records what the API actually does, including the places where the widely-circulated FastMCP
2.x documentation is now wrong.

```text
Environment at verification time
  fastmcp   4.0.5
  pydantic  2.13.5
  python    3.11.x
  date      2026-09-19
```

## The API moved between major versions — this is the first thing to check

A student following a 2.x tutorial cannot tell "I made a mistake" from "the API moved". These
are the differences that were measured, each with the error you get if you use the old name.

| 2.x documentation says | What 4.0.5 actually has | What you see if you use the old name |
|---|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | `ImportError: cannot import name 'ElicitationResult'` |
| `tool.inputSchema` | `tool.parameters` | `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` (the error suggests `uri_template`) |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError: 'FastMCP' object has no attribute 'get_tools'` |

### The same tool exposes its schema under a DIFFERENT name per side

This one is not in the comparison tables anywhere, and it is the easiest to hit because both
names look right:

| Where you are | Object type | Read the schema as |
|---|---|---|
| **server**: `await mcp.list_tools()` | `fastmcp.tools.function_tool.FunctionTool` | `.parameters` |
| **client**: `await client.list_tools()` | `mcp_types._types.Tool` | `.input_schema` |

```text
AttributeError: 'Tool' object has no attribute 'parameters'
```

and the tempting middle name is deprecated rather than absent:

```text
FastMCPDeprecationWarning: Accessing `Tool.inputSchema` is deprecated; MCP SDK v2 renamed this
field to `input_schema`. Update your code to read `.input_schema` instead.
```

So a lesson written against the server-side objects breaks the moment a student reads tools
through a client — which is what every real integration does.

## ⚠️ The one that costs the most time: elicitation needs `mode="legacy"`

`Client(mcp)` defaults to `mode="auto"`, which negotiates the modern **`2026-07-28`** protocol
era. That era is sessionless and **does not support server-initiated requests**, so a tool that
calls `ctx.elicit(...)` fails at call time:

```text
fastmcp.exceptions.ToolError: elicitation via server-initiated requests is unavailable on
                             2026-07-28 connections.
```

Verified working configuration:

```python
async with Client(mcp, mode="legacy", elicitation_handler=handler) as client:
    ...
# client.protocol_version == "2025-11-25"  (the handshake era)
```

Measured across modes:

| `mode=` | result |
|---|---|
| *(default / `"auto"`)* | `ToolError: ... unavailable on 2026-07-28 connections` |
| `"legacy"` | works; `protocol_version == "2025-11-25"` |
| `"2026-07-28"` | adopts that era directly — elicitation unavailable |
| `"2025-06-18"` / `"2025-03-26"` | `ValueError: mode must be 'legacy', 'auto', or one of ['2026-07-28']` |

Only `"legacy"`, `"auto"` and `"2026-07-28"` are accepted values.

## The elicitation handler contract

```python
ElicitationHandler = Callable[
    [str,                              # message
     type[T] | None,                   # the response model (None for URL-mode elicitation)
     ElicitRequestParams,              # the raw params
     RequestContext[...]],             # request context
    Awaitable[T | dict[str, Any] | ElicitResult[T | dict[str, Any]]],
]
```

Four parameters, and it **must be async**. Measured failures:

```text
# wrong arity
MCPError: handler() takes from 2 to 3 positional arguments but 4 were given

# sync handler (even one returning the right value)
ToolError: Error calling tool 'restart_service': object dict can't be used in 'await' expression
ToolError: Error calling tool 'restart_service': object ElicitResult can't be used in 'await' expression
```

The callback awaits the handler unconditionally, so a plain `def` that returns a dict — which
looks completely reasonable — fails on the `await`.

The three outcomes come from the **return value**, not from exceptions:

```python
return {"date": "...", "seat": "..."}        # accept
return ElicitResult(action="decline")        # the user said no
return ElicitResult(action="cancel")         # the user abandoned the flow
```

Measured server-side result for each:

```text
accept   -> {'ok': True,  'status': 'booked',  'booking': {...}}
decline  -> {'ok': False, 'status': 'decline'}
cancel   -> {'ok': False, 'status': 'cancel'}
```

## Prompts: a custom return type must be wrapped, and it fails LATE

Returning a dataclass from `@mcp.prompt` registers fine and `list_prompts()` succeeds; the
failure appears only when a client retrieves the prompt:

```text
MCPError: Error rendering prompt 'dns_lookup_failure': messages[0] must be Message or str,
          got GuidedStep. Use Message(GuidedStep(...)) to wrap the value.
```

The working form, from `fastmcp.prompts`:

```python
from fastmcp.prompts import Message
return [Message(step) for step in steps]     # Message(content, role="user")
```

Lesson: **a registration that succeeds is not a prompt that renders.**

## Schema generation from type hints (the Phase 1 payoff, measured)

The `VMProvisionSchema` from Lesson 1.2, handed to `@mcp.tool`, produces this as
`tool.parameters` — generated, never hand-written:

```json
{
  "additionalProperties": false,
  "properties": {
    "spec": {
      "description": "The provisioning request.",
      "properties": {
        "vm_name":   {"description": "Name of the virtual machine", "type": "string"},
        "cpu_cores": {"default": 2, "maximum": 16, "minimum": 1, "type": "integer"},
        "os_type":   {"description": "Operating System",
                      "enum": ["ubuntu", "rocky", "windows"], "type": "string"}
      },
      "required": ["vm_name", "os_type"],
      "type": "object"
    }
  },
  "required": ["spec"],
  "type": "object"
}
```

Note what each source contributed:

| Source | Appears as |
|---|---|
| parameter name | the property key |
| annotation (`int`, `Literal[...]`) | `type` / `enum` |
| `Field(ge=1, le=16)` | `minimum` / `maximum` |
| `Field(default=2)` | `default` |
| `Field(description=...)` | `description` |
| docstring `Args:` | the parameter `description` |

Measured (lab 1, M0), so the claim is not asserted from memory:

```json
"properties": {
  "a": {"type": "number", "description": "The first number."},
  "b": {"type": "number", "description": "The second number."}
}
```

The docstring's `Args:` block reaches the schema with **no** `Field(description=...)` needed.
An omission there is therefore a silent loss of contract, not a cosmetic gap.

## Validation and error behaviour

| Situation | What the client receives |
|---|---|
| `cpu_cores=99` (violates `le=16`) | `ToolError: 1 validation error for call[vm_plan] … Input should be less than or equal to 16 [type=less_than_equal, input_value=99]` |
| a tool RETURNING `{"ok": false, "error": "division_by_zero"}` | `CallToolResult(…, structured_content={...}, is_error=False)` — data, not a failure |
| a tool RAISING `ZeroDivisionError` | `ToolError`, and the model gets an error string with no plan |

That contrast is the whole of Lesson 2.2.

## Resources

- `@mcp.resource("runbook://{service}")` registers a **template**, not a resource.
- `await mcp.list_resources()` → `[]` for a template-only server.
- `await mcp.list_resource_templates()` → objects whose `uri_template` is `runbook://{service}`.
- `await client.read_resource("runbook://postgres")` → a list; take `[0].text`.
- A resource with no content raises clearly (`FileNotFoundError: no runbook for 'nginx';
  available: postgres, redis`) — which is more useful to a model than an empty string.

## CLI, as installed

```text
fastmcp auth · call · dev · discover · generate-cli · inspect · install · list · login ·
         logout · project · run · version · whoami

fastmcp dev apps | inspector        # the Inspector is a subcommand of dev
fastmcp run --reload --module        # auto-reload while developing
```

## Deprecations worth knowing before they become errors

```text
Client(str(path_to_server))
  FastMCPDeprecationWarning: ... is deprecated and will be removed in FastMCP 5.
  Pass pathlib.Path(...) or an explicit StdioTransport instead.
```

Measured: `Client(SERVER)` with a `Path` works and emits nothing.

## A real upstream shape change: MediaWiki `wikitext`

Not a FastMCP issue, but it cost a debug cycle and students will hit it in Lesson 2.2. The
MediaWiki parse API returns `wikitext` as a plain string for small pages and as `{"*": "..."}`
for large ones. Handling only the string shape gives:

```text
TypeError: unhashable type: 'slice'
```

— an error message that says nothing about the cause.

## What was NOT verified

- No LLM was called. Lesson 3.2's LangGraph graph was exercised with a **scripted chooser**, so
  the graph, the MCP wiring and the checkpointer are proven, but model-driven tool selection is
  not. Run it with `--model` and an API key to exercise that path.
- Windows is not Linux for metrics: `system_metrics` returns `null` for `load_average` and
  memory on Windows because `/proc` is absent. The capstone was run on Windows for the check
  above; on the lab's Ubuntu VMs those fields populate.
- Elicitation was verified with an in-process client (`mode="legacy"`). Over stdio or HTTP with
  a real host application it depends on that host implementing the handler.
