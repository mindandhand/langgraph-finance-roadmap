# 回测前人工审批：用 LangGraph 中断敏感步骤

这篇文档讲的是 `human_review.py`。它演示一个非常小但重要的机制：在进入回测前暂停图执行，等待人工审批，再从同一个状态继续。

回测是量化研究里的敏感步骤。不是因为代码危险，而是因为它会改变研究者后续行为。一旦看到了回测结果，就很难保证自己没有根据结果调整参数、因子、样本或解释。

## 这个示例想说明什么

本节开始使用 LangGraph，因为这里第一次出现“暂停后恢复”的需求：

```text
prepare_request
  ↓
human_review 通过 interrupt() 暂停
  ↓
Command(resume="approve") 恢复
  ↓
approve_backtest 或 reject_backtest
```

普通 Python 的 `input()` 可以做命令行交互，但它不能很好地表达可恢复状态。真实 Agent 平台需要把审批请求发给 UI、任务队列或 reviewer，然后稍后恢复执行。LangGraph 的 `interrupt()` 正是为这个场景设计的。

## ReviewState：审批必须有上下文

```python
class ReviewState(TypedDict):
    factor: str
    period: str
    backtests_used: int
    max_backtests: int
    review_payload: dict
    review_decision: str
    final_status: str
```

审批不是问一句“是否继续”。审批人需要看到：

- 因子名称。
- 样本区间。
- 已用回测次数。
- 最大回测预算。

这些字段进入 `review_payload`，再由 `interrupt()` 抛给外部系统。

## interrupt()：把人工决策变成图的一部分

```python
decision = interrupt(state["review_payload"])
```

这行代码的含义是：图执行到这里时停止，并把 payload 交给外部。外部稍后用：

```python
Command(resume="approve")
```

恢复执行。

恢复后，`human_review()` 会把人工决定写入 state：

```python
return {"review_decision": str(decision)}
```

然后条件路由决定下一步走哪里。

## 为什么需要 checkpointer

```python
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

中断后，图必须记住暂停前的状态，否则恢复时不知道自己审批的是哪个因子、哪个区间、哪一次预算。`MemorySaver` 是内存版 checkpointer，适合本地演示。

生产系统应该换成持久化 checkpointer，并记录：

- 审批 payload。
- 审批人。
- 审批时间。
- 审批决定。
- 恢复后的执行路径。

## 条件路由：审批不是装饰

```python
def route_after_review(state: ReviewState) -> str:
    if state["review_decision"].lower() in {"approve", "approved", "yes", "y"}:
        return "approve_backtest"
    return "reject_backtest"
```

审批结果直接决定图的后续节点。批准才进入 `approve_backtest`，拒绝则进入 `reject_backtest`。

这和“在日志里写一句人工已审批”不同。这里审批结果会改变程序路径。

## 实际运行

```bash
python human_review.py
```

脚本为了可重复运行，会自动模拟一次批准：

```text
interrupt_payload: ...
final_status: approved_for_backtest
review_decision: approve
```

你应该关注的不是自动批准，而是执行方式：第一次 invoke 触发中断，第二次用 `Command(resume=...)` 恢复。

## 常见坑

- 让 Agent 自动批准自己的回测。
- 审批 payload 太少，人工看不到研究预算和样本区间。
- 审批后没有记录是谁批准、何时批准、批准了什么。
- 被拒绝后 Agent 自动换参数重试。
- 只做 UI 弹窗，没有把审批结果接入图路由。

## 下一步

审批机制只是单独一环。下一节 `09-single-agent-factor-evaluation` 会把真实数据、因子计算、评估指标和报告节点串成一个 LangGraph workflow。
