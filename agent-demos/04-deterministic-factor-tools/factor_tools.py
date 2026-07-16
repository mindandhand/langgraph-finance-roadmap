from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "qlib-demos"
    / "qlib-data"
    / "hs300_etf_510300"
    / "csv"
    / "SH510300.csv"
)
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


@dataclass(frozen=True)
class FactorSpec:
    name: str
    lookback: int
    label_horizon: int


@dataclass(frozen=True)
class ArtifactRef:
    path: str
    rows: int
    columns: list[str]


def load_prices(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
    selected = frame[
        (frame["symbol"] == symbol)
        & frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    ].copy()
    if selected.empty:
        raise ValueError(f"no data for {symbol} from {start_date} to {end_date}")
    return selected.sort_values(["symbol", "date"]).reset_index(drop=True)


def compute_momentum(frame: pd.DataFrame, spec: FactorSpec) -> pd.DataFrame:
    df = frame.sort_values(["symbol", "date"]).copy()
    by_symbol = df.groupby("symbol")
    df["factor"] = df["close"] / by_symbol["close"].shift(spec.lookback) - 1
    df["label"] = by_symbol["close"].shift(-spec.label_horizon) / df["close"] - 1
    return df.dropna(subset=["factor", "label"]).reset_index(drop=True)


def write_factor_artifact(data: pd.DataFrame, name: str) -> ArtifactRef:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    path = ARTIFACT_DIR / f"{name}.csv"
    data.to_csv(path, index=False)
    return ArtifactRef(path=str(path), rows=len(data), columns=data.columns.tolist())


if __name__ == "__main__":
    spec = FactorSpec(name="momentum_5d", lookback=5, label_horizon=1)
    prices = load_prices("SH510300", "2024-01-01", "2024-03-31")
    factor_data = compute_momentum(prices, spec)
    artifact = write_factor_artifact(factor_data, spec.name)
    print("spec:", spec)
    print("artifact:", artifact)
    print(factor_data[["date", "symbol", "close", "factor", "label"]].head().to_string(index=False))
