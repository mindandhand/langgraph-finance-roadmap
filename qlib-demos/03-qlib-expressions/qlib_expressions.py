from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qlib_demo_common import load_features, print_context, with_datetime_instrument_index


def main() -> None:
    fields = [
        "$close",
        "Ref($close, 1)",
        "$close / Ref($close, 20) - 1",
        "Mean($close, 20) / $close",
        "Std($close / Ref($close, 1) - 1, 20)",
        "Mean($volume, 5) / Mean($volume, 20)",
        "Rank($close / Ref($close, 20) - 1, 20)",
    ]
    names = [
        "close",
        "prev_close",
        "mom20",
        "ma20_to_close",
        "vol20",
        "volume_ratio_5_20",
        "rolling_mom20_rank",
    ]

    print_context("Qlib expression engine")
    data = with_datetime_instrument_index(load_features(fields, names))
    print(data.dropna().head(20).to_string())


if __name__ == "__main__":
    main()
