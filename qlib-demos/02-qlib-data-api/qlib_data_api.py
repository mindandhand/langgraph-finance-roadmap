import os
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
"""


def load_csv(symbols: list[str], start: str, end: str) -> pd.DataFrame:
    frame = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"])
    mask = frame["symbol"].isin(symbols) & frame["date"].between(pd.Timestamp(start), pd.Timestamp(end))
    return frame.loc[mask].sort_values(["symbol", "date"]).reset_index(drop=True)


def load_qlib(provider_uri: str, symbols: list[str], start: str, end: str) -> pd.DataFrame:
    import qlib
    from qlib.constant import REG_CN
    from qlib.data import D

    qlib.init(provider_uri=provider_uri, region=REG_CN)
    raw = D.features(
        instruments=symbols,
        fields=["$close", "$volume"],
        start_time=start,
        end_time=end,
        freq="day",
    )
    frame = raw.rename(columns={"$close": "close", "$volume": "volume"}).reset_index()
    frame = frame.rename(columns={"datetime": "date", "instrument": "symbol"})
    return frame.sort_values(["symbol", "date"]).reset_index(drop=True)


def main() -> None:
    symbols = ["SH600000", "SZ000001"]
    start, end = "2024-01-02", "2024-01-09"
    provider_uri = os.getenv("QLIB_PROVIDER_URI")

    if provider_uri:
        try:
            data = load_qlib(provider_uri, symbols, start, end)
            source = f"qlib://{provider_uri}"
        except Exception as exc:
            data = load_csv(symbols, start, end)
            source = f"csv fallback because Qlib failed: {exc}"
    else:
        data = load_csv(symbols, start, end)
        source = "csv fallback; set QLIB_PROVIDER_URI to use real Qlib data"

    print("source:", source)
    print(data.to_string(index=False))


if __name__ == "__main__":
    main()
