CLAIM = {
    "factor": "momentum_3d",
    "mean_ic": 0.04,
    "backtest_done": False,
    "cost_checked": False,
    "sample_days": 20,
}


def researcher(claim: dict) -> str:
    return f"Researcher: {claim['factor']} has positive mean IC={claim['mean_ic']:.2f}."


def reviewer(claim: dict) -> list[str]:
    findings = []
    if claim["sample_days"] < 60:
        findings.append("Reviewer: sample is too short for a stable conclusion.")
    if not claim["backtest_done"]:
        findings.append("Reviewer: no portfolio backtest is attached.")
    return findings


def red_team(claim: dict) -> list[str]:
    findings = []
    if not claim["cost_checked"]:
        findings.append("Red-Team: high-turnover momentum may fail after costs.")
    return findings


if __name__ == "__main__":
    print(researcher(CLAIM))
    for item in reviewer(CLAIM):
        print(item)
    for item in red_team(CLAIM):
        print(item)
    print("Decision: requires more evidence")
