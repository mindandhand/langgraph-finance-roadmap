# 完整量化研究 Agent：受约束的 LangGraph 工作流

这篇文档讲的是 `quant_research_agent.py`。它把前面 11 节压缩成一个最小端到端流程：

```text
define_candidate_factor
  ↓
compute_factor
  ↓
evaluate_factor
  ↓
auto_review
  ↓
run_backtest 或 write_report
  ↓
write_report
```

这个 Agent 仍然很小，但它已经体现了量化研究 Agent 的核心原则：**Agent 组织流程，工具计算事实，审批控制敏感步骤，记录保留证据**。

## 为什么这里必须用图

端到端研究不是一个线性脚本就能表达清楚的：

- 有共享 state。
- 有 artifact 在节点之间传递。
- 有评估指标决定后续分支。
- 有回测前审查。
- 有最终报告和 trace。

LangGraph 让这些关系显式化。每个节点只负责一个职责，条件边只负责路由，最终 state 能说明整次实验走过什么路径。

## 真实数据输入

脚本读取仓库里的沪深 300 ETF 数据：

```text
../../qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv
```

默认运行配置是：

- `symbol`: `SH510300`
- `start_date`: `2024-01-01`
- `end_date`: `2026-07-14`
- `lookback`: `5`
- `label_horizon`: `1`

这仍然不是完整多股票研究，但已经不是手写 toy sample。它可以演示真实文件读取、真实日期过滤、真实 artifact 输出和可复现指标。

## ResearchState：端到端流程的唯一事实载体

```python
class ResearchState(TypedDict):
    experiment_id: str
    symbol: str
    start_date: str
    end_date: str
    lookback: int
    label_horizon: int
    factor_ref: str
    metrics: dict[str, float]
    review_decision: str
    backtest_ref: str
    report_ref: str
    trace: list[str]
    status: str
```

State 里不塞大 DataFrame，而是传递 artifact 路径和摘要指标。这是为了让流程可恢复、可记录、可审计。

## 节点一：define_candidate_factor

这个节点现在只更新 trace 和 status：

```python
return {
    "trace": [*state["trace"], "define_candidate_factor"],
    "status": "factor_defined",
}
```

真实系统里，这一步可以由 LLM 根据研究笔记、候选库或用户目标提出因子。但即使由 LLM 提出，它也只能提出配置，不能直接生成数值。

## 节点二：compute_factor

`compute_factor()` 从真实 CSV 读取行情，计算：

```python
data["factor"] = data["close"] / by_symbol["close"].shift(state["lookback"]) - 1
data["label"] = by_symbol["close"].shift(-state["label_horizon"]) / data["close"] - 1
```

然后写出：

```text
artifacts/factor_data.csv
```

这是后续所有评估的证据基础。报告引用的是 `factor_ref`，不是一句自然语言描述。

## 节点三：evaluate_factor

`evaluate_factor()` 读取 `factor_ref`，计算：

- `rows`
- `ic`
- `rank_ic`
- `factor_mean`
- `label_mean`

本例只有一个 ETF，因此 IC / RankIC 是时间序列相关。完整选股研究应当在多标的横截面上逐日计算 IC，再对时间求均值。

这点很重要：本例展示流程，不把单 ETF 指标包装成选股结论。

## 节点四：auto_review

```python
enough_rows = metrics.get("rows", 0) >= 120
finite_ic = metrics.get("ic") == metrics.get("ic")
decision = "approve_backtest" if enough_rows and finite_ic else "reject_backtest"
```

这里用自动规则代替人工审批，目的是保证脚本可以一键运行。它不是生产审批方案。

生产系统应该把这里替换为：

- LangGraph `interrupt()`。
- Reviewer / Red-Team 节点。
- 审批 UI。
- 研究预算检查。

本例保留这个节点，是为了表达一个原则：回测不应该无条件发生。

## 条件路由：审查决定是否进入回测

```python
builder.add_conditional_edges("auto_review", route_after_review)
```

如果 `review_decision == "approve_backtest"`，图进入 `run_backtest`；否则直接进入 `write_report`。

这比在函数里写一串 `if` 更适合扩展。以后你可以把被拒绝路径接到 `request_revision`、`write_rejection_report` 或 `human_review`。

## 节点五：run_backtest

回测逻辑是一个极简 top-1 策略：

```text
每天选择 factor 最高的标的
  ↓
用下一期 label 作为收益
  ↓
换手时扣 10bp 成本
  ↓
生成 equity
```

由于当前数据只有 `SH510300` 一个标的，这个 top-1 回测实际上是单标的持有示例，主要用于展示回测 artifact、成本字段和流程边界。它不能代表完整组合研究。

输出文件：

```text
artifacts/backtest.csv
```

新增指标：

- `backtest_rows`
- `total_net_return`
- `avg_turnover`

## 节点六：write_report

最终报告写入：

```text
artifacts/report.json
```

报告包含：

- 实验 ID。
- 标的和日期区间。
- 因子定义。
- 指标。
- factor / backtest artifact 引用。
- 审慎结论。
- 完整 trace。

trace 类似：

```text
define_candidate_factor -> compute_factor -> evaluate_factor -> review:approve_backtest -> run_backtest -> write_report
```

这就是可审计工作流和普通脚本最大的区别：你不仅知道结果，还知道结果如何产生。

## 实际运行

```bash
python quant_research_agent.py
```

你会看到类似输出：

```text
status: reported
report_ref: .../artifacts/report.json
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

这些 artifacts 被 `.gitignore` 忽略，因为它们是运行产物。

## 这个示例还缺什么

它是端到端最小闭环，但还不是完整研究系统。仍然缺少：

- 多股票 universe。
- Qlib Dataset / DataHandler 接入。
- 样本外和 holdout 管理。
- 正式 human-in-the-loop。
- Reviewer 和 Red-Team 合入主流程。
- 实验数据库或 MLflow。
- 风险、容量、行业暴露和交易约束。

但它已经给出核心形状：Agent 不替代研究纪律，而是把研究纪律编排成可执行流程。

## 常见坑

- 端到端跑通后误以为因子有效。
- 把单 ETF 回测当成组合策略结论。
- 回测前没有审批或预算控制。
- 没有保存 factor data，只保存最终报告。
- 失败路径没有记录。
- Agent 同时提出、评估、批准自己的结论。

## 下一步可以扩展

第 12 节给出的是端到端图结构。后续扩展不应该继续把逻辑堆进节点函数，而应该把前面几节的控制机制接进来：

- 用第 13 节的 `ToolRuntime` 包住 `compute_factor`、`evaluate_factor` 和 `run_backtest`，让每个工具都有描述、参数 schema、超时、重试和调用次数限制。
- 把 `compute_factor()` 换成 Qlib 表达式工具，但仍然通过第 13 节的参数校验限制表达式、日期区间和 universe。
- 把 `auto_review()` 换成第 8 节的 `interrupt()`，让回测前审批真正由人工恢复图执行。
- 把第 10 节 Reviewer / Red-Team 接入回测前分支，让审查结果决定是否进入回测。
- 把 report 写入第 11 节的实验记录器，保存工具调用、参数、artifact、指标和最终决策。
- 把第 6 节的研究预算接进 state，限制最大候选因子数、最大窗口数、最大回测次数。

也就是说，第 12 节负责回答“完整 Agent workflow 长什么样”，第 13 节负责回答“这个 workflow 里的工具调用如何工程化地受控”。两者应该组合使用：

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

图负责状态和路由，工具运行时负责执行边界。缺少任何一边，都不是一个可靠的量化研究 Agent。
