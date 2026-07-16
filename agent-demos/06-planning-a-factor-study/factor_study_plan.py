from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResearchBudget:
    max_factors: int
    max_windows: int
    max_backtests: int
    max_steps: int


@dataclass
class PlanState:
    plan: list[dict[str, Any]]
    budget: ResearchBudget
    current_step: int = 0
    backtests_used: int = 0
    trace: list[str] = field(default_factory=list)
    stopped_reason: str = ""


def make_plan() -> list[dict[str, Any]]:
    return [
        {"step": "define_factor", "factor": "momentum", "windows": [3, 5]},
        {"step": "compute_ic"},
        {"step": "request_review"},
        {"step": "run_simple_backtest"},
        {"step": "write_report"},
    ]


def validate_plan(plan: list[dict[str, Any]], budget: ResearchBudget) -> list[str]:
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
    if len(plan) > budget.max_steps:
        errors.append("too many plan steps")
    return errors


def execute_next(state: PlanState) -> None:
    if state.current_step >= len(state.plan):
        state.stopped_reason = "plan_complete"
        return

    item = state.plan[state.current_step]
    step = item["step"]
    if "backtest" in step:
        if state.backtests_used >= state.budget.max_backtests:
            state.stopped_reason = "backtest_budget_exhausted"
            return
        state.backtests_used += 1

    state.trace.append(step)
    state.current_step += 1


def run_plan(plan: list[dict[str, Any]], budget: ResearchBudget) -> PlanState:
    errors = validate_plan(plan, budget)
    state = PlanState(plan=plan, budget=budget)
    if errors:
        state.stopped_reason = "; ".join(errors)
        return state
    while not state.stopped_reason:
        execute_next(state)
    return state


if __name__ == "__main__":
    budget = ResearchBudget(max_factors=1, max_windows=2, max_backtests=1, max_steps=6)
    state = run_plan(make_plan(), budget)
    print("trace:", " -> ".join(state.trace))
    print("backtests_used:", state.backtests_used)
    print("stopped_reason:", state.stopped_reason)
