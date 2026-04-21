"""Your tools live here.

Each tool has two parts:

  1. A Python function — the code that runs when the LLM calls the tool.
  2. A schema dict — tells the LLM the tool's name, description, and
     what arguments it takes.

Every tool is registered at the bottom of this file in the `TOOLS`
list. To add a new tool:

  a. Write the Python function.
  b. Write its schema (must match the function's arguments).
  c. Append `{"schema": ..., "function": ...}` to `TOOLS`.

The two examples below — get_weather and get_current_time — show both
the "takes an argument" and "no arguments" cases.
"""

from __future__ import annotations

from datetime import datetime


# ─── Tool 1: get_weather ─────────────────────────────────────────────────

def get_weather(city: str) -> str:
    """Pretend to fetch the weather. Swap in a real API call if you like."""
    #print("Hello from get_weather! This is a side effect to show that the tool ran.")
    fake_db = {
        "prague": "18°C, sunny, light wind from the west",
        "tokyo": "23°C, humid, scattered clouds",
        "reykjavik": "4°C, overcast, chance of rain",
    }
    return fake_db.get(
        city.lower(),
        f"No data for {city}. Try Prague, Tokyo, or Reykjavik.",
    )


GET_WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the current weather for a given city. "
            "Use whenever the user asks about weather, temperature, "
            "or what it's like outside in a specific place."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Prague' or 'Tokyo'.",
                },
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
}


# ─── Tool 2: get_current_time ────────────────────────────────────────────

def get_current_time() -> str:
    """Return the current local time of the machine running the CLI."""
    #print("Hello from get_current_time! This is a side effect to show that the tool ran.")
    return datetime.now().strftime("%H:%M on %A, %B %d, %Y")


GET_CURRENT_TIME_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": (
            "Get the current local time and date. Use whenever the "
            "user asks what time it is or what today's date is."
        ),
        "parameters": {
            # A tool with no arguments still needs this block; it just
            # has an empty `properties` map.
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}


# ─── Registry ────────────────────────────────────────────────────────────
# The CLI reads this list. Every entry must have a `schema` and a
# `function`. The function's arguments must match the schema's properties.

TOOLS = [
    {"schema": GET_WEATHER_SCHEMA,      "function": get_weather},
    {"schema": GET_CURRENT_TIME_SCHEMA, "function": get_current_time},
]
