from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "qlib-demos"
    / "qlib-data"
    / "hs300_etf_510300"
    / "csv"
    / "SH510300.csv"
)


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    name: str
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""


def get_prices(symbol: str, start_date: str, end_date: str) -> ToolResult:
    try:
        frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
        selected = frame[
            (frame["symbol"] == symbol)
            & frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
        ].copy()
        if selected.empty:
            return ToolResult(
                name="get_prices",
                ok=False,
                error=f"no rows for {symbol} from {start_date} to {end_date}",
            )
        return ToolResult(
            name="get_prices",
            ok=True,
            data={
                "symbol": symbol,
                "rows": len(selected),
                "start": selected["date"].min().strftime("%Y-%m-%d"),
                "end": selected["date"].max().strftime("%Y-%m-%d"),
                "artifact_ref": str(DATA_PATH),
                "last_close": float(selected.iloc[-1]["close"]),
            },
        )
    except Exception as exc:
        return ToolResult(name="get_prices", ok=False, error=str(exc))


TOOLS: dict[str, Callable[..., ToolResult]] = {
    "get_prices": get_prices,
}


def decide_tool(question: str) -> ToolCall:
    lowered = question.lower()
    if "price" in lowered or "momentum" in lowered or "510300" in lowered:
        return ToolCall(
            name="get_prices",
            args={
                "symbol": "SH510300",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
            },
        )
    raise ValueError("No allowed tool matches the question")


def run_tool(call: ToolCall) -> ToolResult:
    tool = TOOLS.get(call.name)
    if tool is None:
        return ToolResult(name=call.name, ok=False, error="tool is not registered")
    return tool(**call.args)


if __name__ == "__main__":
    question = "Get price data for SH510300 before calculating momentum."
    call = decide_tool(question)
    result = run_tool(call)
    print("tool_call:", call)
    print("tool_result:", result)
