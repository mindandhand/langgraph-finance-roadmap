import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def main() -> None:
    record = {
        "experiment_id": "agent-exp-001",
        "objective": "Evaluate 3-day momentum on toy ETF data",
        "plan": ["load_prices", "compute_factor", "evaluate_ic", "request_review"],
        "tool_calls": [
            {"tool": "get_prices", "args": {"symbol": "SH510300"}},
            {"tool": "compute_momentum", "args": {"lookback": 3}},
        ],
        "metrics": {"mean_ic": 0.04, "mean_rank_ic": 0.03},
        "decision": "requires_more_evidence",
    }
    ARTIFACT_DIR.mkdir(exist_ok=True)
    path = ARTIFACT_DIR / "experiment.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(path)
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
