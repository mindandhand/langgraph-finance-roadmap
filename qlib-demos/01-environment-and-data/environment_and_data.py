import importlib.util
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


def main() -> None:
    has_qlib = importlib.util.find_spec("qlib") is not None
    provider_uri = os.getenv("QLIB_PROVIDER_URI")
    sample = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"])

    print("pyqlib installed:", has_qlib)
    print("QLIB_PROVIDER_URI:", provider_uri or "<not set>")
    print("fallback sample rows:", len(sample))
    print("symbols:", sorted(sample["symbol"].unique().tolist()))
    print("\nNext: run ../02-qlib-data-api/qlib_data_api.py")


if __name__ == "__main__":
    main()
