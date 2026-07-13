"""
LangGraph demo #2 — a graph with real LLM calls.

Same 4 concepts as demo #1 (State / Node / Edge / Graph), except now two of
the nodes call Claude instead of just formatting strings. The routing
decision (add_conditional_edges) is now driven by what the LLM said, not by
a hardcoded field.

    START -> classify_sentiment -> (positive_reply | negative_reply) -> END

Requires:
    pip install langgraph langchain-anthropic python-dotenv
    ../.env with ANTHROPIC_API_KEY (and optionally ANTHROPIC_BASE_URL) set

Run it:
    python llm_graph.py
"""
import warnings
from pathlib import Path
from typing import TypedDict

# Cosmetic: langchain_core's pydantic-v1 compat shim warns on Python 3.14+.
# Harmless here — none of these demos touch pydantic v1 functionality.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.utils.pydantic")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

model = ChatAnthropic(model="claude-sonnet-5")


def extract_text(content) -> str:
    """response.content is a plain str for simple replies, but a list of
    content blocks (e.g. thinking + text) when extended thinking is on."""
    if isinstance(content, str):
        return content
    return "".join(block["text"] for block in content if block.get("type") == "text")


# 1. STATE
class State(TypedDict):
    user_input: str
    sentiment: str
    reply: str


# 2. NODES
def classify_sentiment(state: State) -> dict:
    """LLM call #1 — classify the user's message. Just returns a label,
    which the router below reads to decide which node runs next."""
    prompt = (
        "Classify the sentiment of this message as exactly one word, "
        f"either 'positive' or 'negative':\n\n{state['user_input']}"
    )
    response = model.invoke(prompt)
    sentiment = extract_text(response.content).strip().lower()
    return {"sentiment": sentiment}


def positive_reply(state: State) -> dict:
    """LLM call #2a — only runs when classify_sentiment routed here."""
    prompt = f"Reply enthusiastically to: {state['user_input']}"
    response = model.invoke(prompt)
    return {"reply": extract_text(response.content)}


def negative_reply(state: State) -> dict:
    """LLM call #2b — only runs when classify_sentiment routed here."""
    prompt = f"Reply with empathy and support to: {state['user_input']}"
    response = model.invoke(prompt)
    return {"reply": extract_text(response.content)}


def route_by_sentiment(state: State) -> str:
    return "positive_reply" if state["sentiment"] == "positive" else "negative_reply"


# 3 & 4. GRAPH
builder = StateGraph(State)

builder.add_node("classify_sentiment", classify_sentiment)
builder.add_node("positive_reply", positive_reply)
builder.add_node("negative_reply", negative_reply)

builder.add_edge(START, "classify_sentiment")
builder.add_conditional_edges("classify_sentiment", route_by_sentiment)
builder.add_edge("positive_reply", END)
builder.add_edge("negative_reply", END)

graph = builder.compile()


if __name__ == "__main__":
    for text in ["I just got promoted!", "My cat ran away yesterday."]:
        result = graph.invoke({"user_input": text, "sentiment": "", "reply": ""})
        print(f"[input] {text}")
        print(f"[sentiment] {result['sentiment']}")
        print(f"[reply] {result['reply']}\n")
