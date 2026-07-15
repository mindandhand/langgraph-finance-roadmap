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
2024-01-12,SH600000,10.82,1300000
2024-01-02,SZ000001,12.00,2200000
2024-01-03,SZ000001,11.90,2180000
2024-01-04,SZ000001,12.10,2250000
2024-01-05,SZ000001,12.35,2290000
2024-01-08,SZ000001,12.30,2310000
2024-01-09,SZ000001,12.55,2350000
2024-01-10,SZ000001,12.48,2330000
2024-01-11,SZ000001,12.70,2380000
2024-01-12,SZ000001,12.82,2400000
"""


def main() -> None:
    df = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["feature_momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
    df["label_next_return"] = by_symbol["close"].shift(-1) / df["close"] - 1
    dataset = df.dropna().reset_index(drop=True)

    splits = {
        "train": dataset[dataset["date"] <= "2024-01-08"],
        "valid": dataset[(dataset["date"] > "2024-01-08") & (dataset["date"] <= "2024-01-10")],
        "test": dataset[dataset["date"] > "2024-01-10"],
    }

    for name, part in splits.items():
        dates = part["date"].dt.strftime("%Y-%m-%d").unique().tolist()
        print(f"{name}: rows={len(part)}, dates={dates}")

    print("\nPrepared dataset:")
    print(dataset[["date", "symbol", "feature_momentum_3d", "label_next_return"]].to_string(index=False))


if __name__ == "__main__":
    main()
