# Python & FastMCP for AI Agents

A hands-on course for developers who already know some Python and want to build **real MCP
servers** — with tools, resources, prompts, interactive elicitation, an orchestrated client,
and the security discipline to run it in production.

Three weeks full-time, or six days as a compressed workshop.

## What makes this course different

Every example in this repository has been **executed against the pinned FastMCP version** and
its real output is recorded in [`VERIFIED.md`](VERIFIED.md). That matters more than usual here,
because FastMCP's API changed between major versions in ways that silently break student code:

| The outline that circulated said | What actually exists in FastMCP 4.0.5 |
|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` |
| `tool.inputSchema` | `tool.parameters` |
| `template.uriTemplate` | `template.uri_template` |
| `await mcp.get_tools()` | `await mcp.list_tools()` |

A student who follows a 2.x tutorial cannot tell "I made a mistake" from "the API moved". This
course removes that ambiguity by pinning the version and showing real output.

## Structure

| Module | Lesson | Hours |
|---|---|---|
| [M0](M0_orientation/) | Orientation, lab environment, how an MCP server is judged | 1.5 |
| [M1](M1_python_env/) | Modern Python environment with `uv` and WSL | 2 |
| [M2](M2_types_pydantic/) | Type hints, introspection, Pydantic validation | 3 |
| [M3](M3_asyncio_decorators/) | asyncio and decorators | 2.5 |
| [M4](M4_fastmcp_basics/) | Server initialization and transports | 2 |
| [M5](M5_tools/) | Action-oriented tools (`@mcp.tool`) | 3 |
| [M6](M6_resources/) | Read-only data resources (`@mcp.resource`) | 2.5 |
| [M7](M7_prompts/) | Workflow steering prompts (`@mcp.prompt`) | 2 |
| [M8](M8_elicitation/) | Interactive elicitation (`await ctx.elicit()`) | 3 |
| [M9](M9_clients/) | Host and client orchestration (Cline, LangGraph) | 3.5 |
| [M10](M10_security/) | Production security and hardening | 2.5 |
| [M11](M11_capstone/) | Capstone: Enterprise DevOps / Knowledge Assistant | 6 |

Total: **33 hours** plus the capstone.

### Per-module layout

Every module now follows one consistent shape:

| File | What it is |
|---|---|
| `README.md` | Module overview: what you will learn, lesson list, prerequisites, when it matters |
| `explanation.md` | The lesson, condensed. Each topic follows the same five steps: what it means → why it matters → how it works → worked example → why it matters in practice |
| `exercise.md` | Six hands-on exercises (easy → hard). Each one carries a **Hints** line and an **Expected behavior** line |
| `solution.md` | One worked answer per exercise — headings match the exercise headings one-to-one (runnable code, English comments) plus a one-line key-idea summary. Supplementary worked answers, where a module has extra labs, sit under an `အပိုဆောင်း` heading at the end |
| `cheatsheet.md` | Quick reference card for the module |
| `code/` | The runnable labs referenced by the exercises |
| `../tests/` | The pytest suite that pins the measured behaviour recorded in `VERIFIED.md` |

Recommended loop: read `explanation.md` → do `exercise.md` → check against `solution.md` → run the matching `code/lab_*.py` → keep `cheatsheet.md` open while you build.

### Three-week schedule

| Week | Days | Modules | Milestone |
|---|---|---|---|
| 1 | Mon-Fri | M0, M1, M2, M3 | A `uv` project that validates input with Pydantic and turns a type hint into JSON Schema |
| 2 | Mon-Fri | M4, M5, M6, M7 | A working server with tools, a URI-templated resource and a prompt, driven from the Inspector |
| 3 | Mon-Tue | M8, M9 | An elicitation flow and your own orchestrating client |
| 3 | Wed-Fri | M10, M11 | Hardened, containerized, demonstrated to the group |

### Six-day compressed schedule

| Day | Content |
|---|---|
| 1 | M0 + M1 + M2 (env, type hints, Pydantic) |
| 2 | M3 + M4 (asyncio, decorators, transports) |
| 3 | M5 + M6 (tools, resources) |
| 4 | M7 + M8 (prompts, elicitation) |
| 5 | M9 + M10 (client orchestration, security) |
| 6 | M11 capstone, presented |

## Prerequisites

| | Requirement |
|---|---|
| Audience | Developers and engineers with basic Python who want to build AI tools and agents |
| OS | Ubuntu Linux, WSL2 on Windows 10/11, or macOS |
| Editor | VS Code with the **Cline** and **WSL** extensions |
| Runtime | Python 3.11+ (3.10 works but the examples use `X \| Y` unions) |
| Package manager | `uv` |
| Libraries | `fastmcp`, `pydantic`, `langgraph`, `langchain-openai`, `langchain-mcp-adapters` |

## Running the examples

```bash
uv sync                       # create the environment from the pinned lockfile
uv run python -m M2_types_pydantic.code.schema_demo
uv run pytest -q              # every lesson example is exercised by the suite
```

The lab environment the course is delivered on (VS Code / Jupyter in a browser, one per
student, ephemeral) is described in the platform repository — every module assumes only that
you have a terminal with `uv` on it, so the material runs on a laptop too.
