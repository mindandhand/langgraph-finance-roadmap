from dataclasses import dataclass, field


PRICES = [10.0, 10.2, 10.5, 10.4, 10.8]


@dataclass
class ResearchState:
    question: str
    prices: list[float] = field(default_factory=list)
    momentum: float | None = None
    answer: str = ""
    done: bool = False
    trace: list[str] = field(default_factory=list)


def decide(state: ResearchState) -> str:
    if not state.prices:
        return "load_prices"
    if state.momentum is None:
        return "compute_momentum"
    if not state.answer:
        return "write_answer"
    return "finish"


def act(action: str, state: ResearchState) -> None:
    state.trace.append(action)
    if action == "load_prices":
        state.prices = PRICES.copy()
    elif action == "compute_momentum":
        state.momentum = state.prices[-1] / state.prices[0] - 1
    elif action == "write_answer":
        state.answer = f"5-day momentum is {state.momentum:.2%}."
    elif action == "finish":
        state.done = True
    else:
        raise ValueError(f"unknown action: {action}")


def run_agent(question: str, max_steps: int = 8) -> ResearchState:
    state = ResearchState(question=question)
    for _ in range(max_steps):
        if state.done:
            break
        action = decide(state)
        act(action, state)
    return state


if __name__ == "__main__":
    result = run_agent("Calculate simple momentum for this ETF.")
    print("trace:", " -> ".join(result.trace))
    print("answer:", result.answer)
