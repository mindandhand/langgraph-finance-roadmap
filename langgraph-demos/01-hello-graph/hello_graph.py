"""
Minimal LangGraph demo — no API key needed.

LangGraph's core idea, in 4 pieces:

1. State   — a shared dict (schema) that flows through the graph.
             Every node reads it and returns a partial update to merge in.
2. Node    — a plain function: (state) -> dict of fields to update.
3. Edge    — wiring between nodes. Can be fixed ("always go A -> B")
             or conditional ("go to A or B depending on the state").
4. Graph   — you register nodes + edges on a StateGraph, then `.compile()`
             it into a runnable. Calling `.invoke(state)` walks the graph
             from START to END, threading state through each node.

This demo builds a 3-node graph:

    START -> greet -> check_mood -> (happy_reply | grumpy_reply) -> END

Run it:
    python hello_graph.py
"""
import warnings
from typing import TypedDict

# Cosmetic: langchain_core's pydantic-v1 compat shim warns on Python 3.14+.
# Harmless here — none of these demos touch pydantic v1 functionality.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.utils.pydantic")

from langgraph.graph import StateGraph, START, END


# 1. STATE: the schema shared across every node.
class State(TypedDict):
    name: str
    mood: str
    message: str


# 2. NODES: each one takes the current state and returns the fields it changes.
def greet(state: State) -> dict:
    return {"message": f"Hello, {state['name']}!"}


def happy_reply(state: State) -> dict:
    return {"message": state["message"] + " Great to see you in a good mood."}


def grumpy_reply(state: State) -> dict:
    return {"message": state["message"] + " Hope your mood improves soon."}


# A router doesn't update state — it just returns the name of the next node.
def route_by_mood(state: State) -> str:
    return "happy_reply" if state["mood"] == "happy" else "grumpy_reply"


# 3 & 4. GRAPH: register nodes, wire edges, compile.
builder = StateGraph(State)

builder.add_node("greet", greet)
builder.add_node("happy_reply", happy_reply)
builder.add_node("grumpy_reply", grumpy_reply)

builder.add_edge(START, "greet")                 # fixed edge: entry point -> greet
builder.add_conditional_edges("greet", route_by_mood)  # branch based on state
builder.add_edge("happy_reply", END)              # fixed edge: -> exit point
builder.add_edge("grumpy_reply", END)

graph = builder.compile()


if __name__ == "__main__":
    for mood in ["happy", "grumpy"]:
        result = graph.invoke({"name": "Bird", "mood": mood, "message": "I want fly"})
        print(f"[mood={mood}] {result['message']}")
