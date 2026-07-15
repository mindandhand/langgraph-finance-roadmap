from io import StringIO

import pandas as pd


PREDICTIONS = """date,symbol,score,label
2024-01-10,SH600000,0.010,-0.0075
2024-01-10,SZ000001,0.014,-0.0056
2024-01-10,SH600519,0.006,-0.0057
2024-01-11,SH600000,0.007,0.0114
2024-01-11,SZ000001,0.012,0.0094
2024-01-11,SH600519,0.005,0.0068
2024-01-12,SH600000,0.009,-0.0055
2024-01-12,SZ000001,0.006,-0.0031
2024-01-12,SH600519,0.004,-0.0040
"""


def main() -> None:
    pred = pd.read_csv(StringIO(PREDICTIONS), parse_dates=["date"])
    picks = pred.sort_values(["date", "score"], ascending=[True, False]).groupby("date").head(1)
    picks = picks.sort_values("date").reset_index(drop=True)
    picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
    picks.loc[0, "turnover"] = 1.0
    picks["cost"] = picks["turnover"] * 0.001
    picks["net_return"] = picks["label"] - picks["cost"]
    picks["equity"] = (1 + picks["net_return"]).cumprod()

    print(picks[["date", "symbol", "score", "label", "turnover", "cost", "net_return", "equity"]].to_string(index=False))
    print("total net return:", round(float(picks["equity"].iloc[-1] - 1), 6))


if __name__ == "__main__":
    main()
