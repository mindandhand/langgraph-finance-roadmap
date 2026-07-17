import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "06-factor-evaluation"))

from factor_evaluation import DEFAULT_FACTOR, DEFAULT_LABEL, evaluate_factor
from qlib_demo_common import init_qlib, print_context


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a Qlib factor expression deterministically.")
    parser.add_argument("--expression", default=DEFAULT_FACTOR, help="Qlib factor expression.")
    parser.add_argument("--label", default=DEFAULT_LABEL, help="Qlib label expression.")
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_qlib()
    metrics = evaluate_factor(args.expression, args.label)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print_context("Qlib factor evaluation service")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
