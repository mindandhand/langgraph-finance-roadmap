"""
Build a Qlib-ready CSV package for one CSI 300 ETF with AkShare.

Default ETF:
    510300 - 华泰柏瑞沪深300ETF, represented as SH510300 in the output.

The script creates normalized CSV and metadata that can be converted to Qlib
bin format with Qlib's official scripts/dump_bin.py.

Run:
    python build_hs300_etf_from_akshare.py
"""
import os
from pathlib import Path

import akshare as ak
import pandas as pd


ETF_SYMBOL = "510300"
INSTRUMENT = "SH510300"
START_DATE = "20150101"
END_DATE = "20260715"

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "qlib-data" / "hs300_etf_510300"
CSV_DIR = OUT_DIR / "csv"


def clear_stale_proxy_env() -> None:
    for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"]:
        os.environ.pop(key, None)


def fetch_etf_daily() -> pd.DataFrame:
    try:
        raw = ak.fund_etf_hist_em(
            symbol=ETF_SYMBOL,
            period="daily",
            start_date=START_DATE,
            end_date=END_DATE,
            adjust="qfq",
        )
    except Exception as em_error:
        raw = ak.fund_etf_hist_sina(symbol=f"sh{ETF_SYMBOL}")
        raw["date"] = pd.to_datetime(raw["date"])
        raw = raw[
            raw["date"].between(
                pd.Timestamp(START_DATE),
                pd.Timestamp(END_DATE),
            )
        ].copy()
        raw.attrs["fallback_reason"] = f"eastmoney failed: {em_error}"
    if raw.empty:
        raise RuntimeError(f"AkShare returned no data for ETF {ETF_SYMBOL}")
    return raw


def normalize(raw: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
        "振幅": "amplitude",
        "涨跌幅": "change_pct",
        "涨跌额": "change",
        "换手率": "turnover",
    }
    frame = raw.rename(columns=rename_map).copy()
    required = ["date", "open", "close", "high", "low", "volume", "amount"]
    missing = [col for col in required if col not in frame.columns]
    if missing:
        raise ValueError(f"AkShare response missing expected columns: {missing}; got {list(raw.columns)}")

    frame["date"] = pd.to_datetime(frame["date"])
    frame["symbol"] = INSTRUMENT
    frame["factor"] = 1.0

    numeric_cols = [
        "open",
        "close",
        "high",
        "low",
        "volume",
        "amount",
        "amplitude",
        "change_pct",
        "change",
        "turnover",
        "factor",
    ]
    for col in numeric_cols:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")

    frame = frame.sort_values("date").reset_index(drop=True)
    columns = [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "factor",
        "change",
        "change_pct",
        "turnover",
        "amplitude",
    ]
    return frame[[col for col in columns if col in frame.columns]]


def validate(frame: pd.DataFrame) -> None:
    if frame[["date", "symbol", "open", "high", "low", "close", "volume"]].isna().any().any():
        raise ValueError("Normalized data contains nulls in required fields")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Price fields must be positive")
    if (frame["volume"] < 0).any():
        raise ValueError("Volume must be non-negative")
    duplicated = frame.duplicated(["symbol", "date"]).sum()
    if duplicated:
        raise ValueError(f"Duplicated symbol/date rows: {duplicated}")


def write_outputs(frame: pd.DataFrame) -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = CSV_DIR / f"{INSTRUMENT}.csv"
    frame.to_csv(csv_path, index=False, date_format="%Y-%m-%d")

    calendar = frame["date"].dt.strftime("%Y-%m-%d").drop_duplicates().sort_values()
    calendar.to_csv(OUT_DIR / "calendar.txt", index=False, header=False)

    instrument_line = f"{INSTRUMENT},{frame['date'].min().date()},{frame['date'].max().date()}\n"
    (OUT_DIR / "instruments.txt").write_text(instrument_line, encoding="utf-8")

    include_fields = ",".join(col for col in frame.columns if col not in {"symbol", "date"})
    command = (
        "python scripts/dump_bin.py dump_all "
        f"--data_path {CSV_DIR} "
        f"--qlib_dir {OUT_DIR / 'qlib_bin'} "
        f"--include_fields {include_fields} "
        "--symbol_field_name symbol "
        "--date_field_name date "
        "--file_suffix .csv"
    )
    (OUT_DIR / "dump_bin_command.txt").write_text(command + "\n", encoding="utf-8")

    readme = f"""# HS300 ETF Qlib-ready data

Source: AkShare `fund_etf_hist_em`

- ETF symbol: `{ETF_SYMBOL}`
- Qlib instrument: `{INSTRUMENT}`
- Rows: `{len(frame)}`
- Date range: `{frame['date'].min().date()}` to `{frame['date'].max().date()}`
- Normalized CSV: `{csv_path}`

Convert to Qlib bin format from a Qlib checkout:

```bash
{command}
```

Then use:

```bash
export QLIB_PROVIDER_URI={OUT_DIR / 'qlib_bin'}
```
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    clear_stale_proxy_env()
    raw = fetch_etf_daily()
    frame = normalize(raw)
    validate(frame)
    write_outputs(frame)

    print("Generated HS300 ETF Qlib-ready CSV package")
    print("instrument:", INSTRUMENT)
    print("rows:", len(frame))
    print("date range:", frame["date"].min().date(), "to", frame["date"].max().date())
    print("output:", OUT_DIR)
    print("csv:", CSV_DIR / f"{INSTRUMENT}.csv")
    print("dump command:", OUT_DIR / "dump_bin_command.txt")


if __name__ == "__main__":
    main()
