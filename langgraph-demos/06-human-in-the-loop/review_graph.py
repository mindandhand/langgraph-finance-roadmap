"""
LangGraph demo #6 — pausing the graph for human approval.

Builds on two ideas from earlier demos:
  - demo 3's agent/tools loop (an LLM deciding whether to call a tool)
  - demo 4's checkpointer (State that survives across separate invoke() calls)

Human-in-the-loop needs both: the graph has to *actually stop* mid-run and
hand control back to your code, and then pick up again later exactly where
it left off. That "later" might be seconds or days away, which is only
possible because the checkpointer already saved the State.

    START -> agent -> should_continue -> human_review -> route_after_review -> tools        -> agent -> ...
                                                                             -> reject_tools -> agent -> ...
                    \\_______________________________________________________________________________/
                                                          -> END (once no more tool_calls)

New primitive: `interrupt(payload)`. Calling it inside a node freezes the
graph right there — graph.invoke() returns immediately with the payload
attached under the "__interrupt__" key instead of running to completion.
To continue, you call graph.invoke(Command(resume=value), config) with the
*same* thread_id — value becomes interrupt()'s return value, and the node
picks up from where interrupt() was called.

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it (it will pause and ask you to type approve/reject in the terminal):
    python review_graph.py
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
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# TOOLS — a "sensitive" action: a real side effect, worth a human okaying
# it first. (This mock just prints instead of actually sending mail.)
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}."


tools = [send_email]
tools_by_name = {t.name: t for t in tools}
model = ChatAnthropic(model="claude-sonnet-5").bind_tools(tools)


# 1. STATE — same messages field as demo 3/4, plus the human's decision
# for the tool call currently under review.
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    decision: str


# 2. NODES
def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    return "human_review" if last_message.tool_calls else END


def human_review(state: State) -> dict:
    """Freezes the graph and hands the pending tool calls to whoever is
    running it. Resumes with whatever value Command(resume=...) supplied."""
    last_message = state["messages"][-1]
    pending = [{"name": c["name"], "args": c["args"]} for c in last_message.tool_calls]
    decision = interrupt({"pending_tool_calls": pending})
    return {"decision": decision}


def route_after_review(state: State) -> str:
    return "tools" if state["decision"] == "approve" else "reject_tools"


def call_tools(state: State) -> dict:
    last_message = state["messages"][-1]
    results = [
        ToolMessage(content=str(tools_by_name[c["name"]].invoke(c["args"])), tool_call_id=c["id"])
        for c in last_message.tool_calls
    ]
    return {"messages": results}


def reject_tools(state: State) -> dict:
    """Every tool_use block needs a matching tool_result, even a rejected
    one — otherwise the next agent turn sends a malformed message list."""
    last_message = state["messages"][-1]
    results = [
        ToolMessage(content="User rejected this action.", tool_call_id=c["id"])
        for c in last_message.tool_calls
    ]
    return {"messages": results}


# 3 & 4. GRAPH
builder = StateGraph(State)

builder.add_node("agent", agent)
builder.add_node("human_review", human_review)
builder.add_node("tools", call_tools)
builder.add_node("reject_tools", reject_tools)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_conditional_edges("human_review", route_after_review)
builder.add_edge("tools", "agent")
builder.add_edge("reject_tools", "agent")

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "review-demo"}}
    question = "Send an email to boss@example.com telling them I'll be 10 minutes late."
    result = graph.invoke({"messages": [HumanMessage(question)]}, config)

    # A single request can need more than one round of review — e.g. if
    # rejected, the agent may retry with a different approach.
    while "__interrupt__" in result:
        pending = result["__interrupt__"][0].value["pending_tool_calls"]
        print(f"\nThe agent wants to run: {pending}")
        answer = input("Approve? (yes/no): ").strip().lower()
        decision = "approve" if answer in ("y", "yes") else "reject"
        result = graph.invoke(Command(resume=decision), config)

    result["messages"][-1].pretty_print()
