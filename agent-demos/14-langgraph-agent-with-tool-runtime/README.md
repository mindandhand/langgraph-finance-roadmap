# LangGraph Agent + ToolRuntime：把工作流和工具保护接起来

这篇文档讲的是 `langgraph_agent_with_tool_runtime.py`。第 12 节已经给出端到端量化研究 Agent，第 13 节已经给出工具契约和运行时保护。本节把两者合在一起：

```text
LangGraph 负责状态和路由
ToolRuntime 负责工具描述、参数校验、超时、重试和调用次数限制
```

这就是一个更接近工程化 Agent 的形态。节点不再直接调用 Pandas 函数，而是构造 `ToolCall`，交给受控运行时执行。

## 这个示例想说明什么

第 12 节的节点大致是：

```python
def compute_factor(state):
    data = pd.read_csv(...)
    ...
```

本节改成：

```python
call = ToolCall(name="compute_factor", args={...})
result = ToolRuntime.run(call, runtime_state)
```

也就是说：

- 图节点负责把 state 转成工具调用。
- ToolRuntime 检查这个调用是否合法。
- 工具执行后返回 `ToolResult`。
- 节点把结果写回 state。
- 失败时图进入报告节点，不继续编造后续结果。

## 工作流结构

```text
define_candidate_factor
  ↓
compute_factor     通过 ToolRuntime 执行
  ↓
evaluate_factor    通过 ToolRuntime 执行
  ↓
auto_review
  ↓
run_backtest       通过 ToolRuntime 执行
  ↓
write_report
```

和第 12 节相比，图结构类似，但工具执行边界更严格。

## ToolSpec：每个研究工具都有契约

本节为三个工具定义契约：

- `compute_factor`
- `evaluate_factor`
- `run_backtest`

例如 `compute_factor`：

```python
"compute_factor": ToolSpec(
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
)
```

这里的关键是：Agent 即使想传入其他 symbol、过大的 lookback 或重复调用因子计算，也会被运行时拦住。

## ResearchState 里多了运行时状态

```python
runtime_state: dict[str, Any]
tool_records: list[dict[str, Any]]
error: str
```

新增字段的作用：

- `runtime_state`：记录总工具调用次数、最大调用次数、每个工具调用次数。
- `tool_records`：记录每次 `ToolCall` 和 `ToolResult`。
- `error`：记录工具失败原因。

这让最终报告不只包含 metrics，还包含工具调用轨迹。

## run_guarded_tool：节点和工具运行时的接缝

```python
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
```

这段代码是本节最重要的部分。它把 LangGraph 的 state 世界和 ToolRuntime 的执行世界连接起来。

## 失败路径：工具失败后不继续跑

如果工具返回 `ok=False`，节点会写入：

```python
{
    "error": result.error,
    "trace": [..., "compute_factor:failed"],
    "status": "failed",
}
```

然后条件边把图路由到 `write_report`。

这比在异常发生后继续执行后续节点更可靠。Agent 可以失败，但必须可解释地失败。

## 自动审查仍然只是占位

本节保留了第 12 节的 `auto_review()`，但增加了一个预算条件：

```python
enough_budget = total_tool_calls < max_total_tool_calls
```

它仍然不是生产审批。真实系统应继续接入：

- 第 8 节的 `interrupt()`。
- 第 10 节的 Reviewer / Red-Team。
- 第 11 节的实验记录器。

本节重点是工具运行时保护，不把所有机制一次性塞进来。

## 实际运行

```bash
python langgraph_agent_with_tool_runtime.py
```

你会看到类似输出：

```text
status: reported
report_ref: .../artifacts/report.json
tool_calls: 3
metrics: {
  "rows": 605.0,
  "ic": 0.0284,
  "rank_ic": -0.0254,
  "backtest_rows": 605.0,
  "total_net_return": 0.4394,
  "avg_turnover": 0.00165
}
trace: define_candidate_factor -> compute_factor -> evaluate_factor -> review:approve_backtest -> run_backtest -> write_report
```

生成的报告会包含：

- `metrics`
- `runtime_state`
- `tool_records`
- `artifact_refs`
- `error`
- `trace`

## 和第 12、13 节的关系

第 12 节回答：

```text
完整量化研究 Agent 的图结构长什么样？
```

第 13 节回答：

```text
工具调用如何加描述、schema、超时、重试和调用预算？
```

第 14 节回答：

```text
如何把图工作流和工具运行时组合起来？
```

组合后的结构是：

```text
LangGraph node
  ↓
ToolCall
  ↓
ToolRuntime.validate_args()
  ↓
ToolRuntime.run(timeout / retry / call budget)
  ↓
ToolResult
  ↓
write result back to ResearchState
```

## 常见坑

- LangGraph 节点直接执行所有逻辑，导致工具边界消失。
- ToolRuntime 有校验，但没有把失败写回 state。
- 只记录最终 metrics，不记录工具调用参数和错误。
- 工具失败后继续进入回测或报告乐观结论。
- 只限制图步骤，不限制工具调用次数。

## 下一步

下一步可以把本节继续拆成生产化组件：

- 把 `ToolRuntime` 提到共享模块，避免每个示例复制。
- 把 `auto_review()` 换成第 8 节 `interrupt()`。
- 把第 10 节 Reviewer / Red-Team 接到 `auto_review` 前。
- 把第 11 节 recorder 接到 `tool_records`。
- 把 Pandas 工具替换成 Qlib 表达式和 Dataset 工具。
