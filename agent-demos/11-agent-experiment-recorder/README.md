# Agent 实验记录器：让研究可复现

这篇文档讲的是 `agent_experiment_recorder.py`。它把一次 Agent 研究记录成一个 JSON 文件，包括目标、计划、工具调用、指标和决策。

如果 Agent 做完研究只输出一段回答，那这个研究不可复现。你无法知道它调用了哪些工具、用了哪些参数、指标从哪里来、为什么做出这个决策。

## 这个示例想说明什么

脚本生成：

```text
artifacts/experiment.json
```

内容包括：

```json
{
  "experiment_id": "agent-exp-001",
  "objective": "Evaluate 3-day momentum on toy ETF data",
  "plan": ["load_prices", "compute_factor", "evaluate_ic", "request_review"],
  "tool_calls": [...],
  "metrics": {"mean_ic": 0.04, "mean_rank_ic": 0.03},
  "decision": "requires_more_evidence"
}
```

这就是最小实验记录。

## 为什么记录 tool_calls

指标本身不够。必须知道指标是怎么来的：

- 哪个工具算的。
- 参数是什么。
- 输入 artifact 是什么。
- 输出 artifact 是什么。

没有 tool_calls，Agent 报告就像一段无法复查的自然语言。

## 和 Qlib Recorder 的关系

Qlib 有自己的实验记录能力。这个示例不是替代 Qlib Recorder，而是讲清楚 Agent 也需要同样的记录意识。

真实系统可以把本例 JSON 扩展成：

- Qlib Recorder
- MLflow run
- 数据库 experiment table
- LangGraph trace
- 文件系统 artifact manifest

## 常见坑

- 没有 experiment_id。
- 没有保存失败原因。
- 只保存 metrics，不保存参数。
- 只保存最终回答，不保存工具调用。
- 多 Agent 的不同意见被合并后丢失。

## 设计原则一：实验记录是 Agent 的审计边界

Agent 输出一段漂亮报告并不够。真正可用的研究系统必须回答：

```text
这份报告来自哪次实验？
使用了什么数据？
调用了哪些工具？
工具参数是什么？
指标是多少？
产物在哪里？
最后为什么做出这个决策？
```

`experiment.json` 就是最小答案。

如果没有实验记录，Agent 研究无法复现；无法复现，就不能进入策略决策。

## 设计原则二：记录计划和实际执行

脚本里同时保存：

```json
"plan": ["load_prices", "compute_factor", "evaluate_ic", "request_review"]
```

和：

```json
"tool_calls": [
  {"tool": "get_prices", "args": {"symbol": "SH510300"}},
  {"tool": "compute_momentum", "args": {"lookback": 3}}
]
```

计划说明“原本打算做什么”，工具调用说明“实际做了什么”。两者都重要。

真实系统里，计划和执行可能不一致：

- 工具失败后跳过某步。
- 审批拒绝后停止。
- 数据缺失后改走错误报告。
- Reviewer 要求补充测试。

记录差异有助于发现 Agent 是否越权或偏离计划。

## 设计原则三：metrics 必须绑定上下文

指标不能孤立存在：

```json
"metrics": {"mean_ic": 0.04}
```

这个 IC 只有在知道以下信息时才有意义：

- 因子定义
- 标签定义
- 股票池
- 日期区间
- 数据版本
- 计算工具版本
- 缺失处理规则

本示例只保存最小字段。真实系统应把这些上下文放进 params 或 artifact manifest。

## 设计原则四：记录失败比记录成功更重要

Agent 系统容易只保存看起来好的结果。量化研究恰恰需要保存失败，因为失败能防止重复踩坑，也能反映真实试错空间。

建议失败记录至少包含：

```json
{
  "status": "failed",
  "step": "evaluate_ic",
  "reason": "factor coverage below threshold",
  "artifact": "coverage_report.json"
}
```

这比一句“评估失败”有用得多。

## 和多 Agent 的关系

多 Agent 审查时，不同角色的意见都应该分别记录：

```text
researcher_claims
reviewer_findings
red_team_findings
human_decision
```

不要只保存最终共识。被否决的意见、未解决冲突、反方证据都应该保留。

## 和 Qlib Recorder 的关系

Qlib Recorder 更偏实验系统，能记录模型、预测、分析和 artifact。Agent Recorder 还需要记录：

- Agent plan
- tool calls
- review findings
- approval decisions
- prompt/config version

两者可以合并：Qlib Recorder 保存量化实验产物，Agent Recorder 保存编排和决策轨迹。

## 下一步

最后一节 `12-end-to-end-quant-research-agent` 会把因子计算、评估、审批、回测和报告串成完整最小闭环。
