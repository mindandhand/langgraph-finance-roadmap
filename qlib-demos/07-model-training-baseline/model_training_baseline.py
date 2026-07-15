from io import StringIO

import numpy as np
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
    df["label"] = by_symbol["close"].shift(-1) / df["close"] - 1
    return df.dropna().reset_index(drop=True)


def fit_linear(train: pd.DataFrame, features: list[str]) -> np.ndarray:
    x = train[features].to_numpy(float)
    y = train["label"].to_numpy(float)
    x = np.column_stack([np.ones(len(x)), x])
    return np.linalg.pinv(x.T @ x) @ x.T @ y


def main() -> None:
    features = ["momentum_3d", "volume_change_3d"]
    data = build_dataset()
    train = data[data["date"] <= "2024-01-09"].copy()
    test = data[data["date"] > "2024-01-09"].copy()
    weights = fit_linear(train, features)

    x_test = np.column_stack([np.ones(len(test)), test[features].to_numpy(float)])
    test["score"] = x_test @ weights
    ic = test.groupby("date").apply(lambda g: g["score"].corr(g["label"]), include_groups=False)

    print("weights:", dict(zip(["intercept", *features], [round(float(v), 6) for v in weights])))
    print("test predictions:")
    print(test[["date", "symbol", "score", "label"]].to_string(index=False))
    print("mean test IC:", round(float(ic.mean()), 6))


if __name__ == "__main__":
    main()
