from dataclasses import dataclass
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
"""


class MiniDataHandler:
    def __init__(self, raw: pd.DataFrame):
        self.raw = raw.sort_values(["symbol", "date"]).copy()

    def fetch(self) -> pd.DataFrame:
        df = self.raw.copy()
        by_symbol = df.groupby("symbol")
        df["feature_momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
        df["feature_volume_change_3d"] = df["volume"] / by_symbol["volume"].shift(3) - 1
        df["label_return_1d"] = by_symbol["close"].shift(-1) / df["close"] - 1
        return df.dropna().reset_index(drop=True)


@dataclass
class MiniDataset:
    data: pd.DataFrame
    segments: dict[str, tuple[str, str]]

    def prepare(self, segment: str) -> pd.DataFrame:
        start, end = self.segments[segment]
        mask = self.data["date"].between(pd.Timestamp(start), pd.Timestamp(end))
        return self.data.loc[mask].reset_index(drop=True)


def main() -> None:
    raw = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"])
    handler = MiniDataHandler(raw)
    dataset = MiniDataset(
        data=handler.fetch(),
        segments={
            "train": ("2024-01-01", "2024-01-08"),
            "valid": ("2024-01-09", "2024-01-09"),
            "test": ("2024-01-10", "2024-01-31"),
        },
    )

    for name in ["train", "valid", "test"]:
        part = dataset.prepare(name)
        print(f"{name}: rows={len(part)}")
        print(part[["date", "symbol", "feature_momentum_3d", "label_return_1d"]].to_string(index=False))
        print()


if __name__ == "__main__":
    main()
