from io import StringIO

import pandas as pd


SAMPLE = """date,symbol,close,volume
2024-01-02,SH600000,10.00,1200000
2024-01-03,SH600000,10.10,1180000
2024-01-04,SH600000,10.30,1215000
2024-01-05,SH600000,10.20,1195000
2024-01-08,SH600000,10.45,1250000
2024-01-09,SH600000,10.60,1280000
2024-01-02,SZ000001,12.00,2200000
2024-01-03,SZ000001,11.90,2180000
2024-01-04,SZ000001,12.10,2250000
2024-01-05,SZ000001,12.35,2290000
2024-01-08,SZ000001,12.30,2310000
2024-01-09,SZ000001,12.55,2350000
2024-01-02,SH600519,1700.00,90000
2024-01-03,SH600519,1712.00,91000
2024-01-04,SH600519,1705.00,88000
2024-01-05,SH600519,1720.00,93000
2024-01-08,SH600519,1735.00,94000
2024-01-09,SH600519,1748.00,97000
"""


def main() -> None:
    df = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")

    df["ref_close_1"] = by_symbol["close"].shift(1)
    df["momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
    df["mean_close_3d"] = by_symbol["close"].rolling(3).mean().reset_index(level=0, drop=True)
    df["momentum_rank"] = df.groupby("date")["momentum_3d"].rank(ascending=False, method="first")

    cols = ["date", "symbol", "close", "ref_close_1", "momentum_3d", "mean_close_3d", "momentum_rank"]
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
