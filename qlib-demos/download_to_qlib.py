#!/usr/bin/env python3
"""
Download five representative Chinese ETFs and save them in qlib binary format.

Output layout (relative to qlib-demos/):
    qlib-data/
    ├── calendars/day.txt
    ├── instruments/all.txt
    └── features/<qlib-symbol>/
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
    python download_to_qlib.py --symbol 510300 --qlib-symbol sh510300

By default the provider contains five ETFs. ``--symbol`` and ``--qlib-symbol``
must be supplied together to build a single-instrument provider instead.

To use the data in qlib:
    import qlib
    qlib.init(provider_uri="qlib-data", region="cn")
"""

import argparse
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
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
REQUIRED_FIELDS = ("open", "close", "high", "low", "volume", "amount", "factor")
FEATURES = list(REQUIRED_FIELDS)
QLIB_SYMBOL_PATTERN = re.compile(r"(?:sh|sz)\d{6}\Z")
SOURCE_SYMBOL_PATTERN = re.compile(r"\d{6}\Z")


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


def validate_frame(frame: pd.DataFrame, spec: InstrumentSpec) -> None:
    """Reject data that cannot safely form a qlib instrument."""
    symbol = spec.qlib_symbol
    if frame.empty:
        raise ValueError(f"{symbol} frame is empty")

    missing = [field for field in REQUIRED_FIELDS if field not in frame.columns]
    if missing:
        raise ValueError(f"{symbol} frame is missing required fields: {', '.join(missing)}")

    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError(f"{symbol} frame index must be a DatetimeIndex")
    if frame.index.has_duplicates:
        raise ValueError(f"{symbol} frame contains duplicate dates")
    if not frame.index.is_monotonic_increasing:
        raise ValueError(f"{symbol} frame dates must be monotonic increasing")


def _validate_qlib_symbol(qlib_symbol: str) -> None:
    if not isinstance(qlib_symbol, str) or not QLIB_SYMBOL_PATTERN.fullmatch(
        qlib_symbol
    ):
        raise ValueError(
            "qlib_symbol must match exactly 'sh' or 'sz' followed by six digits"
        )


def validate_instrument_specs(
    specs: Iterable[InstrumentSpec],
) -> tuple[InstrumentSpec, ...]:
    validated = tuple(specs)
    seen: set[str] = set()
    for spec in validated:
        _validate_qlib_symbol(spec.qlib_symbol)
        if not isinstance(spec.source_symbol, str) or not SOURCE_SYMBOL_PATTERN.fullmatch(
            spec.source_symbol
        ):
            raise ValueError("source_symbol must contain exactly six digits")
        if spec.qlib_symbol in seen:
            raise ValueError(f"duplicate qlib_symbol: {spec.qlib_symbol}")
        seen.add(spec.qlib_symbol)
    return validated


def download_all(
    specs: Iterable[InstrumentSpec], start: str, end: str, adjust: str
) -> dict[str, pd.DataFrame]:
    """Download and validate every instrument before returning any provider input."""
    validated_specs = validate_instrument_specs(specs)
    frames: dict[str, pd.DataFrame] = {}
    for spec in validated_specs:
        try:
            frame = download(spec.source_symbol, start, end, adjust)
            validate_frame(frame, spec)
        except Exception as exc:
            raise RuntimeError(
                f"failed to download or validate {spec.qlib_symbol} "
                f"(source {spec.source_symbol})"
            ) from exc
        frames[spec.qlib_symbol] = frame
    return frames


# ---------------------------------------------------------------------------
# Write qlib binary format
# ---------------------------------------------------------------------------
def build_calendar(frames: Mapping[str, pd.DataFrame]) -> pd.DatetimeIndex:
    if not frames:
        raise ValueError("cannot build a calendar without instrument frames")

    calendar = pd.DatetimeIndex([])
    for frame in frames.values():
        calendar = calendar.union(pd.DatetimeIndex(frame.index))
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


def write_provider(frames: Mapping[str, pd.DataFrame], out_dir: Path) -> None:
    """Write a complete multi-instrument qlib provider."""
    for qlib_symbol in frames:
        _validate_qlib_symbol(qlib_symbol)
    calendar = build_calendar(frames)
    write_calendar(calendar, out_dir)
    write_instruments(frames, out_dir)
    for qlib_symbol, frame in frames.items():
        write_features(frame, qlib_symbol, calendar, out_dir)


def validate_provider(out_dir: Path, frames: Mapping[str, pd.DataFrame]) -> None:
    """Independently verify the on-disk provider contract before publication."""
    for qlib_symbol in frames:
        _validate_qlib_symbol(qlib_symbol)
    expected_calendar = build_calendar(frames)
    calendar_path = out_dir / "calendars" / "day.txt"
    if not calendar_path.is_file():
        raise FileNotFoundError(f"missing provider calendar: {calendar_path}")
    calendar_lines = calendar_path.read_text().splitlines()
    if not calendar_lines:
        raise ValueError(f"provider calendar is empty: {calendar_path}")
    try:
        calendar = pd.DatetimeIndex(pd.to_datetime(calendar_lines))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid provider calendar: {calendar_path}") from exc
    if not calendar.equals(expected_calendar):
        raise ValueError(
            f"{calendar_path}: calendar does not exactly match instrument frames"
        )

    metadata_path = out_dir / "instruments" / "all.txt"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"missing instrument metadata: {metadata_path}")
    metadata_lines = metadata_path.read_text().splitlines()
    expected_metadata = [
        f"{qlib_symbol}\t{frame.index[0]:%Y-%m-%d}\t{frame.index[-1]:%Y-%m-%d}"
        for qlib_symbol, frame in sorted(frames.items())
    ]
    if metadata_lines != expected_metadata:
        raise ValueError(
            f"{metadata_path}: instrument metadata does not exactly match frames"
        )

    features_dir = out_dir / "features"
    if not features_dir.is_dir():
        raise FileNotFoundError(f"missing provider features directory: {features_dir}")
    feature_entries = {entry.name: entry for entry in features_dir.iterdir()}
    expected_symbols = set(frames)
    missing_symbols = expected_symbols - set(feature_entries)
    if missing_symbols:
        missing_dir = features_dir / sorted(missing_symbols)[0]
        raise FileNotFoundError(f"missing instrument feature directory: {missing_dir}")
    if set(feature_entries) != expected_symbols or any(
        not entry.is_dir() for entry in feature_entries.values()
    ):
        raise ValueError(
            f"{features_dir}: unexpected or missing instrument feature directories"
        )

    expected_feature_names = {f"{field}.day.bin" for field in REQUIRED_FIELDS}
    for qlib_symbol, frame in frames.items():
        instrument_dir = feature_entries[qlib_symbol]
        instrument_entries = {
            entry.name: entry for entry in instrument_dir.iterdir()
        }
        missing_features = expected_feature_names - set(instrument_entries)
        if missing_features:
            missing_path = instrument_dir / sorted(missing_features)[0]
            raise FileNotFoundError(f"missing provider feature: {missing_path}")
        if set(instrument_entries) != expected_feature_names or any(
            not entry.is_file() for entry in instrument_entries.values()
        ):
            raise ValueError(
                f"{instrument_dir}: unexpected or missing required feature files"
            )

        start_pos = expected_calendar.searchsorted(frame.index[0])
        end_pos = expected_calendar.searchsorted(frame.index[-1])
        calendar_slice = expected_calendar[start_pos : end_pos + 1]
        expected_length = len(calendar_slice) + 1
        for field in REQUIRED_FIELDS:
            feature_path = instrument_entries[f"{field}.day.bin"]
            feature_size = feature_path.stat().st_size
            float_size = np.dtype("<f4").itemsize
            if feature_size % float_size:
                raise ValueError(
                    f"invalid provider feature {feature_path}: "
                    "byte size is not aligned to float32 values"
                )
            values = np.fromfile(feature_path, dtype="<f4")
            if len(values) != expected_length:
                raise ValueError(
                    f"{feature_path}: feature length must be exactly "
                    f"{expected_length} float32 values, found {len(values)}"
                )
            if values[0] != float(start_pos):
                raise ValueError(
                    f"provider feature header mismatch at {feature_path}: "
                    f"expected {start_pos}, found {values[0]}"
                )
            expected_payload = (
                frame[field].reindex(calendar_slice).astype(np.float32).to_numpy()
            )
            if not np.array_equal(values[1:], expected_payload, equal_nan=True):
                raise ValueError(
                    f"{feature_path}: feature payload does not exactly match frame"
                )


def _replace_path(source: Path, target: Path) -> None:
    source.replace(target)


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def publish_provider(staging: Path, target: Path) -> None:
    """Atomically replace a provider, restoring the previous version on failure."""
    backup = target.parent / f".{target.name}.backup"
    backup_exists = backup.exists() or backup.is_symlink()
    target_exists = target.exists() or target.is_symlink()
    if backup_exists and not target_exists:
        _replace_path(backup, target)
    elif backup_exists:
        _remove_path(backup)

    had_target = target.exists() or target.is_symlink()
    if had_target:
        _replace_path(target, backup)

    try:
        _replace_path(staging, target)
    except Exception:
        if had_target:
            _remove_path(target)
            _replace_path(backup, target)
        raise
    else:
        _remove_path(backup)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download five default ETFs into one qlib provider, or use paired "
            "--symbol/--qlib-symbol options for a single ETF"
        )
    )
    parser.add_argument(
        "--symbol",
        default=None,
        help="AkShare ETF code for a single override (requires --qlib-symbol)",
    )
    parser.add_argument(
        "--qlib-symbol",
        default=None,
        help="Qlib name for a single override (requires --symbol)",
    )
    parser.add_argument("--start", default="20100104", help="Start date YYYYMMDD")
    parser.add_argument("--end", default=datetime.now().strftime("%Y%m%d"), help="End date YYYYMMDD")
    parser.add_argument("--adjust", default="qfq", choices=["qfq", "hfq", ""], help="Price adjustment (default: qfq)")
    parser.add_argument("--out-dir", default=str(DATA_DIR), help="Output directory")
    args = parser.parse_args()
    if (args.symbol is None) != (args.qlib_symbol is None):
        parser.error("--symbol and --qlib-symbol must be supplied together")
    return args


def selected_instruments(args: argparse.Namespace) -> tuple[InstrumentSpec, ...]:
    if (args.symbol is None) != (args.qlib_symbol is None):
        raise ValueError("--symbol and --qlib-symbol must be supplied together")
    if args.symbol is not None:
        specs = (InstrumentSpec(args.symbol, args.qlib_symbol, "Custom ETF"),)
    else:
        specs = DEFAULT_INSTRUMENTS
    return validate_instrument_specs(specs)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    specs = selected_instruments(args)
    frames = download_all(specs, args.start, args.end, args.adjust)

    with tempfile.TemporaryDirectory(dir=out_dir.parent) as temporary_directory:
        staging = Path(temporary_directory) / "provider"
        write_provider(frames, staging)
        validate_provider(staging, frames)
        publish_provider(staging, out_dir)

    calendar = build_calendar(frames)
    start_str = calendar[0].strftime("%Y-%m-%d")
    end_str = calendar[-1].strftime("%Y-%m-%d")
    qlib_symbols = list(frames)

    print(f"\n✓ Done — data saved to: {out_dir.resolve()}")
    print("\nQuick verification:")
    print(f"  import qlib")
    print(f"  qlib.init(provider_uri='{out_dir}', region='cn')")
    print(f"  from qlib.data import D")
    print(f"  df = D.features({qlib_symbols!r}, ['$close'], '{start_str}', '{end_str}')")
    print(f"  print(df.head())")


if __name__ == "__main__":
    main()
