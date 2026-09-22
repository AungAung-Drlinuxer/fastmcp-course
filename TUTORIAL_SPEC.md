# TUTORIAL AUTHORING SPEC — read this completely before writing

## What you are producing and what you are NOT

You are writing a **teaching tutorial** in Burmese for a student who will type the code
themselves. You are NOT setting up their machine, NOT installing anything for them, and NOT
writing a summary. Your output is *prose that teaches*, hundreds of sections long, interleaved
with code the student will type.

A summary is a failure. A bulleted outline is a failure. A "here is the concept, now try it"
paragraph is a failure. Expect to write the equivalent of a book chapter.

## LANGUAGE RULE — read twice, it is strict

- **Explanations, narration, why-it-matters, mistakes, encouragements = BURMESE (Myanmar script).**
- **ALL code, ALL code comments, ALL technical names, ALL commands, ALL tables' technical
  columns = ENGLISH.**
- Mixed inside one sentence is correct and expected:
    `uv run` command သည် `.venv` ကို အလိုအလျောက် ရှာပေးသည်။
- NEVER write a code comment in Burmese. NEVER write a whole paragraph in English. If you are
  unsure, the prose is Burmese and everything inside backticks or a code fence is English.

## FILE LAYOUT — one module = one folder of many files

Write into `D:\fastmcp-course\<MODULE>\tutorial\` as numbered files:

    01-<topic>.md
    02-<topic>.md
    ...
    NN-cheatsheet.md
    NN-labs-answers.md

Each file must be **350-600 lines**. The module's TOTAL across all files must be **at least
5000 lines**. That means roughly 10-14 files. Do not pad with blank lines; pad with CONTENT.
Reach the count by covering more ground, in more depth, with more worked examples — never by
repeating yourself.

## THE STRUCTURE EVERY TOPIC FILE MUST FOLLOW

    # <English topic title>

    ## ဒီဖိုင်မှာ ဘာသင်မလဲ
    <3-6 Burmese bullets>

    ## <concept section in Burmese>
    <explain the concept fully. why it exists. what breaks without it. analogies are welcome.
     Burmese narration around English terms in backticks.>

    ### ဥပမာ — <what this example shows>
    ```python
    # English comment explaining the line above or the block below
    <real, runnable code>
    ```
    <Burmese paragraph walking through the code LINE BY LINE, saying what each part does and
     why it is written that way>

    ### ဘာကြောင့် ဒီလိုရေးရလဲ
    <Burmese: the design reasoning. what the naive version would be and what goes wrong>

    ### မှားလေ့ရှိသည့် အချက်
    <2-5 Burmese bullets, each naming a concrete mistake and its symptom>

    ## LAB <n> — <English lab title>
    **ရည်မှန်းချက်:** <Burmese one line>
    **အချိန်:** <n> မိနစ်
    **ဖိုင်:** `M2_types_pydantic/code/lab_<n>_<name>.py`

    ### အဆင့် ၁ — <Burmese step title>
    <Burmese explanation of why this step>
    ```python
    <the code the student types>
    ```
    ### အဆင့် ၂ — ...
    ...
    ### စစ်ဆေးနည်း
    ```
    uv run python -m <module path>
    ```
    **မျှော်မှန်းရလဒ်:**
    ```text
    <the exact output they should see>
    ```
    ### ဖြစ်နိုင်သည့် အမှား
    <Burmese: symptom then cause then fix — as a 3-column table with technical columns in English>

    ## နိဒါန်း
    <3-6 Burmese bullets recapping what this file taught>

    ## ကိုးကား
    <relative links to the code files this file refers to>

## GROUNDING — the rule that keeps this honest

Read the module's existing code files first and TEACH FROM THEM. If you show code, it must be
either (a) copied from the repo, or (b) a new lab file the student writes, and in that case you
must ALSO write that lab file to disk at the path you name. Never invent a FastMCP API. The
verified API facts for this project are in `D:\fastmcp-course\VERIFIED.md` — read it, and if
you need a behaviour it does not cover, say so in your report instead of guessing.

## TONE

Teach a competent adult who has written some Python but has never built an MCP server. Be
concrete. Name the failure before naming the fix. Where a student would reasonably ask "why not
just do it the simple way", answer that question in Burmese in the text.

## REPORT

Report only: files written (paths + line counts), the module total, lab code files you created,
and any API behaviour you could not verify.
