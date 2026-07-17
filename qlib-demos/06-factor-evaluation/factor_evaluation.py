import json
import os
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qlib_demo_common import load_features, print_context, with_datetime_instrument_index


DEFAULT_FACTOR = "$close / Ref($close, 20) - 1"
DEFAULT_LABEL = "Ref($close, -5) / $close - 1"


def evaluate_factor(expression: str, label: str, quantiles: int = 5) -> dict:
    data = with_datetime_instrument_index(
        load_features([expression, label], ["factor", "label"])
    )
    total_rows = len(data)
    data = data.dropna()

    daily = data.groupby(level="datetime").apply(
        lambda g: pd.Series(
            {
                "ic": g["factor"].corr(g["label"]),
                "rank_ic": g["factor"].corr(g["label"], method="spearman"),
            }
        ),
        include_groups=False,
    )

    def quantile_return(group: pd.DataFrame) -> pd.Series:
        bucket = pd.qcut(group["factor"].rank(method="first"), quantiles, labels=False, duplicates="drop")
        return group.groupby(bucket)["label"].mean()

    quantile = data.groupby(level="datetime").apply(quantile_return, include_groups=False)
    quantile_mean = quantile.groupby(level=-1).mean().to_dict()

    ic_std = daily["ic"].std()
    rank_ic_std = daily["rank_ic"].std()
    return {
        "expression": expression,
        "label": label,
        "rows": int(len(data)),
        "coverage": round(float(len(data) / total_rows), 6) if total_rows else 0.0,
        "ic_mean": round(float(daily["ic"].mean()), 6),
        "rank_ic_mean": round(float(daily["rank_ic"].mean()), 6),
        "icir": round(float(daily["ic"].mean() / ic_std), 6) if ic_std else None,
        "rank_icir": round(float(daily["rank_ic"].mean() / rank_ic_std), 6) if rank_ic_std else None,
        "quantile_return_mean": {str(int(k)): round(float(v), 6) for k, v in quantile_mean.items()},
    }


def main() -> None:
    expression = os.getenv("QLIB_FACTOR_EXPR", DEFAULT_FACTOR)
    label = os.getenv("QLIB_LABEL_EXPR", DEFAULT_LABEL)
    print_context("Qlib factor evaluation")
    metrics = evaluate_factor(expression, label)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
