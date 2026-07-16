from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ReviewState(TypedDict):
    factor: str
    period: str
    max_backtests_used: str
    decision: str
    status: str


def prepare_request(state: ReviewState) -> dict:
    return {"status": "review_required"}


def human_review(state: ReviewState) -> dict:
    decision = interrupt({
        "factor": state["factor"],
        "period": state["period"],
        "max_backtests_used": state["max_backtests_used"],
        "question": "Approve backtest?",
    })
    return {"decision": decision}


def route_after_review(state: ReviewState) -> str:
    return "approve_backtest" if state["decision"] == "approve" else "reject_backtest"


def approve_backtest(state: ReviewState) -> dict:
    return {"status": "approved_for_backtest"}


def reject_backtest(state: ReviewState) -> dict:
    return {"status": "rejected_by_human"}


builder = StateGraph(ReviewState)
builder.add_node("prepare_request", prepare_request)
builder.add_node("human_review", human_review)
builder.add_node("approve_backtest", approve_backtest)
builder.add_node("reject_backtest", reject_backtest)
builder.add_edge(START, "prepare_request")
builder.add_edge("prepare_request", "human_review")
builder.add_conditional_edges("human_review", route_after_review)
builder.add_edge("approve_backtest", END)
builder.add_edge("reject_backtest", END)

graph = builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    initial_state: ReviewState = {
        "factor": "momentum_5d",
        "period": "2024-01-01 to 2024-03-31",
        "max_backtests_used": "0 / 1",
        "decision": "",
        "status": "created",
    }
    config = {"configurable": {"thread_id": "review-demo-001"}}

    result = graph.invoke(initial_state, config)
    pending = result["__interrupt__"][0].value
    print("interrupt_payload:", pending)

    final = graph.invoke(Command(resume="approve"), config)
    print("final_status:", final["status"])
