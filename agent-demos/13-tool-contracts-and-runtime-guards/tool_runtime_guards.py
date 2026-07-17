from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, Literal


JsonType = Literal["string", "integer", "number", "boolean"]


@dataclass(frozen=True)
class FieldSpec:
    type: JsonType
    required: bool = True
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple[Any, ...] = ()


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, FieldSpec]
    timeout_seconds: float
    max_retries: int
    max_calls_per_run: int


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    name: str
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    attempts: int = 0


@dataclass
class RuntimeState:
    step: int = 0
    max_steps: int = 5
    total_tool_calls: int = 0
    max_total_tool_calls: int = 4
    per_tool_calls: dict[str, int] = field(default_factory=dict)


class ToolRuntime:
    def __init__(self, specs: dict[str, ToolSpec], tools: dict[str, Callable[..., dict[str, Any]]]):
        self.specs = specs
        self.tools = tools

    def run(self, call: ToolCall, state: RuntimeState) -> ToolResult:
        spec = self.specs.get(call.name)
        if spec is None or call.name not in self.tools:
            return ToolResult(name=call.name, ok=False, error="tool is not registered")

        call_count = state.per_tool_calls.get(call.name, 0)
        if call_count >= spec.max_calls_per_run:
            return ToolResult(name=call.name, ok=False, error="per-tool call limit exceeded")
        if state.total_tool_calls >= state.max_total_tool_calls:
            return ToolResult(name=call.name, ok=False, error="total tool call limit exceeded")

        validation_error = validate_args(spec, call.args)
        if validation_error:
            return ToolResult(name=call.name, ok=False, error=validation_error)

        attempts = 0
        last_error = ""
        for attempts in range(1, spec.max_retries + 2):
            state.total_tool_calls += 1
            state.per_tool_calls[call.name] = state.per_tool_calls.get(call.name, 0) + 1
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self.tools[call.name], **call.args)
                    data = future.result(timeout=spec.timeout_seconds)
                return ToolResult(name=call.name, ok=True, data=data, attempts=attempts)
            except TimeoutError:
                last_error = f"tool timed out after {spec.timeout_seconds:.2f}s"
            except TransientToolError as exc:
                last_error = f"transient error: {exc}"
            except Exception as exc:
                return ToolResult(name=call.name, ok=False, error=str(exc), attempts=attempts)

        return ToolResult(name=call.name, ok=False, error=last_error, attempts=attempts)


class TransientToolError(RuntimeError):
    pass


def validate_args(spec: ToolSpec, args: dict[str, Any]) -> str:
    allowed = set(spec.input_schema)
    extra = sorted(set(args) - allowed)
    if extra:
        return f"unexpected args: {extra}"

    for name, field_spec in spec.input_schema.items():
        if field_spec.required and name not in args:
            return f"missing required arg: {name}"
        if name not in args:
            continue

        value = args[name]
        if field_spec.type == "string" and not isinstance(value, str):
            return f"{name} must be string"
        if field_spec.type == "integer" and not isinstance(value, int):
            return f"{name} must be integer"
        if field_spec.type == "number" and not isinstance(value, int | float):
            return f"{name} must be number"
        if field_spec.type == "boolean" and not isinstance(value, bool):
            return f"{name} must be boolean"
        if field_spec.minimum is not None and value < field_spec.minimum:
            return f"{name} must be >= {field_spec.minimum}"
        if field_spec.maximum is not None and value > field_spec.maximum:
            return f"{name} must be <= {field_spec.maximum}"
        if field_spec.choices and value not in field_spec.choices:
            return f"{name} must be one of {field_spec.choices}"

    return ""


class DemoTools:
    def __init__(self) -> None:
        self.quote_failures = 0

    def get_quote(self, symbol: str) -> dict[str, Any]:
        if symbol == "RETRY_ONCE" and self.quote_failures == 0:
            self.quote_failures += 1
            raise TransientToolError("temporary market data gateway failure")
        prices = {"SH510300": 3.91, "RETRY_ONCE": 3.91}
        return {"symbol": symbol, "last_close": prices[symbol]}

    def compute_momentum(self, lookback: int) -> dict[str, Any]:
        return {"factor": f"momentum_{lookback}d", "lookback": lookback}

    def slow_backtest(self, seconds: float) -> dict[str, Any]:
        time.sleep(seconds)
        return {"status": "finished"}


def build_runtime() -> ToolRuntime:
    demo_tools = DemoTools()
    specs = {
        "get_quote": ToolSpec(
            name="get_quote",
            description="Read the latest close for an allowed market symbol.",
            input_schema={"symbol": FieldSpec("string", choices=("SH510300", "RETRY_ONCE"))},
            timeout_seconds=0.5,
            max_retries=1,
            max_calls_per_run=2,
        ),
        "compute_momentum": ToolSpec(
            name="compute_momentum",
            description="Compute a deterministic momentum factor for a bounded lookback window.",
            input_schema={"lookback": FieldSpec("integer", minimum=1, maximum=20)},
            timeout_seconds=0.5,
            max_retries=0,
            max_calls_per_run=1,
        ),
        "slow_backtest": ToolSpec(
            name="slow_backtest",
            description="Demo backtest tool used to show timeout handling.",
            input_schema={"seconds": FieldSpec("number", minimum=0, maximum=5)},
            timeout_seconds=0.1,
            max_retries=0,
            max_calls_per_run=1,
        ),
    }
    tools = {
        "get_quote": demo_tools.get_quote,
        "compute_momentum": demo_tools.compute_momentum,
        "slow_backtest": demo_tools.slow_backtest,
    }
    return ToolRuntime(specs=specs, tools=tools)


def decide_next_action(state: RuntimeState) -> ToolCall:
    if state.step == 0:
        return ToolCall(name="get_quote", args={"symbol": "RETRY_ONCE"})
    if state.step == 1:
        return ToolCall(name="compute_momentum", args={"lookback": 5})
    if state.step == 2:
        return ToolCall(name="slow_backtest", args={"seconds": 0.3})
    return ToolCall(name="compute_momentum", args={"lookback": 999})


def run_agent_loop() -> list[ToolResult]:
    runtime = build_runtime()
    state = RuntimeState()
    results = []

    while state.step < state.max_steps:
        call = decide_next_action(state)
        result = runtime.run(call, state)
        results.append(result)
        state.step += 1
        if not result.ok:
            break
        if state.total_tool_calls >= state.max_total_tool_calls:
            break

    return results


if __name__ == "__main__":
    for result in run_agent_loop():
        print(result)
