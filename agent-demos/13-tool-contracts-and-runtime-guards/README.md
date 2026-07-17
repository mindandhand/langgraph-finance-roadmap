# 工具契约和运行时保护：让 Agent 可控地调用工具

这篇文档讲的是 `tool_runtime_guards.py`。前面的示例已经说明 Agent 应该通过工具读取行情、计算因子、评估指标和执行回测。本节补上工程化 Agent 必须有的一层：**工具契约和运行时保护**。

没有这一层，Agent 很容易出问题：

- 工具描述太模糊，模型不知道什么时候该调用。
- 参数没有校验，模型传入无效字段或危险范围。
- 工具卡住，Agent 一直等待。
- 工具临时失败，Agent 直接放弃或盲目重试。
- Agent 陷入循环，反复调用同一个工具。

本节不接入 LLM，也不接入 LangGraph，目的是把运行时边界讲清楚。

## 这个示例想说明什么

脚本把工具调用拆成四层：

```text
ToolSpec       描述工具能做什么、需要什么参数、有什么运行限制
  ↓
validate_args 参数校验
  ↓
ToolRuntime   执行超时、重试、调用次数限制
  ↓
Agent loop    受 max_steps 和 tool budget 约束
```

Agent 可以决定下一步调用什么工具，但工具运行时必须独立检查这个调用是否允许执行。

## ToolSpec：工具描述不是给人看的注释

```python
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, FieldSpec]
    timeout_seconds: float
    max_retries: int
    max_calls_per_run: int
```

一个合格的工具描述至少要回答：

- 这个工具做什么。
- 什么时候应该调用。
- 参数有哪些。
- 参数范围是什么。
- 超时时间是多少。
- 失败后最多重试几次。
- 单次运行最多调用几次。

对 LLM 来说，`description` 会影响它是否选择这个工具。对执行系统来说，`input_schema`、`timeout_seconds`、`max_retries` 和 `max_calls_per_run` 才是真正的安全边界。

## 工具描述应该怎么写

坏的工具描述：

```text
get_data: get data
```

这个描述太泛，模型不知道它能读什么数据、什么时候该用、返回什么。

更好的工具描述：

```text
Read the latest close for an allowed market symbol.
```

更完整的工具契约还应该配合 schema：

```python
"get_quote": ToolSpec(
    name="get_quote",
    description="Read the latest close for an allowed market symbol.",
    input_schema={
        "symbol": FieldSpec("string", choices=("SH510300", "RETRY_ONCE")),
    },
    timeout_seconds=0.5,
    max_retries=1,
    max_calls_per_run=2,
)
```

这样模型即使想调用未授权 symbol，也会被运行时拦住。

## 参数校验：不要相信模型传参

本例的参数校验检查：

- 是否有未知参数。
- 必填参数是否存在。
- 类型是否正确。
- 数值是否在范围内。
- 字符串是否在允许列表内。

例如 `compute_momentum` 的 schema 是：

```python
{"lookback": FieldSpec("integer", minimum=1, maximum=20)}
```

如果 Agent 传入：

```python
ToolCall(name="compute_momentum", args={"lookback": 999})
```

运行时会拒绝：

```text
lookback must be <= 20
```

这比把“不要传太大的 lookback”写在 prompt 里可靠。

## 超时：工具卡住时必须返回控制权

```python
future.result(timeout=spec.timeout_seconds)
```

本例的 `slow_backtest` 故意 sleep 超过限制：

```python
"slow_backtest": ToolSpec(
    timeout_seconds=0.1,
    max_retries=0,
)
```

运行时会返回：

```text
tool timed out after 0.10s
```

真实系统里，超时后通常还要做两件事：

- 记录失败原因和工具参数。
- 决定是停止、降级、请求人工，还是稍后重试。

不要让 Agent 在没有上限的情况下等待工具。

## 重试：只重试临时错误

不是所有失败都应该重试。

可以重试：

- 临时网络失败。
- 数据源短暂不可用。
- 429 / 503 这类明确可恢复错误。

不应该重试：

- 参数校验失败。
- 未注册工具。
- 权限不足。
- 数据不存在。
- 业务规则拒绝。

本例中，`get_quote("RETRY_ONCE")` 第一次会抛出 `TransientToolError`，第二次成功。因为 `max_retries=1`，运行时最多尝试两次。

## 调用次数限制：防止工具被反复打爆

本例有两层调用限制：

```python
max_total_tool_calls: int = 4
max_calls_per_run: int = 2
```

含义不同：

- `max_total_tool_calls`：整个 Agent run 最多调用多少次工具。
- `max_calls_per_run`：某个具体工具最多被调用多少次。

这能防止 Agent 在一个错误状态里反复调用 `get_quote`、`run_backtest` 或 `search_notes`。

量化研究中特别要限制回测工具。因为每多看一次回测结果，就多一次根据历史表现调参的机会。

## 防止 Agent 无限循环

本例的 `RuntimeState` 还有：

```python
step: int = 0
max_steps: int = 5
```

主循环是：

```python
while state.step < state.max_steps:
    call = decide_next_action(state)
    result = runtime.run(call, state)
    ...
```

这和第 1 节的 `max_steps` 是同一个原则：Agent 必须有业务停止条件，也必须有安全停止条件。

常见的停止条件包括：

- 任务完成。
- 工具失败且不可恢复。
- 达到最大步骤数。
- 达到最大工具调用次数。
- 达到研究预算。
- 人工拒绝继续。

## 实际运行

```bash
python tool_runtime_guards.py
```

你会看到类似输出：

```text
ToolResult(name='get_quote', ok=True, data={'symbol': 'RETRY_ONCE', 'last_close': 3.91}, attempts=2)
ToolResult(name='compute_momentum', ok=True, data={'factor': 'momentum_5d', 'lookback': 5}, attempts=1)
ToolResult(name='slow_backtest', ok=False, error='tool timed out after 0.10s', attempts=1)
```

第三步失败后循环停止。Agent 不会继续编造回测结果，也不会无限重试。

## 和前面章节的关系

- 第 1 节讲 Agent 基本循环。
- 第 3 节讲工具调用和工具白名单。
- 第 6 节讲研究预算。
- 第 8 节讲人工审批。
- 第 11 节讲实验记录。
- 本节讲工具运行时保护。

这些机制应该同时存在。只靠 prompt 约束 Agent 不够，必须把约束写进运行时。

## 常见坑

- 工具描述过短，导致模型乱用工具。
- 参数校验只在 prompt 里，没有运行时代码。
- 所有错误都重试，导致无效请求被反复执行。
- 工具没有超时，Agent 被长任务卡住。
- 只限制 Agent 步数，不限制工具调用次数。
- 回测工具没有预算，导致参数挖掘。

## 下一步

完整系统可以把本节的 `ToolRuntime` 接到 LangGraph 节点里。图负责状态和路由，工具运行时负责参数、超时、重试和调用预算。两者结合，才是可控的工程化 Agent。
