from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, TypedDict

import pandas as pd
from langgraph.graph import END, START, StateGraph


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "qlib-demos"
    / "qlib-data"
    / "hs300_etf_510300"
    / "csv"
    / "SH510300.csv"
)
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

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

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
            "attempts": self.attempts,
        }


@dataclass
class RuntimeState:
    total_tool_calls: int = 0
    max_total_tool_calls: int = 6
    per_tool_calls: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> RuntimeState:
        return cls(
            total_tool_calls=int(raw.get("total_tool_calls", 0)),
            max_total_tool_calls=int(raw.get("max_total_tool_calls", 6)),
            per_tool_calls=dict(raw.get("per_tool_calls", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_tool_calls": self.total_tool_calls,
            "max_total_tool_calls": self.max_total_tool_calls,
            "per_tool_calls": self.per_tool_calls,
        }


class ToolRuntime:
    def __init__(self, specs: dict[str, ToolSpec], tools: dict[str, Callable[..., dict[str, Any]]]):
        self.specs = specs
        self.tools = tools

    def run(self, call: ToolCall, state: RuntimeState) -> ToolResult:
        spec = self.specs.get(call.name)
        if spec is None or call.name not in self.tools:
            return ToolResult(name=call.name, ok=False, error="tool is not registered")

        if state.per_tool_calls.get(call.name, 0) >= spec.max_calls_per_run:
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
            except Exception as exc:
                return ToolResult(name=call.name, ok=False, error=str(exc), attempts=attempts)

        return ToolResult(name=call.name, ok=False, error=last_error, attempts=attempts)


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


def compute_factor_tool(
    symbol: str,
    start_date: str,
    end_date: str,
    lookback: int,
    label_horizon: int,
) -> dict[str, Any]:
    frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
    data = frame[
        (frame["symbol"] == symbol)
        & frame["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    ].sort_values(["symbol", "date"]).copy()
    if data.empty:
        raise ValueError(f"no rows for {symbol} from {start_date} to {end_date}")

    by_symbol = data.groupby("symbol")
    data["factor"] = data["close"] / by_symbol["close"].shift(lookback) - 1
    data["label"] = by_symbol["close"].shift(-label_horizon) / data["close"] - 1
    data = data.dropna(subset=["factor", "label"]).reset_index(drop=True)
    if data.empty:
        raise ValueError("factor data is empty after lookback and label alignment")

    ARTIFACT_DIR.mkdir(exist_ok=True)
    factor_ref = ARTIFACT_DIR / "factor_data.csv"
    data.to_csv(factor_ref, index=False)
    return {
        "factor_ref": str(factor_ref),
        "rows": len(data),
        "start": data["date"].min().strftime("%Y-%m-%d"),
        "end": data["date"].max().strftime("%Y-%m-%d"),
    }


def evaluate_factor_tool(factor_ref: str) -> dict[str, Any]:
    data = pd.read_csv(factor_ref, parse_dates=["date"])
    return {
        "rows": float(len(data)),
        "ic": float(data["factor"].corr(data["label"])),
        "rank_ic": float(data["factor"].corr(data["label"], method="spearman")),
        "factor_mean": float(data["factor"].mean()),
        "label_mean": float(data["label"].mean()),
    }


def run_backtest_tool(factor_ref: str, cost_bps: float) -> dict[str, Any]:
    data = pd.read_csv(factor_ref, parse_dates=["date"])
    picks = data.sort_values(["date", "factor"], ascending=[True, False]).groupby("date").head(1)
    picks = picks.sort_values("date").reset_index(drop=True)
    picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
    picks.loc[0, "turnover"] = 1.0
    picks["net_return"] = picks["label"] - picks["turnover"] * cost_bps / 10000
    picks["equity"] = (1 + picks["net_return"]).cumprod()

    backtest_ref = ARTIFACT_DIR / "backtest.csv"
    picks.to_csv(backtest_ref, index=False)
    return {
        "backtest_ref": str(backtest_ref),
        "backtest_rows": float(len(picks)),
        "total_net_return": float(picks["equity"].iloc[-1] - 1),
        "avg_turnover": float(picks["turnover"].mean()),
    }


def build_runtime() -> ToolRuntime:
    specs = {
        "compute_factor": ToolSpec(
            name="compute_factor",
            description="Compute bounded momentum factor data from the local SH510300 price file.",
            input_schema={
                "symbol": FieldSpec("string", choices=("SH510300",)),
                "start_date": FieldSpec("string"),
                "end_date": FieldSpec("string"),
                "lookback": FieldSpec("integer", minimum=1, maximum=60),
                "label_horizon": FieldSpec("integer", minimum=1, maximum=5),
            },
            timeout_seconds=3.0,
            max_retries=0,
            max_calls_per_run=1,
        ),
        "evaluate_factor": ToolSpec(
            name="evaluate_factor",
            description="Evaluate IC and RankIC from a factor artifact produced by compute_factor.",
            input_schema={"factor_ref": FieldSpec("string")},
            timeout_seconds=5.0,
            max_retries=0,
            max_calls_per_run=1,
        ),
        "run_backtest": ToolSpec(
            name="run_backtest",
            description="Run a minimal top-1 backtest from a factor artifact with bounded cost.",
            input_schema={
                "factor_ref": FieldSpec("string"),
                "cost_bps": FieldSpec("number", minimum=0, maximum=100),
            },
            timeout_seconds=5.0,
            max_retries=0,
            max_calls_per_run=1,
        ),
    }
    tools = {
        "compute_factor": compute_factor_tool,
        "evaluate_factor": evaluate_factor_tool,
        "run_backtest": run_backtest_tool,
    }
    return ToolRuntime(specs=specs, tools=tools)


RUNTIME = build_runtime()


class ResearchState(TypedDict):
    experiment_id: str
    symbol: str
    start_date: str
    end_date: str
    lookback: int
    label_horizon: int
    cost_bps: float
    factor_ref: str
    backtest_ref: str
    metrics: dict[str, float]
    runtime_state: dict[str, Any]
    tool_records: list[dict[str, Any]]
    review_decision: str
    report_ref: str
    error: str
    trace: list[str]
    status: str


def run_guarded_tool(state: ResearchState, call: ToolCall) -> tuple[ToolResult, dict[str, Any]]:
    runtime_state = RuntimeState.from_dict(state["runtime_state"])
    result = RUNTIME.run(call, runtime_state)
    record = {
        "call": {"name": call.name, "args": call.args},
        "result": result.as_record(),
    }
    return result, {
        "runtime_state": runtime_state.to_dict(),
        "tool_records": [*state["tool_records"], record],
    }


def define_candidate_factor(state: ResearchState) -> dict:
    return {
        "trace": [*state["trace"], "define_candidate_factor"],
        "status": "factor_defined",
    }


def compute_factor(state: ResearchState) -> dict:
    call = ToolCall(
        name="compute_factor",
        args={
            "symbol": state["symbol"],
            "start_date": state["start_date"],
            "end_date": state["end_date"],
            "lookback": state["lookback"],
            "label_horizon": state["label_horizon"],
        },
    )
    result, updates = run_guarded_tool(state, call)
    if not result.ok:
        return {
            **updates,
            "error": result.error,
            "trace": [*state["trace"], "compute_factor:failed"],
            "status": "failed",
        }
    return {
        **updates,
        "factor_ref": result.data["factor_ref"],
        "trace": [*state["trace"], "compute_factor"],
        "status": "factor_computed",
    }


def evaluate_factor(state: ResearchState) -> dict:
    call = ToolCall(name="evaluate_factor", args={"factor_ref": state["factor_ref"]})
    result, updates = run_guarded_tool(state, call)
    if not result.ok:
        return {
            **updates,
            "error": result.error,
            "trace": [*state["trace"], "evaluate_factor:failed"],
            "status": "failed",
        }
    return {
        **updates,
        "metrics": result.data,
        "trace": [*state["trace"], "evaluate_factor"],
        "status": "evaluated",
    }


def auto_review(state: ResearchState) -> dict:
    metrics = state["metrics"]
    enough_rows = metrics.get("rows", 0) >= 120
    finite_ic = metrics.get("ic") == metrics.get("ic")
    enough_budget = state["runtime_state"]["total_tool_calls"] < state["runtime_state"]["max_total_tool_calls"]
    decision = "approve_backtest" if enough_rows and finite_ic and enough_budget else "reject_backtest"
    return {
        "review_decision": decision,
        "trace": [*state["trace"], f"review:{decision}"],
        "status": "reviewed",
    }


def run_backtest(state: ResearchState) -> dict:
    call = ToolCall(
        name="run_backtest",
        args={"factor_ref": state["factor_ref"], "cost_bps": state["cost_bps"]},
    )
    result, updates = run_guarded_tool(state, call)
    if not result.ok:
        return {
            **updates,
            "error": result.error,
            "trace": [*state["trace"], "run_backtest:failed"],
            "status": "failed",
        }
    return {
        **updates,
        "backtest_ref": result.data["backtest_ref"],
        "metrics": {**state["metrics"], **{k: v for k, v in result.data.items() if k != "backtest_ref"}},
        "trace": [*state["trace"], "run_backtest"],
        "status": "backtested",
    }


def route_after_compute(state: ResearchState) -> str:
    return "write_report" if state["status"] == "failed" else "evaluate_factor"


def route_after_evaluate(state: ResearchState) -> str:
    return "write_report" if state["status"] == "failed" else "auto_review"


def route_after_review(state: ResearchState) -> str:
    return "run_backtest" if state["review_decision"] == "approve_backtest" else "write_report"


def route_after_backtest(state: ResearchState) -> str:
    return "write_report"


def write_report(state: ResearchState) -> dict:
    trace = [*state["trace"], "write_report"]
    report = {
        "experiment_id": state["experiment_id"],
        "symbol": state["symbol"],
        "candidate_factor": f"{state['lookback']}-day momentum",
        "period": {"start": state["start_date"], "end": state["end_date"]},
        "metrics": state["metrics"],
        "runtime_state": state["runtime_state"],
        "tool_records": state["tool_records"],
        "artifact_refs": {
            "factor": state["factor_ref"],
            "backtest": state["backtest_ref"],
        },
        "decision": "requires_human_review_before_real_use",
        "error": state["error"],
        "trace": trace,
    }
    ARTIFACT_DIR.mkdir(exist_ok=True)
    report_ref = ARTIFACT_DIR / "report.json"
    report_ref.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {
        "report_ref": str(report_ref),
        "trace": trace,
        "status": "reported" if not state["error"] else "failed_reported",
    }


builder = StateGraph(ResearchState)
builder.add_node("define_candidate_factor", define_candidate_factor)
builder.add_node("compute_factor", compute_factor)
builder.add_node("evaluate_factor", evaluate_factor)
builder.add_node("auto_review", auto_review)
builder.add_node("run_backtest", run_backtest)
builder.add_node("write_report", write_report)
builder.add_edge(START, "define_candidate_factor")
builder.add_edge("define_candidate_factor", "compute_factor")
builder.add_conditional_edges("compute_factor", route_after_compute)
builder.add_conditional_edges("evaluate_factor", route_after_evaluate)
builder.add_conditional_edges("auto_review", route_after_review)
builder.add_conditional_edges("run_backtest", route_after_backtest)
builder.add_edge("write_report", END)
graph = builder.compile()


def initial_state() -> ResearchState:
    return {
        "experiment_id": "agent-runtime-001",
        "symbol": "SH510300",
        "start_date": "2024-01-01",
        "end_date": "2026-07-14",
        "lookback": 5,
        "label_horizon": 1,
        "cost_bps": 10.0,
        "factor_ref": "",
        "backtest_ref": "",
        "metrics": {},
        "runtime_state": RuntimeState().to_dict(),
        "tool_records": [],
        "review_decision": "",
        "report_ref": "",
        "error": "",
        "trace": [],
        "status": "created",
    }


if __name__ == "__main__":
    result = graph.invoke(initial_state())
    print("status:", result["status"])
    print("report_ref:", result["report_ref"])
    print("tool_calls:", result["runtime_state"]["total_tool_calls"])
    print("metrics:", json.dumps(result["metrics"], indent=2))
    print("trace:", " -> ".join(result["trace"]))
