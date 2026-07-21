#!/usr/bin/env python3
"""
Download HS300 ETF (510300) daily data from akshare and save in qlib binary format.

Output layout (relative to qlib-demos/):
    qlib-data/
    ├── calendars/day.txt
    ├── instruments/all.txt
    └── features/sh510300/
        ├── open.day.bin
        ├── close.day.bin
        ├── high.day.bin
        ├── low.day.bin
        ├── volume.day.bin
        ├── amount.day.bin
        └── factor.day.bin

Usage:
    cd qlib-demos
    python download_to_qlib.py
    python download_to_qlib.py --start 20150101 --end 20241231

To use the data in qlib:
    import qlib
    qlib.init(provider_uri="qlib-data", region="cn")
"""

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SYMBOL = "510300"
QLIB_SYMBOL = "sh510300"
DATA_DIR = Path(__file__).parent / "qlib-data"  # qlib-demos/qlib-data


@dataclass(frozen=True)
class InstrumentSpec:
    source_symbol: str
    qlib_symbol: str
    name: str


DEFAULT_INSTRUMENTS = (
    InstrumentSpec("510050", "sh510050", "上证50 ETF"),
    InstrumentSpec("510300", "sh510300", "沪深300 ETF"),
    InstrumentSpec("510500", "sh510500", "中证500 ETF"),
    InstrumentSpec("159915", "sz159915", "创业板 ETF"),
    InstrumentSpec("588000", "sh588000", "科创50 ETF"),
)

COLUMN_MAP = {
    "日期": "date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
    "成交额": "amount",
}
FEATURES = ["open", "close", "high", "low", "volume", "amount", "factor"]


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
def download(symbol: str, start: str, end: str, adjust: str = "qfq") -> pd.DataFrame:
    import akshare as ak  # lazy import so the script loads without akshare for --help

    print(f"[download] {symbol}  {start} → {end}  adjust={adjust}")
    df = ak.fund_etf_hist_em(
        symbol=symbol,
        period="daily",
        start_date=start,
        end_date=end,
        adjust=adjust,
    )
    df = df.rename(columns=COLUMN_MAP)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # qfq data already carries the price adjustment; set factor = 1.0
    # If you need true unadjusted + factor, download both and divide.
    df["factor"] = 1.0

    keep = [c for c in FEATURES if c in df.columns]
    df = df[keep].astype(np.float32)
    print(f"[download] {len(df)} rows  {df.index[0].date()} → {df.index[-1].date()}")
    return df


# ---------------------------------------------------------------------------
# Write qlib binary format
# ---------------------------------------------------------------------------
def build_calendar(frames: Mapping[str, pd.DataFrame]) -> pd.DatetimeIndex:
    if not frames:
        raise ValueError("cannot build a calendar without instrument frames")

    calendar = pd.DatetimeIndex([])
    for frame in frames.values():
        calendar = calendar.union(frame.index)
    return calendar.drop_duplicates().sort_values()


def write_calendar(dates: pd.DatetimeIndex, out_dir: Path) -> None:
    path = out_dir / "calendars" / "day.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(d.strftime("%Y-%m-%d") for d in dates) + "\n")
    print(f"[calendar] {len(dates)} days → {path}")


def write_instruments(frames: Mapping[str, pd.DataFrame], out_dir: Path) -> None:
    path = out_dir / "instruments" / "all.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{qlib_symbol}\t{frame.index[0]:%Y-%m-%d}\t{frame.index[-1]:%Y-%m-%d}"
        for qlib_symbol, frame in sorted(frames.items())
    ]
    path.write_text("\n".join(lines) + "\n")
    print(f"[instruments] {path}")


def write_features(df: pd.DataFrame, qlib_symbol: str, calendar: pd.DatetimeIndex, out_dir: Path) -> None:
    feat_dir = out_dir / "features" / qlib_symbol
    feat_dir.mkdir(parents=True, exist_ok=True)

    # Slice calendar to [first_date, last_date] of the stock
    start_pos = calendar.searchsorted(df.index[0])
    end_pos = calendar.searchsorted(df.index[-1])
    cal_slice = calendar[start_pos : end_pos + 1]

    for col in FEATURES:
        if col not in df.columns:
            continue
        # Align to calendar slice; NaN for any gap (suspended trading, etc.)
        arr = df[col].reindex(cal_slice).values.astype(np.float32)
        path = feat_dir / f"{col}.day.bin"
        # Qlib stores the calendar start index as the first float in each feature file.
        np.hstack([start_pos, arr]).astype("<f4").tofile(str(path))
        nan_count = int(np.isnan(arr).sum())
        print(f"[feature] {path.name}  {len(arr)} values  ({nan_count} NaN)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download ETF data → qlib format")
    parser.add_argument("--symbol", default=SYMBOL, help="AkShare ETF code (default: 510300)")
    parser.add_argument("--qlib-symbol", default=QLIB_SYMBOL, help="Qlib instrument name (default: sh510300)")
    parser.add_argument("--start", default="20100104", help="Start date YYYYMMDD")
    parser.add_argument("--end", default=datetime.now().strftime("%Y%m%d"), help="End date YYYYMMDD")
    parser.add_argument("--adjust", default="qfq", choices=["qfq", "hfq", ""], help="Price adjustment (default: qfq)")
    parser.add_argument("--out-dir", default=str(DATA_DIR), help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)

    df = download(args.symbol, args.start, args.end, args.adjust)

    frames = {args.qlib_symbol: df}
    calendar = build_calendar(frames)
    start_str = df.index[0].strftime("%Y-%m-%d")
    end_str = df.index[-1].strftime("%Y-%m-%d")

    write_calendar(calendar, out_dir)
    write_instruments(frames, out_dir)
    write_features(df, args.qlib_symbol, calendar, out_dir)

    print(f"\n✓ Done — data saved to: {out_dir.resolve()}")
    print("\nQuick verification:")
    print(f"  import qlib")
    print(f"  qlib.init(provider_uri='{out_dir}', region='cn')")
    print(f"  from qlib.data import D")
    print(f"  df = D.features(['{args.qlib_symbol}'], ['$close'], '{start_str}', '{end_str}')")
    print(f"  print(df.head())")


if __name__ == "__main__":
    main()
