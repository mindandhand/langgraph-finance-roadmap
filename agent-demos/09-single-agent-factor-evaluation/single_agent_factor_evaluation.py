from io import StringIO

import pandas as pd


CSV = """date,symbol,close
2024-01-02,A,10.0
2024-01-03,A,10.2
2024-01-04,A,10.5
2024-01-05,A,10.4
2024-01-08,A,10.8
2024-01-02,B,20.0
2024-01-03,B,19.8
2024-01-04,B,20.1
2024-01-05,B,20.4
2024-01-08,B,20.2
"""


def prepare() -> pd.DataFrame:
    df = pd.read_csv(StringIO(CSV), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["factor"] = df["close"] / by_symbol["close"].shift(2) - 1
    df["label"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna().reset_index(drop=True)


def evaluate(data: pd.DataFrame) -> dict[str, float]:
    daily = data.groupby("date").apply(
        lambda g: pd.Series({
            "ic": g["factor"].corr(g["label"]),
            "rank_ic": g["factor"].corr(g["label"], method="spearman"),
        }),
        include_groups=False,
    )
    return {"mean_ic": float(daily["ic"].mean()), "mean_rank_ic": float(daily["rank_ic"].mean())}


if __name__ == "__main__":
    metrics = evaluate(prepare())
    print("Agent report:")
    print(f"- candidate_factor: 2-day momentum")
    print(f"- mean_ic: {metrics['mean_ic']:.4f}")
    print(f"- mean_rank_ic: {metrics['mean_rank_ic']:.4f}")
    print("- conclusion: evidence is only a toy-sample demonstration, not an investment claim")
