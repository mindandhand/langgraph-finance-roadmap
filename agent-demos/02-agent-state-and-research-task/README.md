# Agent State：把任务状态设计成研究对象

这篇文档讲的是 `research_state.py`。示例 1 里 State 只是几个字段；这一节把它扩展成更像量化研究任务的结构。

很多 Agent 示例把 State 写成 `messages: list`。这对聊天机器人够用，但对量化研究不够。研究 Agent 需要知道：研究目标是什么，标的是什么，时间区间是什么，候选因子是什么，产物在哪里，指标是多少，当前状态到哪一步。

## 这个示例想说明什么

`ResearchState` 是一个 `TypedDict`：

```python
class ResearchState(TypedDict):
    research_id: str
    objective: str
    instrument: str
    start_date: str
    end_date: str
    candidate_factor: str
    artifact_refs: dict[str, str]
    metrics: dict[str, float]
    status: str
```

这比聊天历史更适合研究任务，因为每个字段都有明确用途。

## Artifact 引用为什么重要

```python
state["artifact_refs"]["prices"] = "artifacts/agent-demo-002/prices.csv"
state["artifact_refs"]["factor"] = "artifacts/agent-demo-002/factor.csv"
```

真实研究里，价格矩阵、因子矩阵、预测结果、回测明细都可能很大，不应该长期塞进 State。State 应该保存引用和摘要。

这也是 LangGraph / Agent 编排里的重要边界：State 负责协调流程，不负责承载所有数据。

## 状态变化

脚本执行：

```text
create_task
  -> register_price_artifact
  -> register_factor_artifact
```

每一步都更新 `status`：

```text
created -> data_registered -> factor_registered
```

状态字段让后续路由变得明确。例如：

- `data_registered` 后才能计算因子。
- `factor_registered` 后才能评估。
- `review_required` 后必须等待审批。

## 常见坑

- State 只有自然语言，没有结构化字段。
- 把大型 DataFrame 放进 State。
- artifact 路径没版本，后续运行互相覆盖。
- `status` 太随意，无法作为路由条件。
- 指标没有和数据版本、因子版本绑定。

## 设计原则一：State 是流程契约，不是临时变量堆

Agent State 最容易被写坏。很多实现会把所有临时变量、模型回复、工具结果、DataFrame、错误信息都塞进一个大 dict。短期看省事，长期看会导致三个问题：

- 路由条件不稳定：不知道应该看哪个字段决定下一步。
- 复现困难：同一个字段可能在不同节点里被不同含义地覆盖。
- 上下文污染：LLM 看到太多无关内容，更容易误读任务。

所以本示例把 State 设计成一个研究流程契约。每个字段都回答一个明确问题：

```text
objective        研究要解决什么问题
instrument       研究哪个标的
date range       研究哪个时间段
candidate_factor 当前候选因子是什么
artifact_refs    大型产物在哪里
metrics          已经算出的指标
status           当前流程走到哪一步
```

这套结构可以直接映射到 LangGraph State。节点只读自己需要的字段，只写自己负责更新的字段。

## 设计原则二：State 保存“小而稳定”的信息

量化研究会产生很多大型对象：

- 原始行情 DataFrame
- 因子矩阵
- 预测分数
- 回测成交明细
- 模型文件

这些对象不适合长期放进 Agent State。原因不是技术上不能放，而是工程上不应该放：

- State 会被序列化、checkpoint、传给节点，过大会拖慢执行。
- 大型对象难以 diff，审计时看不清变化。
- LLM 不应该直接读取完整矩阵；它只需要摘要和引用。

更好的方式是：

```text
大型对象 -> artifact 文件 / 数据库 / Qlib Recorder
State   -> artifact_ref + 摘要 + 版本
```

这样 Agent 可以知道“因子已经算完，结果在哪里”，但不会把因子矩阵当成聊天上下文。

## 设计原则三：status 必须能驱动路由

`status` 不是给人看的标签，而是给流程控制用的字段。

坏的 status：

```text
ok
done
processing
almost ready
```

这些状态太模糊，无法安全路由。

好的 status：

```text
created
data_registered
factor_registered
evaluated
review_required
approved_for_backtest
rejected
```

这些状态可以直接决定下一步：

```text
created               -> load/register data
data_registered       -> compute factor
factor_registered     -> evaluate
evaluated             -> request review
approved_for_backtest -> run backtest
rejected              -> stop
```

这就是 LangGraph 里 conditional edge 的基础。路由函数不应该猜测自然语言，它应该读取结构化状态。

## 设计原则四：State 不等于 Memory

State 和 Memory 经常被混在一起：

```text
State  = 当前这次执行需要的工作状态
Memory = 跨实验、跨会话保留的历史证据
```

当前研究的 `candidate_factor`、`status`、`artifact_refs` 属于 State。过去失败过的因子、历史审查意见、研究笔记属于 Memory 或 Journal。

如果把 Memory 全塞进 State，Agent 会背着大量历史信息走每一步，容易污染判断。更好的做法是：State 只保留当前任务；需要历史信息时，通过 RAG 或 journal 查询。

## 如何扩展到真实系统

真实量化 Agent 的 State 可以继续增加：

```python
class ResearchState(TypedDict):
    research_id: str
    objective: str
    universe: str
    data_version: str
    factor_spec: dict
    label_spec: dict
    budget: dict
    artifact_refs: dict[str, str]
    metrics: dict[str, float]
    review_findings: list[dict]
    decision: str
    status: str
```

但不要一开始就加太多字段。原则是：只有当某个字段会被节点读取、路由使用、审计需要，才加入 State。

## 下一步

State 定义好之后，下一节 `03-tool-calling-for-market-data` 会让 Agent 通过工具获取市场数据，而不是自己编造行情。
