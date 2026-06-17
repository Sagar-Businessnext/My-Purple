"""Memory tools — explicit remember, structured profile, and the people in your life.

Recall happens automatically (the agent injects your profile + relevant facts each turn),
so these are the write side: deliberately remember a fact, set a profile field, or note
a person Purple should know about.
"""

from __future__ import annotations

from purple.memory.extract import normalize_category
from purple.runtime import get_memory
from purple.tools.registry import registry


@registry.tool(
    name="remember",
    description="Store a durable fact about the user to recall in future conversations. "
    "category is one of: preference, person, project, routine, fact.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The fact to remember."},
            "category": {"type": "string", "description": "preference|person|project|routine|fact"},
        },
        "required": ["text"],
    },
)
async def remember(text: str, category: str = "fact") -> str:
    await get_memory().remember(text, kind=normalize_category(category))
    return "Got it — I'll remember that."


@registry.tool(
    name="set_profile",
    description="Set a structured profile field about the user (e.g. key 'name', "
    "'location', 'work', 'comms_style'). Overwrites any existing value for that key.",
    parameters={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Profile field, e.g. name / location / work."},
            "value": {"type": "string", "description": "The value to store."},
        },
        "required": ["key", "value"],
    },
)
async def set_profile(key: str, value: str) -> str:
    await get_memory().set_profile(key.strip().lower().replace(" ", "_"), value.strip())
    return f"Saved {key}."


@registry.tool(
    name="get_profile",
    description="Show what Purple knows about the user (the structured profile).",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def get_profile() -> dict | str:
    profile = await get_memory().get_profile()
    return profile or "I don't have a profile for you yet."


@registry.tool(
    name="remember_person",
    description="Remember a person in the user's life (so Purple knows who 'my boss' or "
    "'Priya' is). relation e.g. boss/spouse/colleague; aliases comma-separated.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The person's name."},
            "relation": {"type": "string", "description": "How they relate to the user."},
            "aliases": {"type": "string", "description": "Other names, comma-separated."},
            "notes": {"type": "string", "description": "Anything else worth noting."},
        },
        "required": ["name"],
    },
)
async def remember_person(name: str, relation: str = "", aliases: str = "", notes: str = "") -> str:
    alias_list = [a.strip() for a in aliases.split(",") if a.strip()]
    await get_memory().add_entity("person", name, relation, alias_list, notes)
    return f"Noted {name}" + (f" ({relation})." if relation else ".")


@registry.tool(
    name="list_people",
    description="List the people Purple knows about in the user's life.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_people() -> list[dict] | str:
    people = await get_memory().list_entities("person")
    return people or "I don't know anyone in your life yet — tell me about them."


@registry.tool(
    name="consolidate_memory",
    description="Tidy long-term memory by merging duplicate facts (keeps the newest wording).",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def consolidate_memory() -> str:
    n = await get_memory().consolidate()
    if not n:
        return "Memory's already tidy — no duplicates found."
    return f"Tidied up — merged {n} duplicate {'memory' if n == 1 else 'memories'}."
