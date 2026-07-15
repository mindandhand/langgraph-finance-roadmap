import json
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd


CONFIG = {
    "experiment_id": "config_alpha_001",
    "features": ["momentum_3d", "volume_change_3d"],
    "label": "next_1d_return",
    "train_end": "2024-01-09",
    "test_start": "2024-01-10",
    "topk": 1,
    "cost_rate": 0.001,
}

SAMPLE = """date,symbol,close,volume
2024-01-02,SH600000,10.00,1200000
2024-01-03,SH600000,10.10,1180000
2024-01-04,SH600000,10.30,1215000
2024-01-05,SH600000,10.20,1195000
2024-01-08,SH600000,10.45,1250000
2024-01-09,SH600000,10.60,1280000
2024-01-10,SH600000,10.52,1260000
2024-01-11,SH600000,10.70,1290000
2024-01-12,SH600000,10.82,1300000
2024-01-15,SH600000,10.76,1270000
2024-01-02,SZ000001,12.00,2200000
2024-01-03,SZ000001,11.90,2180000
2024-01-04,SZ000001,12.10,2250000
2024-01-05,SZ000001,12.35,2290000
2024-01-08,SZ000001,12.30,2310000
2024-01-09,SZ000001,12.55,2350000
2024-01-10,SZ000001,12.48,2330000
2024-01-11,SZ000001,12.70,2380000
2024-01-12,SZ000001,12.82,2400000
2024-01-15,SZ000001,12.78,2370000
2024-01-02,SH600519,1700.00,90000
2024-01-03,SH600519,1712.00,91000
2024-01-04,SH600519,1705.00,88000
2024-01-05,SH600519,1720.00,93000
2024-01-08,SH600519,1735.00,94000
2024-01-09,SH600519,1748.00,97000
2024-01-10,SH600519,1738.00,92000
2024-01-11,SH600519,1760.00,98000
2024-01-12,SH600519,1772.00,99000
2024-01-15,SH600519,1765.00,95000
"""


def build_dataset() -> pd.DataFrame:
    df = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
    df["volume_change_3d"] = df["volume"] / by_symbol["volume"].shift(3) - 1
    df["next_1d_return"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna().reset_index(drop=True)


def fit(train: pd.DataFrame, features: list[str], label: str) -> np.ndarray:
    x = train[features].to_numpy(float)
    y = train[label].to_numpy(float)
    x = np.column_stack([np.ones(len(x)), x])
    return np.linalg.pinv(x.T @ x) @ x.T @ y


def main() -> None:
    dataset = build_dataset()
    train = dataset[dataset["date"] <= CONFIG["train_end"]].copy()
    test = dataset[dataset["date"] >= CONFIG["test_start"]].copy()

    weights = fit(train, CONFIG["features"], CONFIG["label"])
    x_test = np.column_stack([np.ones(len(test)), test[CONFIG["features"]].to_numpy(float)])
    test["score"] = x_test @ weights

    ic = test.groupby("date").apply(
        lambda g: g["score"].corr(g[CONFIG["label"]]),
        include_groups=False,
    )
    picks = test.sort_values(["date", "score"], ascending=[True, False]).groupby("date").head(CONFIG["topk"])
    picks = picks.sort_values("date").reset_index(drop=True)
    picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
    picks.loc[0, "turnover"] = 1.0
    picks["net_return"] = picks[CONFIG["label"]] - picks["turnover"] * CONFIG["cost_rate"]
    picks["equity"] = (1 + picks["net_return"]).cumprod()

    out = Path(__file__).resolve().parent / "artifacts" / CONFIG["experiment_id"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")
    test.to_csv(out / "predictions.csv", index=False)
    picks.to_csv(out / "backtest.csv", index=False)

    metrics = {
        "mean_ic": round(float(ic.mean()), 6),
        "total_net_return": round(float(picks["equity"].iloc[-1] - 1), 6),
        "prediction_rows": len(test),
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("metrics:", metrics)
    print("artifacts:", out)


if __name__ == "__main__":
    main()
