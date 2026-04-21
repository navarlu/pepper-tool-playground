"""
Tool Playground CLI
===================

A minimal chat loop that lets an OpenAI model call ONE Python tool
that you defined in `tools.py`. Read this file top to bottom — it's
the whole program.

The flow, per user message:

    1. Add the user's message to the conversation history.
    2. Send the full history + your tool schema to the LLM.
    3. The LLM either:
         (a) replies with plain text  → print it, wait for next input.
         (b) asks to call your tool   → run the Python function, add
                                        the result to the history, go
                                        back to step 2.

That inner repeat is called the "agent loop". It ends as soon as the
model decides it has enough information and writes a plain answer.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# These two imports pull the bits you (the student) are editing.
from system_prompt import SYSTEM_PROMPT
from tools import TOOLS

# Two convenience lookups derived from the TOOLS list in tools.py:
#   SCHEMAS            — what we hand to the LLM so it knows what's available.
#   FUNCTIONS_BY_NAME  — how we find the right Python function when the LLM
#                        says "call the tool named X".
SCHEMAS = [tool["schema"] for tool in TOOLS]
FUNCTIONS_BY_NAME = {
    tool["schema"]["function"]["name"]: tool["function"]
    for tool in TOOLS
}


# ─── Settings ──────────────────────────────────────────────────────────────
MODEL = "gpt-4o-mini"                      # cheap model that supports tools
TEMPERATURE = 0.7                          # 0.0 = deterministic, 1.0 = creative
ROOT = Path(__file__).resolve().parent     # folder this script lives in

# ANSI escape codes — special strings that colour text in the terminal.
# Purely decorative; you can delete them if you don't care.
CYAN = "\033[36m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main() -> None:
    """Entry point — load the key, start the chat loop."""
    # Read the OpenAI key from the .env file next to this script.
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        print("Copy .env.example to .env and paste the key you were given.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # The conversation history is just a list of messages. The first
    # one is the system prompt — it tells the model who it is.
    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"Loaded {len(TOOLS)} tool(s): {', '.join(FUNCTIONS_BY_NAME)}")
    print("Commands: /quit, /reset\n")

    # Main chat loop — one iteration = one user message.
    while True:
        try:
            user = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not user:
            continue
        if user == "/quit":
            return
        if user == "/reset":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("[history cleared]\n")
            continue

        # Record what the user said, then let the agent loop take over.
        history.append({"role": "user", "content": user})
        run_agent_loop(client, history)


def run_agent_loop(client: OpenAI, history: list[dict]) -> None:
    """Keep calling the model until it stops asking for tools.

    Each pass through the loop is one API call to OpenAI. The loop
    exits as soon as the model writes a plain-text answer.
    """
    while True:
        # Ask the model for the next message.
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=history,
            tools=SCHEMAS,   # tell the model what tools exist
        )
        message = response.choices[0].message

        # Add the model's reply to history so it stays in context
        # for the next turn.
        history.append(serialize_assistant_message(message))

        # CASE A — plain answer. Print it and we're done.
        if not message.tool_calls:
            print(f"{BOLD}Bot>{RESET} {message.content}\n")
            return

        # CASE B — the model asked to run your tool (possibly more
        # than once). Execute each call, append the result, and loop
        # again so the model can read the result and decide what to say.
        for call in message.tool_calls:
            result = execute_tool_call(call)
            history.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })


def execute_tool_call(call) -> str:
    """Run the Python function requested by the LLM and return its result as text."""
    # 1. Read what the model asked for.
    name = call.function.name
    args_json = call.function.arguments or "{}"
    print(f"  {CYAN}[tool call]{RESET}   {name}({args_json})")

    # 2. Turn the JSON argument string into a Python dict.
    args = json.loads(args_json)

    # 3. Look up the matching Python function in tools.py and run it.
    python_function = FUNCTIONS_BY_NAME[name]
    try:
        result = python_function(**args)
    except Exception as exc:
        result = f"ERROR: {exc!r}"

    # 4. Print and hand the result back to the agent loop.
    print(f"  {GREEN}[tool result]{RESET} {result}\n")
    return str(result)


def serialize_assistant_message(message) -> dict:
    """Turn the OpenAI response object into a plain dict for the history.

    OpenAI needs every message in the list to be a dict with a `role`
    and either a `content` (plain text) or `tool_calls` (list of
    requested tool invocations).
    """
    entry: dict = {"role": "assistant", "content": message.content}
    if message.tool_calls:
        entry["tool_calls"] = [
            {
                "id": c.id,
                "type": "function",
                "function": {
                    "name": c.function.name,
                    "arguments": c.function.arguments,
                },
            }
            for c in message.tool_calls
        ]
    return entry


if __name__ == "__main__":
    main()
