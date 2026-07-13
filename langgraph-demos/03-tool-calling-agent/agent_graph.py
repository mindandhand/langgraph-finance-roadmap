"""
LangGraph demo #3 — a tool-calling agent with a loop.

Demos 1 and 2 were both DAGs: data flows one direction, no node runs twice.
This demo introduces the piece that makes LangGraph worth using over a plain
chain: an edge that points *backwards*, so the graph can loop until the LLM
decides it's done.

    START -> agent -> should_continue -> tools -> agent -> ... -> END
                    \\_____________________________________/
                                 (back to END once the LLM
                                  stops requesting tools)

Each turn through the loop:
  1. `agent` sends the conversation so far to the LLM, with tools bound.
  2. If the LLM's reply contains tool_calls, `should_continue` routes to
     `tools`, which executes them and appends the results as ToolMessages.
  3. `tools` always routes back to `agent`, so the LLM sees the tool
     results and decides what to do next — answer, or call another tool.
  4. Once the LLM replies with no tool_calls, `should_continue` routes to
     END instead of `tools`, and the loop stops.

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python agent_graph.py
"""
import warnings
from pathlib import Path
from typing import Annotated, TypedDict

# Cosmetic: langchain_core's pydantic-v1 compat shim warns on Python 3.14+.
# Harmless here — none of these demos touch pydantic v1 functionality.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.utils.pydantic")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# TOOLS — plain Python functions the LLM can choose to call.
@tool
def get_weather(city: str) -> str:
    """Look up the current weather for a city."""
    fake_weather = {
        "beijing": "Sunny, 25°C",
        "tokyo": "Cloudy, 20°C",
        "paris": "Rainy, 15°C",
    }
    return fake_weather.get(city.lower(), f"No weather data for {city}.")


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


tools = [get_weather, add]
tools_by_name = {t.name: t for t in tools}
model = ChatAnthropic(model="claude-sonnet-5").bind_tools(tools)


# 1. STATE — `add_messages` is a reducer: instead of overwriting the
# messages list on every update, it appends to it. Without this, each
# node's return value would replace the whole conversation history.
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# 2. NODES
def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def call_tools(state: State) -> dict:
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        output = tools_by_name[call["name"]].invoke(call["args"])
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END


# 3 & 4. GRAPH — the add_edge("tools", "agent") is what creates the loop.
builder = StateGraph(State)

builder.add_node("agent", agent)
builder.add_node("tools", call_tools)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()


if __name__ == "__main__":
    question = "What's the weather in Beijing, and what is 23 + 19?"
    result = graph.invoke({"messages": [HumanMessage(question)]})
    for message in result["messages"]:
        message.pretty_print()
