"""
LangGraph demo #5 — streaming instead of waiting for the whole graph.

Every earlier demo called graph.invoke(), which blocks until the graph
reaches END and hands back the final State in one go. graph.stream() runs
the exact same kind of graph but yields pieces as they're produced.

To make that difference actually visible — not just claimed — this demo
reuses demo 3's agent/tools loop (multiple nodes, runs more than once per
call) and prints a timestamp next to every chunk. The timestamps are the
proof: with invoke() you'd see nothing until the entire loop finished; with
stream() you see each step land the moment it's ready.

Two stream_mode values:

  - "updates": one chunk per node, the instant that node finishes. On a
    multi-step graph like this one, you watch the agent decide to call
    tools, then the tools actually run, then the agent read the results —
    as three separate, timestamped events instead of one final blob.

  - "messages": one chunk per LLM token, as the model generates them.
    Notably, the `agent` node below still just calls `model.invoke(...)`
    — nothing about the node changed to support this. graph.stream(...)
    taps into any LLM call happening inside any node and streams its
    tokens out, regardless of how that node is written.

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python stream_graph.py
"""
import time
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


# TOOLS — same shape as demo 3.
@tool
def get_weather(city: str) -> str:
    """Look up the current weather for a city."""
    fake_weather = {"beijing": "Sunny, 25°C", "tokyo": "Cloudy, 20°C"}
    return fake_weather.get(city.lower(), f"No weather data for {city}.")


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


tools = [get_weather, add]
tools_by_name = {t.name: t for t in tools}
model = ChatAnthropic(model="claude-sonnet-5").bind_tools(tools)


def extract_text(content) -> str:
    """content is a plain str for simple replies, but a list of content
    blocks (thinking + text) when extended thinking is on — see demo 2."""
    if isinstance(content, str):
        return content
    return "".join(block.get("text", "") for block in content if block.get("type") == "text")


def text_blocks(content):
    """Same idea as extract_text, but for a single streamed token chunk:
    yields only the 'text' pieces, skipping 'thinking' chunks."""
    if isinstance(content, str):
        if content:
            yield content
        return
    for block in content:
        if block.get("type") == "text":
            yield block.get("text", "")


def summarize(message) -> str:
    """One-line description of a message, for the 'updates' trace."""
    if getattr(message, "tool_calls", None):
        calls = ", ".join(f"{c['name']}({c['args']})" for c in message.tool_calls)
        return f"requests tool call(s): {calls}"
    if isinstance(message, ToolMessage):
        return f"tool result: {message.content}"
    return extract_text(message.content)


# 1. STATE — identical to demo 3.
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# 2. NODES — identical to demo 3's agent/tools loop.
def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def call_tools(state: State) -> dict:
    last_message = state["messages"][-1]
    results = [
        ToolMessage(content=str(tools_by_name[c["name"]].invoke(c["args"])), tool_call_id=c["id"])
        for c in last_message.tool_calls
    ]
    return {"messages": results}


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END


# 3 & 4. GRAPH — identical shape to demo 3.
builder = StateGraph(State)
builder.add_node("agent", agent)
builder.add_node("tools", call_tools)
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()


if __name__ == "__main__":
    question = "What's the weather in Beijing and Tokyo, and what is 23 + 19?"
    inputs = {"messages": [HumanMessage(question)]}

    print("--- stream_mode='updates': one timestamped chunk per finished node ---")
    start = time.monotonic()
    for chunk in graph.stream(inputs, stream_mode="updates"):
        elapsed = time.monotonic() - start
        for node_name, update in chunk.items():
            for message in update["messages"]:
                print(f"[{elapsed:5.2f}s] [{node_name}] {summarize(message)}")

    print("\n--- stream_mode='messages': one timestamped chunk per LLM token ---")
    start = time.monotonic()
    for token, metadata in graph.stream(inputs, stream_mode="messages"):
        for text in text_blocks(token.content):
            elapsed = time.monotonic() - start
            print(f"[{elapsed:5.2f}s] [{metadata['langgraph_node']}] {text!r}")
