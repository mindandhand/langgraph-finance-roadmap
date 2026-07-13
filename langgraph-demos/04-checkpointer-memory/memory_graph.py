"""
LangGraph demo #4 — multi-turn memory via a checkpointer.

Demos 1-3 all called graph.invoke() once and were done. This demo calls it
several times against the *same graph object* and shows that the LLM
remembers earlier turns — without us ever passing the full message history
back in ourselves.

The graph itself is deliberately the simplest possible chat loop:

    START -> chatbot -> END

Nothing new there. What's new is a single argument to .compile():

    graph = builder.compile(checkpointer=InMemorySaver())

and a `thread_id` passed alongside every invoke():

    graph.invoke({"messages": [...]}, {"configurable": {"thread_id": "abc"}})

The checkpointer saves the State after every step, keyed by thread_id. Next
time you invoke() with the same thread_id, LangGraph loads that saved State
first and merges your new input into it — that's the entire mechanism
behind "memory" here. A different thread_id starts from empty State again.

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python memory_graph.py
"""
import warnings
from pathlib import Path
from typing import Annotated, TypedDict

# Cosmetic: langchain_core's pydantic-v1 compat shim warns on Python 3.14+.
# Harmless here — none of these demos touch pydantic v1 functionality.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.utils.pydantic")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

model = ChatAnthropic(model="claude-sonnet-5")


# 1. STATE — same add_messages reducer as demo 3: new messages get
# appended to the history instead of replacing it.
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# 2. NODE
def chatbot(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# 3 & 4. GRAPH — the only difference from demo 1's shape is the
# checkpointer argument to compile().
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    thread_a = {"configurable": {"thread_id": "conversation-a"}}

    result = graph.invoke({"messages": [HumanMessage("My name is Neil.")]}, thread_a)
    result["messages"][-1].pretty_print()

    # Same thread_id, brand new invoke() call, and we only send the new
    # question — no need to resend "My name is Neil." ourselves.
    result = graph.invoke({"messages": [HumanMessage("What's my name?")]}, thread_a)
    result["messages"][-1].pretty_print()

    # A different thread_id has never seen this conversation.
    thread_b = {"configurable": {"thread_id": "conversation-b"}}
    result = graph.invoke({"messages": [HumanMessage("What's my name?")]}, thread_b)
    result["messages"][-1].pretty_print()
