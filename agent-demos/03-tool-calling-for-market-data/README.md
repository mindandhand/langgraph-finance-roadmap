# 工具调用：Agent 不能自己编造市场数据

这篇文档讲的是 `market_data_tools.py`。它演示 Agent 和工具之间最小但关键的边界：Agent 可以判断“我需要行情数据”，但行情数据必须由受控工具从真实数据源读取。

本例使用的是仓库里的真实沪深 300 ETF 数据：

```text
../../qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv
```

这份 CSV 由前面的 Qlib 示例准备，字段包括 `symbol`、`date`、`open`、`high`、`low`、`close`、`volume`、`amount`、`factor`。它不是模型记忆，也不是手写价格表，而是一个可以被工具反复读取、审计和替换的数据文件。

## 这个示例想说明什么

脚本的执行路径是：

```text
question
  ↓
decide_tool() 生成 ToolCall
  ↓
run_tool() 只允许执行注册过的工具
  ↓
get_prices() 从真实 CSV 读取行情
  ↓
ToolResult 返回结构化结果
```

重点不是 `decide_tool()` 的规则有多聪明，而是工具调用的边界清楚：

- Agent 决定要不要调用工具。
- 工具负责计算或读取事实。
- 工具返回结构化结果和错误信息。
- Agent 只能解释结果，不能改写结果。

## ToolCall：把意图变成结构化请求

```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
```

一个工具调用至少需要两个字段：

- `name`：调用哪个工具。
- `args`：工具参数。

真实 LLM tool calling 还会有 `tool_call_id`、JSON schema、工具描述和权限配置。但最小模型就是这个：**模型不直接执行动作，而是提出一个可检查的调用请求**。

本例中，`decide_tool()` 会把一个含有 `510300`、`price`、`momentum` 等意图的问题转成：

```python
ToolCall(
    name="get_prices",
    args={
        "symbol": "SH510300",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
    },
)
```

这比让模型直接回答“涨了多少”可靠得多。因为参数可以被检查，工具名可以被白名单限制，执行结果可以被记录。

## ToolResult：工具结果也要有契约

```python
@dataclass(frozen=True)
class ToolResult:
    ok: bool
    data: dict[str, Any]
    error: str | None = None
```

工具结果不应该只是自然语言。量化研究后续还要继续计算因子、评估 IC、生成报告，所以结果必须机器可读。

本例的 `get_prices()` 返回：

- `rows`：读取到多少行。
- `start` / `end`：实际覆盖的日期范围。
- `last_close`：最后一个收盘价摘要。
- `artifact_ref`：源数据文件位置。
- `records`：指定区间内的行情记录。

如果 symbol 不存在，或者日期区间没有数据，工具返回 `ok=False` 和明确错误，而不是让 Agent 猜。

## 工具注册表：Agent 不能自由执行任意能力

```python
TOOLS: dict[str, Callable[..., ToolResult]] = {
    "get_prices": get_prices,
}
```

这是工具白名单。Agent 只能调用这里注册的能力。

在量化系统里，正确做法是把所有允许的能力封装成有限工具，例如：

- `get_prices(symbol, start_date, end_date)`
- `compute_factor(expression, universe, date_range)`
- `evaluate_ic(factor_ref, label_ref)`
- `run_backtest(signal_ref, config)`
- `write_experiment_record(payload)`

不要让模型自由执行任意 Python，不要让模型自己拼 SQL，不要让模型直接生成市场数据。工具越确定，Agent 越可控。

## 为什么这里还不用 LangGraph

本节只有一次决策和一次工具调用：

```text
decide -> run_tool -> print result
```

这类线性流程用普通 Python 更清楚。过早接入图编排会掩盖本节真正要讲的东西：**工具调用的核心不是图，而是契约、白名单和可审计结果**。

后面当流程出现暂停、分支、多角色审查、端到端状态流转时，再使用 LangGraph。

## 实际运行

```bash
python market_data_tools.py
```

你会看到类似输出：

```text
tool_call: ToolCall(name='get_prices', args={...})
tool_result_ok: True
rows: 58
last_close: 3.493
artifact_ref: .../qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv
```

你应该关注两点：

- 工具读取的是真实文件，不是内置玩具价格。
- 输出里包含数据引用和行数，后续可以复查。

## 常见坑

- 让 LLM 直接输出行情、收益率或成交量。
- 工具参数没有 schema，导致模型传入无效字段。
- 工具返回一段自然语言，后续程序无法复用。
- 工具失败后 Agent 不终止，继续编结论。
- 没有保存 `artifact_ref`，之后无法复现数据来源。

## 下一步

本节只读取价格。下一节 `04-deterministic-factor-tools` 会继续：Agent 可以选择“计算动量因子”，但因子值和标签必须由 Pandas 工具确定性计算。
