from io import StringIO

import pandas as pd


SAMPLE = """date,symbol,open,high,low,close,volume
2024-01-02,SH600000,9.90,10.08,9.86,10.00,1200000
2024-01-03,SH600000,10.02,10.15,9.98,10.10,1180000
2024-01-04,SH600000,10.12,10.35,10.08,10.30,1215000
2024-01-05,SH600000,10.28,10.36,10.15,10.20,1195000
2024-01-08,SH600000,10.21,10.50,10.18,10.45,1250000
2024-01-09,SH600000,10.48,10.66,10.40,10.60,1280000
2024-01-02,SZ000001,11.95,12.08,11.88,12.00,2200000
2024-01-03,SZ000001,12.02,12.06,11.86,11.90,2180000
2024-01-04,SZ000001,11.92,12.15,11.90,12.10,2250000
2024-01-05,SZ000001,12.12,12.40,12.08,12.35,2290000
2024-01-08,SZ000001,12.36,12.42,12.20,12.30,2310000
2024-01-09,SZ000001,12.32,12.60,12.30,12.55,2350000
"""


def simplified_alpha158_config() -> dict[str, str]:
    return {
        "KMID": "($close-$open)/$open",
        "KLEN": "($high-$low)/$open",
        "OPEN0": "$open/$close",
        "ROC5": "Ref($close, 5)/$close",
        "MA5": "Mean($close, 5)/$close",
        "STD5": "Std($close, 5)/$close",
    }


def simplified_alpha360_config(days: int = 3) -> dict[str, str]:
    fields: dict[str, str] = {}
    for i in range(days - 1, -1, -1):
        fields[f"CLOSE{i}"] = "$close/$close" if i == 0 else f"Ref($close, {i})/$close"
        fields[f"VOLUME{i}"] = "$volume/($volume+1e-12)" if i == 0 else f"Ref($volume, {i})/($volume+1e-12)"
    return fields


def custom_factor_config() -> dict[str, str]:
    return {
        "MOM3": "$close/Ref($close, 3)-1",
        "VOL_SHOCK3": "$volume/Mean($volume, 3)-1",
        "INTRADAY_STRENGTH": "($close-$open)/($high-$low+1e-12)",
    }


def compute_demo_features() -> pd.DataFrame:
    df = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"]).sort_values(["symbol", "date"])
    by_symbol = df.groupby("symbol")
    df["KMID"] = (df["close"] - df["open"]) / df["open"]
    df["KLEN"] = (df["high"] - df["low"]) / df["open"]
    df["MOM3"] = df["close"] / by_symbol["close"].shift(3) - 1
    df["VOL_SHOCK3"] = df["volume"] / by_symbol["volume"].rolling(3).mean().reset_index(level=0, drop=True) - 1
    df["CLOSE2"] = by_symbol["close"].shift(2) / df["close"]
    df["CLOSE1"] = by_symbol["close"].shift(1) / df["close"]
    df["CLOSE0"] = 1.0
    return df.dropna().reset_index(drop=True)


def main() -> None:
    print("Simplified Alpha158 expressions:")
    for name, expr in simplified_alpha158_config().items():
        print(f"  {name:12s} = {expr}")

    print("\nSimplified Alpha360 expressions:")
    for name, expr in simplified_alpha360_config().items():
        print(f"  {name:12s} = {expr}")

    print("\nCustom factor expressions:")
    for name, expr in custom_factor_config().items():
        print(f"  {name:18s} = {expr}")

    print("\nComputed feature preview:")
    cols = ["date", "symbol", "KMID", "KLEN", "MOM3", "VOL_SHOCK3", "CLOSE2", "CLOSE1", "CLOSE0"]
    print(compute_demo_features()[cols].to_string(index=False))


if __name__ == "__main__":
    main()
