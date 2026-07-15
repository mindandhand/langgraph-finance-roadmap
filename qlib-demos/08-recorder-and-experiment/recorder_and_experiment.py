import json
from io import StringIO
from pathlib import Path

import pandas as pd


SAMPLE = """date,symbol,score,label
2024-01-10,SH600000,0.010,-0.0075
2024-01-10,SZ000001,0.014,-0.0056
2024-01-10,SH600519,0.006,-0.0057
2024-01-11,SH600000,0.007,0.0114
2024-01-11,SZ000001,0.012,0.0094
2024-01-11,SH600519,0.005,0.0068
"""


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts" / "exp_001"


def main() -> None:
    predictions = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"])
    daily_ic = predictions.groupby("date").apply(
        lambda g: g["score"].corr(g["label"]),
        include_groups=False,
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(ARTIFACT_DIR / "predictions.csv", index=False)

    params = {
        "experiment_id": "exp_001",
        "model": "linear_baseline",
        "features": ["momentum_3d", "volume_change_3d"],
        "label": "next_1d_return",
    }
    metrics = {
        "mean_ic": round(float(daily_ic.mean()), 6),
        "prediction_rows": len(predictions),
    }
    (ARTIFACT_DIR / "params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("recorded experiment:", ARTIFACT_DIR)
    print("params:", params)
    print("metrics:", metrics)


if __name__ == "__main__":
    main()
