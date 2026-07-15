from dataclasses import dataclass
from typing import Any, Callable


PRICE_DB = {
    "SH510300": [3.90, 3.94, 3.98, 3.92, 4.02],
}


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


def get_prices(symbol: str) -> dict[str, Any]:
    return {"symbol": symbol, "prices": PRICE_DB[symbol]}


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_prices": get_prices,
}


def decide_tool(question: str) -> ToolCall:
    if "price" in question.lower() or "momentum" in question.lower():
        return ToolCall(name="get_prices", args={"symbol": "SH510300"})
    raise ValueError("No allowed tool matches the question")


def run_tool(call: ToolCall) -> dict[str, Any]:
    return TOOLS[call.name](**call.args)


if __name__ == "__main__":
    question = "Get price data for SH510300 before calculating momentum."
    call = decide_tool(question)
    result = run_tool(call)
    print("tool_call:", call)
    print("tool_result:", result)
