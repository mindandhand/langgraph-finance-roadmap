from typing import TypedDict


class ResearchState(TypedDict):
    research_id: str
    objective: str
    instrument: str
    start_date: str
    end_date: str
    candidate_factor: str
    artifact_refs: dict[str, str]
    metrics: dict[str, float]
    status: str


def create_task() -> ResearchState:
    return {
        "research_id": "agent-demo-002",
        "objective": "Evaluate whether short-term momentum has predictive value.",
        "instrument": "SH510300",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "candidate_factor": "close / Ref(close, 5) - 1",
        "artifact_refs": {},
        "metrics": {},
        "status": "created",
    }


def register_price_artifact(state: ResearchState) -> ResearchState:
    state["artifact_refs"]["prices"] = "artifacts/agent-demo-002/prices.csv"
    state["status"] = "data_registered"
    return state


def register_factor_artifact(state: ResearchState) -> ResearchState:
    state["artifact_refs"]["factor"] = "artifacts/agent-demo-002/factor.csv"
    state["status"] = "factor_registered"
    return state


if __name__ == "__main__":
    state = create_task()
    state = register_price_artifact(state)
    state = register_factor_artifact(state)
    for key, value in state.items():
        print(f"{key}: {value}")
