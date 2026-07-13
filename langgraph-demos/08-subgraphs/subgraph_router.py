"""
LangGraph demo #8 — a compiled graph used as a node in a bigger graph.

Every earlier demo built one graph, compiled it once, and ran it. This demo
builds two small, complete agents — each is exactly demo 3's agent/tools
loop, just with a single tool each — and then nests both of them as nodes
inside a third, bigger graph that decides which one to hand a question to.

    weather_agent (its own agent/tools loop, tool = get_weather)
    math_agent    (its own agent/tools loop, tool = add)

    parent graph:
    START -> classify -> route -> weather_agent -> END
                                -> math_agent    -> END

`classify` is the same pattern as demo 2's classify_sentiment: one LLM call
that labels the request, then a plain router function reads the label.
What's new is what `route` routes *to* — "weather_agent" and "math_agent"
aren't node functions we wrote inline, they're .compile()'d graphs, added
to the parent with builder.add_node("weather_agent", weather_agent) — no
different from adding any other node.

This only works directly because both sub-agents and the parent graph
share the same shape for the field they all touch:
    messages: Annotated[list[BaseMessage], add_messages]
LangGraph merges a subgraph's output into the parent's State by matching
key names and reducers. If a subgraph's state didn't share a key with the
parent, you'd wrap it in a small translator node instead of adding it
directly — see the README for that case.

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python subgraph_router.py
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

model = ChatAnthropic(model="claude-sonnet-5")


def extract_text(content) -> str:
    """content is a plain str for simple replies, but a list of content
    blocks (thinking + text) when extended thinking is on — see demo 2."""
    if isinstance(content, str):
        return content
    return "".join(block.get("text", "") for block in content if block.get("type") == "text")


# TOOLS — one per specialist agent.
@tool
def get_weather(city: str) -> str:
    """Look up the current weather for a city."""
    fake_weather = {"beijing": "Sunny, 25°C", "tokyo": "Cloudy, 20°C"}
    return fake_weather.get(city.lower(), f"No weather data for {city}.")


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


# SUBGRAPHS — each one is demo 3's agent/tools loop, parameterized by
# which tool it gets. Every subgraph uses this same State shape.
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def make_agent(tools: list):
    tools_by_name = {t.name: t for t in tools}
    bound_model = model.bind_tools(tools)

    def agent(state: AgentState) -> dict:
        return {"messages": [bound_model.invoke(state["messages"])]}

    def call_tools(state: AgentState) -> dict:
        last_message = state["messages"][-1]
        results = [
            ToolMessage(content=str(tools_by_name[c["name"]].invoke(c["args"])), tool_call_id=c["id"])
            for c in last_message.tool_calls
        ]
        return {"messages": results}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        return "tools" if last_message.tool_calls else END

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent)
    builder.add_node("tools", call_tools)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_edge("tools", "agent")
    return builder.compile()


weather_agent = make_agent([get_weather])
math_agent = make_agent([add])


# PARENT GRAPH — routes to one of the two compiled subgraphs above.
class ParentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str


def classify(state: ParentState) -> dict:
    last_message = state["messages"][-1]
    prompt = (
        "Classify this request as exactly one word, either 'weather' or 'math':\n\n"
        f"{last_message.content}"
    )
    response = model.invoke(prompt)
    return {"topic": extract_text(response.content).strip().lower()}


def route(state: ParentState) -> str:
    return "weather_agent" if state["topic"] == "weather" else "math_agent"


parent_builder = StateGraph(ParentState)
parent_builder.add_node("classify", classify)
parent_builder.add_node("weather_agent", weather_agent)  # <- a compiled graph, used as a node
parent_builder.add_node("math_agent", math_agent)         # <- same here
parent_builder.add_edge(START, "classify")
parent_builder.add_conditional_edges("classify", route, ["weather_agent", "math_agent"])
parent_builder.add_edge("weather_agent", END)
parent_builder.add_edge("math_agent", END)

graph = parent_builder.compile()


if __name__ == "__main__":
    for question in ["What is the weather in Tokyo?", "What is 17 plus 25?"]:
        result = graph.invoke({"messages": [HumanMessage(question)], "topic": ""})
        print(f"[question] {question}")
        print(f"[routed to] {result['topic']}_agent")
        print(f"[answer] {extract_text(result['messages'][-1].content)}\n")
