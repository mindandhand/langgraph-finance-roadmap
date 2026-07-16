import json
from pathlib import Path
from typing import TypedDict

import pandas as pd
from langgraph.graph import END, START, StateGraph


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "qlib-demos"
    / "qlib-data"
    / "hs300_etf_510300"
    / "csv"
    / "SH510300.csv"
)
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


class ResearchState(TypedDict):
    experiment_id: str
    symbol: str
    start_date: str
    end_date: str
    lookback: int
    label_horizon: int
    factor_ref: str
    metrics: dict[str, float]
    review_decision: str
    backtest_ref: str
    report_ref: str
    trace: list[str]
    status: str


def define_candidate_factor(state: ResearchState) -> dict:
    return {
        "trace": [*state["trace"], "define_candidate_factor"],
        "status": "factor_defined",
    }


def compute_factor(state: ResearchState) -> dict:
    frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
    data = frame[
        (frame["symbol"] == state["symbol"])
        & frame["date"].between(pd.Timestamp(state["start_date"]), pd.Timestamp(state["end_date"]))
    ].sort_values(["symbol", "date"]).copy()
    by_symbol = data.groupby("symbol")
    data["factor"] = data["close"] / by_symbol["close"].shift(state["lookback"]) - 1
    data["label"] = by_symbol["close"].shift(-state["label_horizon"]) / data["close"] - 1
    data = data.dropna(subset=["factor", "label"]).reset_index(drop=True)

    ARTIFACT_DIR.mkdir(exist_ok=True)
    factor_ref = ARTIFACT_DIR / "factor_data.csv"
    data.to_csv(factor_ref, index=False)
    return {
        "factor_ref": str(factor_ref),
        "trace": [*state["trace"], "compute_factor"],
        "status": "factor_computed",
    }


def evaluate_factor(state: ResearchState) -> dict:
    data = pd.read_csv(state["factor_ref"], parse_dates=["date"])
    metrics = {
        "rows": float(len(data)),
        "ic": float(data["factor"].corr(data["label"])),
        "rank_ic": float(data["factor"].corr(data["label"], method="spearman")),
        "factor_mean": float(data["factor"].mean()),
        "label_mean": float(data["label"].mean()),
    }
    return {
        "metrics": metrics,
        "trace": [*state["trace"], "evaluate_factor"],
        "status": "evaluated",
    }


def auto_review(state: ResearchState) -> dict:
    metrics = state["metrics"]
    enough_rows = metrics.get("rows", 0) >= 120
    finite_ic = metrics.get("ic") == metrics.get("ic")
    decision = "approve_backtest" if enough_rows and finite_ic else "reject_backtest"
    return {
        "review_decision": decision,
        "trace": [*state["trace"], f"review:{decision}"],
        "status": "reviewed",
    }


def route_after_review(state: ResearchState) -> str:
    return "run_backtest" if state["review_decision"] == "approve_backtest" else "write_report"


def run_backtest(state: ResearchState) -> dict:
    data = pd.read_csv(state["factor_ref"], parse_dates=["date"])
    picks = data.sort_values(["date", "factor"], ascending=[True, False]).groupby("date").head(1)
    picks = picks.sort_values("date").reset_index(drop=True)
    picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
    picks.loc[0, "turnover"] = 1.0
    picks["net_return"] = picks["label"] - picks["turnover"] * 0.001
    picks["equity"] = (1 + picks["net_return"]).cumprod()

    backtest_ref = ARTIFACT_DIR / "backtest.csv"
    picks.to_csv(backtest_ref, index=False)
    metrics = {
        **state["metrics"],
        "backtest_rows": float(len(picks)),
        "total_net_return": float(picks["equity"].iloc[-1] - 1),
        "avg_turnover": float(picks["turnover"].mean()),
    }
    return {
        "backtest_ref": str(backtest_ref),
        "metrics": metrics,
        "trace": [*state["trace"], "run_backtest"],
        "status": "backtested",
    }


def write_report(state: ResearchState) -> dict:
    trace = [*state["trace"], "write_report"]
    report = {
        "experiment_id": state["experiment_id"],
        "symbol": state["symbol"],
        "candidate_factor": f"{state['lookback']}-day momentum",
        "period": {"start": state["start_date"], "end": state["end_date"]},
        "metrics": state["metrics"],
        "artifact_refs": {
            "factor": state["factor_ref"],
            "backtest": state["backtest_ref"],
        },
        "decision": "requires_human_review_before_real_use",
        "trace": trace,
    }
    report_ref = ARTIFACT_DIR / "report.json"
    report_ref.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {
        "report_ref": str(report_ref),
        "trace": trace,
        "status": "reported",
    }


builder = StateGraph(ResearchState)
builder.add_node("define_candidate_factor", define_candidate_factor)
builder.add_node("compute_factor", compute_factor)
builder.add_node("evaluate_factor", evaluate_factor)
builder.add_node("auto_review", auto_review)
builder.add_node("run_backtest", run_backtest)
builder.add_node("write_report", write_report)
builder.add_edge(START, "define_candidate_factor")
builder.add_edge("define_candidate_factor", "compute_factor")
builder.add_edge("compute_factor", "evaluate_factor")
builder.add_edge("evaluate_factor", "auto_review")
builder.add_conditional_edges("auto_review", route_after_review)
builder.add_edge("run_backtest", "write_report")
builder.add_edge("write_report", END)
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "experiment_id": "agent-e2e-001",
        "symbol": "SH510300",
        "start_date": "2024-01-01",
        "end_date": "2026-07-14",
        "lookback": 5,
        "label_horizon": 1,
        "factor_ref": "",
        "metrics": {},
        "review_decision": "",
        "backtest_ref": "",
        "report_ref": "",
        "trace": [],
        "status": "created",
    })
    print("status:", result["status"])
    print("report_ref:", result["report_ref"])
    print("metrics:", json.dumps(result["metrics"], indent=2))
    print("trace:", " -> ".join(result["trace"]))
