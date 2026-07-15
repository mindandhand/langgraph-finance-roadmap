# Agent for Quant Research：从 0 到可运行的量化研究 Agent

这是一条把 `langgraph-demos/` 和 `qlib-demos/` 合起来用的 Agent 学习路径。

它不把 Agent 当成聊天机器人来讲，而是围绕一个更具体的问题：

```text
如何让 Agent 服务于可复现、可审查、可约束的量化研究？
```

## 核心立场

Agent 不是魔法。对量化研究来说，它应该负责：

- 拆解研究任务
- 选择允许的确定性工具
- 组织研究步骤
- 发现证据缺口
- 写出结构化报告
- 在关键节点等待人工审批

Agent 不应该负责：

- 直接编造因子有效性结论
- 替代 Pandas/Qlib 做数值真值计算
- 跳过数据校验和回测
- 无限尝试直到找到好结果
- 自动批准自己的研究结论

## 运行准备

所有示例默认只依赖 Python 标准库；涉及表格计算的示例使用 `pandas`：

```bash
pip install pandas
```

涉及 LangGraph 的示例需要：

```bash
pip install langgraph
```

为了保证每个目录独立运行，本路径默认使用 fake model / rule model 和内置小数据，不依赖外部 LLM API。

## 学习路径

| # | 目录 | 主题 | 新增能力 |
|---|---|---|---|
| 1 | [`01-agent-is-loop-not-magic`](01-agent-is-loop-not-magic) | Agent 是循环 | observe → decide → act → observe |
| 2 | [`02-agent-state-and-research-task`](02-agent-state-and-research-task) | 研究任务状态 | 把 State 设计成量化研究任务，而不是闲聊历史 |
| 3 | [`03-tool-calling-for-market-data`](03-tool-calling-for-market-data) | 市场数据工具 | Agent 选择工具，工具读取行情 |
| 4 | [`04-deterministic-factor-tools`](04-deterministic-factor-tools) | 确定性因子工具 | 因子计算由 Pandas 工具完成 |
| 5 | [`05-memory-and-research-journal`](05-memory-and-research-journal) | 研究记忆 | research journal、artifact refs、失败记录 |
| 6 | [`06-planning-a-factor-study`](06-planning-a-factor-study) | 研究规划 | 有预算、有步骤、有终止条件的计划 |
| 7 | [`07-rag-over-research-notes`](07-rag-over-research-notes) | RAG 研究笔记 | 检索已有笔记，不凭空编造 |
| 8 | [`08-human-review-before-backtest`](08-human-review-before-backtest) | 回测前审批 | 敏感步骤前暂停等待人工确认 |
| 9 | [`09-single-agent-factor-evaluation`](09-single-agent-factor-evaluation) | 单 Agent 因子评估 | IC、RankIC、分组收益由工具计算 |
| 10 | [`10-multi-agent-review-and-red-team`](10-multi-agent-review-and-red-team) | 多 Agent 审查 | Researcher、Reviewer、Red-Team 分权 |
| 11 | [`11-agent-experiment-recorder`](11-agent-experiment-recorder) | 实验记录 | 保存参数、指标、artifact、失败原因 |
| 12 | [`12-end-to-end-quant-research-agent`](12-end-to-end-quant-research-agent) | 完整研究 Agent | 候选因子 → 评估 → 回测 → 审批 → 报告 |

## 概念地图

```text
Agent loop（01）
  ↓
Research State（02）
  ↓
Tools: market data + factor calculation（03-04）
  ↓
Memory / Journal / Planning（05-06）
  ↓
Evidence retrieval and human approval（07-08）
  ↓
Factor evaluation workflow（09）
  ↓
Independent review and red-team（10）
  ↓
Experiment recorder（11）
  ↓
End-to-end quant research agent（12）
```

## 和前两条学习线的关系

- `langgraph-demos/` 教你 Graph、State、Tool Calling、Memory、Interrupt、Subgraph。
- `qlib-demos/` 教你行情、表达式、Dataset、因子、模型、回测、实验记录。
- `agent-demos/` 讲如何把两者组合成一个受约束的量化研究 Agent。

## 完成后应该能回答什么

- Agent 在量化研究里到底该做什么、不该做什么。
- 为什么 LLM 不能直接给因子结论。
- 如何把确定性 Pandas/Qlib 工具挂到 Agent 后面。
- 如何限制 Agent 的研究预算和工具权限。
- 如何用 LangGraph 表示 Agent 循环、审批和多 Agent 审查。
- 如何保存 research trace、artifact 和实验记录。
- 如何让 Agent 服务于可复现研究，而不是变成聊天机器人。
