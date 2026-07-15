import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
JOURNAL = ARTIFACT_DIR / "research_journal.jsonl"


def append_event(event: dict) -> None:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if JOURNAL.exists():
        JOURNAL.unlink()

    append_event({"step": "load_data", "artifact": "prices.csv", "status": "ok"})
    append_event({"step": "compute_factor", "factor": "momentum_3d", "artifact": "factor.csv", "status": "ok"})
    append_event({"step": "evaluate", "metric": "ic", "value": 0.04, "status": "weak"})

    print(JOURNAL)
    print(JOURNAL.read_text(encoding="utf-8"))
