# Agent for Quant Research：从 0 到可运行的量化研究 Agent

这是一条把 `langgraph-demos/` 和 `qlib-demos/` 合起来用的 Agent 学习路径。

它不把 Agent 当成聊天机器人来讲，而是围绕一个更具体的问题：

```text
如何让 Agent 服务于可复现、可审查、可约束的量化研究？
```

## 先给 Agent 一个朴素定义

本目录采用的 Agent 定义很务实：

```text
Agent = 状态 + 决策策略 + 工具 + 循环 + 终止条件 + 记录
```

更展开一点：

```text
observe state
  ↓
decide next action
  ↓
call allowed tool
  ↓
write result back to state / artifact
  ↓
decide whether to continue, stop, ask human, or hand off
```

LLM 不是 Agent 的全部。LLM 只可能参与 `decide next action` 和 `write report` 这些环节。数据读取、因子计算、IC、回测、成本、实验记录都应该由确定性工具完成。

## 为什么要结合 LangGraph 和量化

如果只讲抽象 Agent，很容易落到“模型会调用工具”的泛泛教程。这个仓库已经有两条基础线：

- `langgraph-demos/`：Graph、State、Tool Calling、Memory、Streaming、Interrupt、Subgraph。
- `qlib-demos/`：行情、表达式、Dataset、因子、模型、回测、实验记录。

所以 `agent-demos/` 的定位是第三层：

```text
用 LangGraph 的编排思想
  + Qlib/Pandas 的确定性量化工具
  + Agent 的任务拆解和审查能力
  = 可复现、可约束的量化研究 Agent
```

## Agent 应该做什么

对量化研究来说，Agent 适合做：

- 拆解研究任务。
- 选择允许的工具。
- 组织研究步骤。
- 检索已有研究笔记。
- 发现证据缺口。
- 请求人工审批。
- 汇总工具结果。
- 写出结构化报告。
- 保留 trace、artifact 和实验记录。

Agent 不应该做：

- 编造行情、财务数据或指标。
- 替代 Pandas/Qlib 做数值真值计算。
- 根据最终结果反复改参数。
- 跳过数据校验、成本和回测。
- 自动批准自己的研究结论。
- 用多 Agent 投票代替统计证据。

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
| 9 | [`09-single-agent-factor-evaluation`](09-single-agent-factor-evaluation) | 单 Agent 因子评估 | IC、RankIC 由工具计算 |
| 10 | [`10-multi-agent-review-and-red-team`](10-multi-agent-review-and-red-team) | 多 Agent 审查 | Researcher、Reviewer、Red-Team 分权 |
| 11 | [`11-agent-experiment-recorder`](11-agent-experiment-recorder) | 实验记录 | 保存参数、指标、artifact、失败原因 |
| 12 | [`12-end-to-end-quant-research-agent`](12-end-to-end-quant-research-agent) | 完整研究 Agent | 候选因子 → 评估 → 回测 → 审批 → 报告 |

## 概念地图

```text
Agent loop（01）
  ↓
Research State（02）
  ↓
Tool boundary: market data + factor calculation（03-04）
  ↓
Memory / Journal / Planning（05-06）
  ↓
Evidence retrieval and human approval（07-08）
  ↓
Single-agent evaluation workflow（09）
  ↓
Independent review and red-team（10）
  ↓
Experiment recorder（11）
  ↓
End-to-end quant research agent（12）
```

## Agent 和普通 Workflow 的区别

普通 workflow 的路径通常是固定的：

```text
load -> compute -> evaluate -> report
```

Agent workflow 的路径由 State 和决策策略决定：

```text
if data missing -> load data
if factor missing -> compute factor
if evidence weak -> request more tests or stop
if backtest requested -> ask human review
if reviewer finds gap -> revise or reject
```

所以 Agent 的价值不在于“更会写代码”，而在于它能根据状态选择下一步。但这个灵活性必须被预算、工具权限和终止条件约束。

## Agent 和 Tool Calling 的区别

Tool calling 只是一次结构化函数调用：

```text
model -> tool_call -> tool_result
```

Agent 至少还要有：

- 状态。
- 循环。
- 多步决策。
- 终止条件。
- trace。
- 错误和审批路径。

没有这些，工具调用只是函数调用，不是研究 Agent。

## Agent 和 RAG 的区别

RAG 是检索证据。Agent 是根据状态决定是否检索、检索什么、如何使用证据、是否还需要工具计算或人工审批。

在量化研究里，RAG 不能替代数据计算。研究笔记可以告诉你“短期动量可能高换手”，但真实换手、成本和收益仍然必须由回测工具计算。

## 多 Agent 的正确用法

多 Agent 不应该用于热闹讨论，也不应该靠投票裁决。更合理的是分权：

```text
Researcher: 提交候选和初步证据
Reviewer: 检查证据完整性
Red-Team: 主动寻找失败路径
Human: 最终判断或要求补充测试
```

事实冲突由确定性工具裁决，统计冲突由补充检验解决，经济解释冲突可以披露并保留。

## 运行准备

所有示例默认只依赖 Python 标准库；涉及表格计算的示例使用 `pandas`：

```bash
pip install pandas
```

为了保证每个目录独立运行，本路径默认使用 fake model / rule model 和内置小数据，不依赖外部 LLM API。

涉及人工审批的示例可以交互运行，也可以用管道模拟：

```bash
printf 'yes\n' | python agent-demos/08-human-review-before-backtest/human_review.py
```

## 完成后应该能回答什么

- Agent 的最小组成是什么。
- Agent 和普通 workflow 有什么区别。
- Agent 和 tool calling 有什么区别。
- Agent 和 RAG 有什么区别。
- 为什么量化 Agent 必须使用确定性工具。
- 为什么 LLM 不能直接给因子结论。
- 如何把工具调用、artifact、journal 和实验记录串起来。
- 如何限制 Agent 的研究预算和工具权限。
- 为什么回测前需要人工审批。
- 多 Agent 审查为什么不是投票。
- 如何让 Agent 服务于可复现研究，而不是变成聊天机器人。
