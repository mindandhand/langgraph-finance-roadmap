from io import StringIO

import pandas as pd


CSV = """date,symbol,close
2024-01-02,SH510300,3.90
2024-01-03,SH510300,3.94
2024-01-04,SH510300,3.98
2024-01-05,SH510300,3.92
2024-01-08,SH510300,4.02
2024-01-09,SH510300,4.06
"""


def compute_momentum(frame: pd.DataFrame, lookback: int) -> pd.DataFrame:
    df = frame.sort_values(["symbol", "date"]).copy()
    by_symbol = df.groupby("symbol")
    df["factor_momentum"] = df["close"] / by_symbol["close"].shift(lookback) - 1
    df["label_next_return"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna().reset_index(drop=True)


if __name__ == "__main__":
    prices = pd.read_csv(StringIO(CSV), parse_dates=["date"])
    result = compute_momentum(prices, lookback=3)
    print(result.to_string(index=False))
