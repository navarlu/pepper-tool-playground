# Pepper Tool Playground

Chat with an LLM that can call a **Python tool you write**. Once you're
happy with your tool and system prompt, hand them to Lucas and he'll wire
them into the real Pepper robot.

---

## Setup

Requires Python 3.10+.

```bash
# 1. Clone
git clone <this-repo-url>
cd tool-playground

# 2. Create a virtual environment and install deps
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt

# 3. Set the API key
cp .env.example .env    # Windows: copy .env.example .env
# then open .env and paste the key you got from the link below
```

Get your OpenAI API key here:

> https://privatebin.net/?719ebb35838623d1#3zQjZRZV8nTGrjqg2TS7orY4coP5BuD49ZkARqYvVefq

The password is written on the blackboard. Paste the key into your `.env`
file as `OPENAI_API_KEY=sk-...`.

## Run

```bash
python cli.py
```

You'll see `You>`. Type a message. When the bot decides it needs your
tool, you'll see the tool call and its result printed inline, then the
final answer:

```
You> what's the weather in Prague?
  [tool call]   get_weather({"city":"Prague"})
  [tool result] 18°C, sunny, light wind from the west
Bot> It's 18 degrees and sunny in Prague right now.
```

## Files you edit

- **`system_prompt.py`** — edit the `SYSTEM_PROMPT` string to tell the bot
  who it is and how to behave.
- **`tools.py`** — define one or more tools. Each tool needs:
  - a Python function — the code that runs when the LLM calls the tool;
  - a schema dict — tells the LLM the tool's name, description, and arguments.

  Register every tool in the `TOOLS` list at the bottom of the file. The
  starter file ships with two examples — `get_weather` (takes a city) and
  `get_current_time` (no arguments) — so you can see both shapes.

## Slash commands

While chatting:

| command   | effect                                                        |
|-----------|---------------------------------------------------------------|
| `/reset`  | clear conversation history (keeps your current prompt + tool) |
| `/quit`   | exit                                                          |

After editing `system_prompt.py` or `tools.py`, press `Ctrl-C` and run
`python cli.py` again to reload them.

## What to submit

After class, send Lucas your `system_prompt.py` and `tools.py`.
