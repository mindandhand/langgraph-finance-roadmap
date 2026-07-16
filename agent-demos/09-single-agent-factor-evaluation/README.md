# 单 Agent 因子评估：报告可以由 Agent 写，指标必须由工具算

这篇文档讲的是 `single_agent_factor_evaluation.py`。它把前面几节串起来：一个单 Agent workflow 读取真实 ETF 数据，计算候选因子，评估 IC / RankIC，最后生成报告。

重点不是这个 5 日动量因子是否有效，而是职责边界：

```text
Agent / Graph: 组织流程和状态流转
Tool code: 读取数据、计算因子、计算指标
Report node: 解释结果和披露限制
```

## 为什么这里用 LangGraph

本节的流程已经不只是一个函数调用，而是有明确状态在节点之间传递：

```text
load_and_compute_factor
  ↓
evaluate_factor
  ↓
write_report
```

LangGraph 让这些节点有稳定边界：

- 每个节点读取 `FactorState` 的一部分。
- 每个节点只返回自己更新的字段。
- artifact 路径和 metrics 在 state 中流转。
- 后续可以自然加入审批、失败分支和 reviewer 节点。

## 真实数据输入

脚本读取：

```text
../../qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv
```

默认评估：

- `symbol`: `SH510300`
- `start_date`: `2024-01-01`
- `end_date`: `2026-07-14`
- `lookback`: `5`
- `label_horizon`: `1`

这比 toy sample 更接近真实研究：数据量足够大，日期覆盖清楚，输出 artifact 可复查。

## 节点一：计算因子和标签

```python
data["factor"] = data["close"] / by_symbol["close"].shift(state["lookback"]) - 1
data["label"] = by_symbol["close"].shift(-state["label_horizon"]) / data["close"] - 1
```

这里仍然坚持前面的原则：

- `factor` 只能使用过去价格。
- `label` 使用未来收益，但只用于训练和评估。
- 结果写入 `artifacts/factor_data.csv`。

Agent 不直接携带大 DataFrame，而是携带 `factor_ref`。这是更接近真实研究平台的做法。

## 节点二：评估 IC 和 RankIC

本例只有一个 ETF，所以这里计算的是时间序列相关：

```python
"ic": data["factor"].corr(data["label"])
"rank_ic": data["factor"].corr(data["label"], method="spearman")
```

在多股票横截面研究中，IC / RankIC 通常按交易日横截面计算，再对时间求均值。本例为了保持数据准备简单，用单 ETF 演示工具边界和流程结构。

这也正是报告必须披露的限制：单 ETF 时间序列 IC 不能直接等同于横截面选股能力。

## 节点三：写报告

`write_report()` 不修改指标，只把指标组织成可读报告：

```text
factor_ref: ...
rows: ...
ic: ...
rank_ic: ...
conclusion: metrics are diagnostics, not strategy returns
```

这条边界很重要。Agent 可以解释数值，但不能重算或美化数值。

## 实际运行

```bash
python single_agent_factor_evaluation.py
```

你会看到类似输出：

```text
status: reported
factor_ref: .../artifacts/factor_data.csv
metrics: {'rows': 605.0, 'ic': 0.0284, 'rank_ic': -0.0254, ...}
```

生成的 artifact 会被 `.gitignore` 忽略，因为它是运行产物。

## 单 Agent 的局限

单 Agent 可以完成初筛，但不应该单独批准研究结论：

- 自己提出因子，自己解释结果，容易确认偏误。
- 容易忽略成本、样本外、容量和行业暴露。
- 如果没有预算限制，可能自动换参数直到结果变好。
- 报告容易强调支持证据，弱化反证。

所以本节只到“评估报告”，不直接给投资结论。

## 常见坑

- 把 IC 当成收益。
- 把单 ETF 时间序列相关当成横截面选股能力。
- Agent 修改工具返回的指标。
- 只报告平均值，不报告样本数和数据区间。
- 没有把 factor data 保存成 artifact。

## 下一步

下一节 `10-multi-agent-review-and-red-team` 会把 Researcher、Reviewer、Red-Team 分开，让不同角色独立审查同一份结论。
