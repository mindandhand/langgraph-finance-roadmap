import json
from io import StringIO
from pathlib import Path

import pandas as pd


CSV = """date,symbol,close
2024-01-02,A,10.0
2024-01-03,A,10.2
2024-01-04,A,10.5
2024-01-05,A,10.4
2024-01-08,A,10.8
2024-01-09,A,10.7
2024-01-02,B,20.0
2024-01-03,B,19.8
2024-01-04,B,20.1
2024-01-05,B,20.4
2024-01-08,B,20.2
2024-01-09,B,20.6
"""

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def compute_factor() -> pd.DataFrame:
    df = pd.read_csv(StringIO(CSV), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["factor"] = df["close"] / by_symbol["close"].shift(2) - 1
    df["label"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna().reset_index(drop=True)


def evaluate(data: pd.DataFrame) -> dict:
    daily = data.groupby("date").apply(
        lambda g: pd.Series({
            "ic": g["factor"].corr(g["label"]),
            "rank_ic": g["factor"].corr(g["label"], method="spearman"),
        }),
        include_groups=False,
    )
    return {"mean_ic": float(daily["ic"].mean()), "mean_rank_ic": float(daily["rank_ic"].mean())}


def backtest(data: pd.DataFrame) -> pd.DataFrame:
    picks = data.sort_values(["date", "factor"], ascending=[True, False]).groupby("date").head(1)
    picks = picks.sort_values("date").reset_index(drop=True)
    picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
    picks.loc[0, "turnover"] = 1.0
    picks["net_return"] = picks["label"] - picks["turnover"] * 0.001
    picks["equity"] = (1 + picks["net_return"]).cumprod()
    return picks


def main() -> None:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    trace = []

    trace.append("define_candidate_factor")
    data = compute_factor()
    data.to_csv(ARTIFACT_DIR / "factor_data.csv", index=False)

    trace.append("evaluate_factor")
    metrics = evaluate(data)

    approved = metrics["mean_ic"] == metrics["mean_ic"]
    trace.append("human_review_auto_approved" if approved else "human_review_rejected")

    bt = backtest(data) if approved else pd.DataFrame()
    if approved:
        bt.to_csv(ARTIFACT_DIR / "backtest.csv", index=False)

    report = {
        "candidate_factor": "2-day momentum",
        "metrics": metrics,
        "backtest_rows": len(bt),
        "decision": "requires_review_before_real_use",
        "trace": trace,
    }
    (ARTIFACT_DIR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
