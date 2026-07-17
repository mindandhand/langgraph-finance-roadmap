from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qlib_demo_common import load_features, print_context, with_datetime_instrument_index


def main() -> None:
    fields = ["$open", "$high", "$low", "$close", "$volume"]
    names = ["open", "high", "low", "close", "volume"]

    print_context("Qlib Data API")
    data = with_datetime_instrument_index(load_features(fields, names))
    print(data.head(20).to_string())
    print("index names:", data.index.names)
    print("columns:", list(data.columns))


if __name__ == "__main__":
    main()
