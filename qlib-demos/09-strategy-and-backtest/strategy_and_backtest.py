import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qlib_demo_common import load_features, print_context, with_datetime_instrument_index


DEFAULT_SCORE = "$close / Ref($close, 20) - 1"
DEFAULT_LABEL = "Ref($close, -2) / Ref($close, -1) - 1"


def main() -> None:
    score_expr = os.getenv("QLIB_SCORE_EXPR", DEFAULT_SCORE)
    label_expr = os.getenv("QLIB_LABEL_EXPR", DEFAULT_LABEL)
    topk = int(os.getenv("QLIB_TOPK", "50"))
    cost_rate = float(os.getenv("QLIB_COST_RATE", "0.001"))

    print_context("Qlib score to simple top-k backtest")
    data = with_datetime_instrument_index(load_features([score_expr, label_expr], ["score", "label"])).dropna()

    reports = []
    previous = set()
    for date, group in data.groupby(level="datetime", sort=True):
        picked = group.sort_values("score", ascending=False).head(topk)
        current = set(picked.index.get_level_values("instrument"))
        buys = current - previous
        sells = previous - current
        turnover = (len(buys) + len(sells)) / max(topk, 1)
        gross_return = picked["label"].mean()
        net_return = gross_return - turnover * cost_rate
        reports.append(
            {
                "datetime": date,
                "holdings": len(current),
                "gross_return": gross_return,
                "turnover": turnover,
                "cost": turnover * cost_rate,
                "net_return": net_return,
            }
        )
        previous = current

    import pandas as pd

    report = pd.DataFrame(reports).set_index("datetime")
    report["equity"] = (1 + report["net_return"]).cumprod()
    print(report.head(20).to_string())
    print("total net return:", round(float(report["equity"].iloc[-1] - 1), 6))
    print("mean turnover:", round(float(report["turnover"].mean()), 6))


if __name__ == "__main__":
    main()
