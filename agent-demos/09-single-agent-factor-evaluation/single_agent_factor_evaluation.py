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


class FactorState(TypedDict):
    symbol: str
    start_date: str
    end_date: str
    lookback: int
    label_horizon: int
    factor_ref: str
    metrics: dict[str, float]
    report: str
    status: str


def load_and_compute_factor(state: FactorState) -> dict:
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
    return {"factor_ref": str(factor_ref), "status": "factor_computed"}


def evaluate_factor(state: FactorState) -> dict:
    data = pd.read_csv(state["factor_ref"], parse_dates=["date"])
    if data.empty:
        return {"metrics": {"rows": 0}, "status": "insufficient_data"}

    # One ETF has no daily cross-section, so evaluate time-series IC between
    # factor values and next-period returns.
    metrics = {
        "rows": float(len(data)),
        "ic": float(data["factor"].corr(data["label"])),
        "rank_ic": float(data["factor"].corr(data["label"], method="spearman")),
        "factor_mean": float(data["factor"].mean()),
        "label_mean": float(data["label"].mean()),
    }
    return {"metrics": metrics, "status": "evaluated"}


def write_report(state: FactorState) -> dict:
    metrics = state["metrics"]
    report = (
        f"Agent report for {state['symbol']}\n"
        f"- factor: {state['lookback']}-day momentum\n"
        f"- rows: {metrics.get('rows', 0):.0f}\n"
        f"- IC: {metrics.get('ic', float('nan')):.4f}\n"
        f"- RankIC: {metrics.get('rank_ic', float('nan')):.4f}\n"
        "- conclusion: tool-computed evidence only; not an investment claim"
    )
    return {"report": report, "status": "reported"}


builder = StateGraph(FactorState)
builder.add_node("load_and_compute_factor", load_and_compute_factor)
builder.add_node("evaluate_factor", evaluate_factor)
builder.add_node("write_report", write_report)
builder.add_edge(START, "load_and_compute_factor")
builder.add_edge("load_and_compute_factor", "evaluate_factor")
builder.add_edge("evaluate_factor", "write_report")
builder.add_edge("write_report", END)
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "symbol": "SH510300",
        "start_date": "2024-01-01",
        "end_date": "2026-07-14",
        "lookback": 5,
        "label_horizon": 1,
        "factor_ref": "",
        "metrics": {},
        "report": "",
        "status": "created",
    })
    print(result["report"])
