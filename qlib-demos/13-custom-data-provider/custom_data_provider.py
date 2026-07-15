from io import StringIO
from pathlib import Path

import pandas as pd


RAW_VENDOR_DATA = """symbol,date,open,high,low,close,volume,factor,pe
SH600000,2024-01-02,9.90,10.08,9.86,10.00,1200000,1.0,5.1
SH600000,2024-01-03,10.02,10.15,9.98,10.10,1180000,1.0,5.2
SH600000,2024-01-04,10.12,10.35,10.08,10.30,1215000,1.0,5.3
SZ000001,2024-01-02,11.95,12.08,11.88,12.00,2200000,1.0,6.8
SZ000001,2024-01-03,12.02,12.06,11.86,11.90,2180000,1.0,6.7
SZ000001,2024-01-04,11.92,12.15,11.90,12.10,2250000,1.0,6.9
"""


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts" / "custom_provider_plan"
REQUIRED_COLUMNS = {"symbol", "date", "open", "high", "low", "close", "volume", "factor"}


def validate_raw_data(frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        errors.append(f"missing required columns: {missing}")
    if frame["date"].isna().any():
        errors.append("date contains null or unparsable values")
    price_cols = ["open", "high", "low", "close"]
    if (frame[price_cols] <= 0).any().any():
        errors.append("price columns must be positive")
    if (frame["volume"] < 0).any():
        errors.append("volume must be non-negative")
    duplicated = frame.duplicated(["symbol", "date"]).sum()
    if duplicated:
        errors.append(f"duplicated symbol/date rows: {duplicated}")
    return errors


def main() -> None:
    frame = pd.read_csv(StringIO(RAW_VENDOR_DATA), parse_dates=["date"])
    frame = frame.sort_values(["symbol", "date"]).reset_index(drop=True)
    errors = validate_raw_data(frame)
    if errors:
        print("Data is not ready for Qlib conversion:")
        for error in errors:
            print("-", error)
        return

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    calendar = frame["date"].drop_duplicates().sort_values().dt.strftime("%Y-%m-%d")
    instruments = frame.groupby("symbol")["date"].agg(["min", "max"]).reset_index()
    instruments["min"] = instruments["min"].dt.strftime("%Y-%m-%d")
    instruments["max"] = instruments["max"].dt.strftime("%Y-%m-%d")

    frame.to_csv(ARTIFACT_DIR / "normalized_sample.csv", index=False)
    calendar.to_csv(ARTIFACT_DIR / "calendar.txt", index=False, header=False)
    instruments.to_csv(ARTIFACT_DIR / "instruments.txt", index=False, header=False)

    command = (
        "python scripts/dump_bin.py dump_all "
        "--data_path ~/.qlib/my_data "
        "--qlib_dir ~/.qlib/qlib_data/my_data "
        "--include_fields open,close,high,low,volume,factor,pe "
        "--symbol_field_name symbol "
        "--date_field_name date "
        "--file_suffix .csv"
    )
    (ARTIFACT_DIR / "dump_bin_command.txt").write_text(command + "\n", encoding="utf-8")

    print("Raw data passed basic checks.")
    print("symbols:", sorted(frame["symbol"].unique().tolist()))
    print("calendar days:", len(calendar))
    print("artifacts:", ARTIFACT_DIR)
    print("suggested dump command:")
    print(command)


if __name__ == "__main__":
    main()
