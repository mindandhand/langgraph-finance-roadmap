from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ReviewState(TypedDict):
    claim: dict
    researcher_claims: list[dict]
    reviewer_findings: list[dict]
    red_team_findings: list[dict]
    decision: str


def researcher(state: ReviewState) -> dict:
    claim = state["claim"]
    return {
        "researcher_claims": [{
            "role": "researcher",
            "statement": f"{claim['factor']} has IC={claim['ic']:.4f}",
            "evidence": {"ic": claim["ic"], "rank_ic": claim["rank_ic"]},
        }]
    }


def reviewer(state: ReviewState) -> dict:
    claim = state["claim"]
    findings = []
    if claim["rows"] < 120:
        findings.append({"severity": "high", "message": "sample is too short"})
    if not claim["backtest_done"]:
        findings.append({"severity": "high", "message": "portfolio backtest is missing"})
    if abs(claim["ic"]) < 0.02:
        findings.append({"severity": "medium", "message": "IC is economically weak"})
    return {"reviewer_findings": findings}


def red_team(state: ReviewState) -> dict:
    claim = state["claim"]
    findings = []
    if not claim["cost_checked"]:
        findings.append({"severity": "high", "message": "cost sensitivity is missing"})
    if claim["factor"].startswith("momentum"):
        findings.append({"severity": "medium", "message": "momentum can be regime-dependent"})
    return {"red_team_findings": findings}


def synthesize(state: ReviewState) -> dict:
    high_findings = [
        *[f for f in state["reviewer_findings"] if f["severity"] == "high"],
        *[f for f in state["red_team_findings"] if f["severity"] == "high"],
    ]
    decision = "requires_more_evidence" if high_findings else "can_continue_to_human_review"
    return {"decision": decision}


builder = StateGraph(ReviewState)
builder.add_node("researcher", researcher)
builder.add_node("reviewer", reviewer)
builder.add_node("red_team", red_team)
builder.add_node("synthesize", synthesize)
builder.add_edge(START, "researcher")
builder.add_edge("researcher", "reviewer")
builder.add_edge("reviewer", "red_team")
builder.add_edge("red_team", "synthesize")
builder.add_edge("synthesize", END)
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "claim": {
            "factor": "momentum_5d",
            "ic": 0.018,
            "rank_ic": 0.021,
            "rows": 80,
            "backtest_done": False,
            "cost_checked": False,
        },
        "researcher_claims": [],
        "reviewer_findings": [],
        "red_team_findings": [],
        "decision": "",
    })
    print("researcher_claims:", result["researcher_claims"])
    print("reviewer_findings:", result["reviewer_findings"])
    print("red_team_findings:", result["red_team_findings"])
    print("decision:", result["decision"])
