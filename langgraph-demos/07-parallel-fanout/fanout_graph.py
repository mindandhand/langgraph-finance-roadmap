"""
LangGraph demo #7 — dynamic parallel fan-out with Send.

Every earlier demo's graph shape was fixed at compile time: you know in
advance which nodes exist and how they connect. This demo's graph doesn't
know how many times "research_city" will run until it actually executes —
that count comes from the length of a list in the input. And unlike demo
3's tool-calling loop (which runs multiple tool calls one after another in
a Python for-loop), the parallel branches created here genuinely run
*concurrently*, so three slow LLM calls take roughly as long as one.

    START -> dispatch -> research_city (city=Paris)  -\\
                       -> research_city (city=Tokyo)  --> END
                       -> research_city (city=Cairo)  -/

`dispatch` doesn't return a fixed next-node name like the routers in demos
1-6 — it returns a *list* of Send objects, one per city, each carrying its
own separate input. LangGraph runs all of them in the same step and merges
their results back into the shared `facts` list via a reducer, the same
mechanism as demo 3/4's `add_messages` (there: append messages; here:
concatenate lists — `operator.add` on two lists is just `list1 + list2`).

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python fanout_graph.py
"""
import operator
import time
import warnings
from pathlib import Path
from typing import Annotated, TypedDict

# Cosmetic: langchain_core's pydantic-v1 compat shim warns on Python 3.14+.
# Harmless here — none of these demos touch pydantic v1 functionality.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.utils.pydantic")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

model = ChatAnthropic(model="claude-sonnet-5")


def extract_text(content) -> str:
    """content is a plain str for simple replies, but a list of content
    blocks (thinking + text) when extended thinking is on — see demo 2."""
    if isinstance(content, str):
        return content
    return "".join(block.get("text", "") for block in content if block.get("type") == "text")


# 1. STATE — two schemas here, on purpose.
#
# OverallState is what the graph as a whole takes as input and returns.
# `facts` uses operator.add as its reducer: instead of overwriting the
# list, each parallel branch's result gets concatenated onto it — the
# list-equivalent of demo 3/4's add_messages.
class OverallState(TypedDict):
    cities: list[str]
    facts: Annotated[list[str], operator.add]


# CityState is what each individual parallel branch receives — just the
# one city it's responsible for, not the whole OverallState.
class CityState(TypedDict):
    city: str


# 2. NODES
def dispatch(state: OverallState) -> list[Send]:
    """Not a router in the demo 1-6 sense — instead of one next-node name,
    this returns one Send per city, each an independent parallel branch."""
    return [Send("research_city", {"city": city}) for city in state["cities"]]


def research_city(state: CityState) -> dict:
    prompt = f"Tell me one interesting fact about {state['city']} in one short sentence."
    response = model.invoke(prompt)
    return {"facts": [f"{state['city']}: {extract_text(response.content)}"]}


# 3 & 4. GRAPH — dispatch is wired as a conditional edge straight off
# START, since which "research_city" branches exist isn't known until
# dispatch runs.
builder = StateGraph(OverallState)
builder.add_node("research_city", research_city)
builder.add_conditional_edges(START, dispatch, ["research_city"])
builder.add_edge("research_city", END)

graph = builder.compile()


if __name__ == "__main__":
    cities = ["Paris", "Tokyo", "Cairo"]

    print("--- sequential baseline: one model.invoke() at a time ---")
    start = time.monotonic()
    for city in cities:
        prompt = f"Tell me one interesting fact about {city} in one short sentence."
        response = model.invoke(prompt)
        elapsed = time.monotonic() - start
        print(f"[{elapsed:5.2f}s] {city}: {extract_text(response.content)}")
    sequential_total = time.monotonic() - start

    print("\n--- parallel fan-out: all three research_city branches at once ---")
    start = time.monotonic()
    for chunk in graph.stream({"cities": cities, "facts": []}, stream_mode="updates"):
        elapsed = time.monotonic() - start
        for node_name, update in chunk.items():
            print(f"[{elapsed:5.2f}s] {update['facts'][0]}")
    parallel_total = time.monotonic() - start

    print(f"\nsequential total: {sequential_total:.2f}s | parallel total: {parallel_total:.2f}s")
