from dataclasses import dataclass


@dataclass
class ResearchBudget:
    max_factors: int
    max_windows: int
    max_backtests: int


def make_plan() -> list[dict]:
    return [
        {"step": "define_factor", "factor": "momentum", "windows": [3, 5]},
        {"step": "compute_ic"},
        {"step": "run_simple_backtest"},
        {"step": "write_report"},
    ]


def validate_plan(plan: list[dict], budget: ResearchBudget) -> list[str]:
    errors = []
    factor_steps = [s for s in plan if s["step"] == "define_factor"]
    windows = sum(len(s.get("windows", [])) for s in factor_steps)
    backtests = sum(1 for s in plan if "backtest" in s["step"])
    if len(factor_steps) > budget.max_factors:
        errors.append("too many factors")
    if windows > budget.max_windows:
        errors.append("too many windows")
    if backtests > budget.max_backtests:
        errors.append("too many backtests")
    return errors


if __name__ == "__main__":
    plan = make_plan()
    errors = validate_plan(plan, ResearchBudget(max_factors=1, max_windows=2, max_backtests=1))
    print("plan:", plan)
    print("budget_errors:", errors)
