from io import StringIO

import pandas as pd


SAMPLE = """date,symbol,close,volume
2024-01-02,SH600000,10.00,1200000
2024-01-03,SH600000,10.10,1180000
2024-01-04,SH600000,10.30,1215000
2024-01-05,SH600000,10.20,1195000
2024-01-08,SH600000,10.45,1250000
2024-01-09,SH600000,10.60,1280000
2024-01-10,SH600000,10.52,1260000
2024-01-11,SH600000,10.70,1290000
2024-01-02,SZ000001,12.00,2200000
2024-01-03,SZ000001,11.90,2180000
2024-01-04,SZ000001,12.10,2250000
2024-01-05,SZ000001,12.35,2290000
2024-01-08,SZ000001,12.30,2310000
2024-01-09,SZ000001,12.55,2350000
2024-01-10,SZ000001,12.48,2330000
2024-01-11,SZ000001,12.70,2380000
2024-01-02,SH600519,1700.00,90000
2024-01-03,SH600519,1712.00,91000
2024-01-04,SH600519,1705.00,88000
2024-01-05,SH600519,1720.00,93000
2024-01-08,SH600519,1735.00,94000
2024-01-09,SH600519,1748.00,97000
2024-01-10,SH600519,1738.00,92000
2024-01-11,SH600519,1760.00,98000
"""


def prepare() -> pd.DataFrame:
    df = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["factor"] = df["close"] / by_symbol["close"].shift(3) - 1
    df["label"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna(subset=["factor", "label"]).reset_index(drop=True)


def score_day(group: pd.DataFrame) -> pd.Series:
    ranked = group.sort_values("factor", ascending=False)
    return pd.Series({
        "ic": group["factor"].corr(group["label"]),
        "rank_ic": group["factor"].corr(group["label"], method="spearman"),
        "top_minus_bottom": ranked.iloc[0]["label"] - ranked.iloc[-1]["label"],
    })


def main() -> None:
    result = prepare().groupby("date").apply(score_day, include_groups=False)
    print(result.to_string())
    print("\nmean IC:", round(float(result["ic"].mean()), 6))
    print("mean Rank IC:", round(float(result["rank_ic"].mean()), 6))


if __name__ == "__main__":
    main()
