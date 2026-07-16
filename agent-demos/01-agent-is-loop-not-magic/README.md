# Agent 是循环，不是魔法

这篇文档讲的是 `agent_loop.py`。它故意不用 LLM、不用 LangGraph、不用任何外部 API，只保留 Agent 的最小骨架：**观察当前状态，决定下一步动作，执行动作，然后再次观察状态**。

很多 Agent 教程一开始就上模型、工具调用、记忆和多 Agent，容易让人误以为 Agent 是某种神秘能力。其实最小 Agent 只是一个受控循环：

```text
observe state -> decide action -> act -> update state -> observe again
```

量化研究里的 Agent 也必须先从这个循环理解。区别只在于：它观察的不是聊天上下文，而是研究任务状态；它执行的不是随意动作，而是受约束的确定性工具。

## 这个示例想说明什么

`agent_loop.py` 跑的是一个玩具任务：给一段 ETF 价格，计算简单动量并输出回答。

执行轨迹是：

```text
load_prices -> compute_momentum -> write_answer -> finish
```

这条轨迹已经包含 Agent 的四个核心部件：

- **State**：保存问题、价格、动量、回答、是否结束、执行轨迹。
- **Policy / Decide**：根据当前 State 决定下一步动作。
- **Action / Tool**：真正执行动作，更新 State。
- **Stop condition**：状态完成或达到最大步数后停止。

如果把 `decide()` 换成 LLM，把 `act()` 换成工具调用系统，把 `ResearchState` 换成 LangGraph State，这就是后续复杂 Agent 的骨架。

## State：Agent 看到的世界

```python
@dataclass
class ResearchState:
    question: str
    prices: list[float] = field(default_factory=list)
    momentum: float | None = None
    answer: str = ""
    done: bool = False
    trace: list[str] = field(default_factory=list)
```

这里没有 `messages`，因为本节不是聊天机器人。Agent 需要完成的是一个研究任务，所以 State 直接保存研究任务需要的字段。

字段含义：

- `question`：用户给出的研究请求。
- `prices`：工具加载出的价格序列。
- `momentum`：确定性计算得到的数值结果。
- `answer`：最终文本摘要。
- `done`：循环是否结束。
- `trace`：执行过哪些动作，方便审计。

量化 Agent 的 State 应该优先保存结构化研究状态，而不是把所有东西塞进自然语言对话。

## Decide：为什么下一步是这个动作

```python
def decide(state: ResearchState) -> str:
    if not state.prices:
        return "load_prices"
    if state.momentum is None:
        return "compute_momentum"
    if not state.answer:
        return "write_answer"
    return "finish"
```

这就是一个最小策略函数。它不是“智能”的，但它揭示了 Agent 的本质：**根据当前缺什么，决定下一步补什么**。

真实 LLM Agent 的 `decide` 也在做类似事情，只是它会从 prompt、messages、tool schema 和 state 中推断下一步。区别在于，LLM 的决策更灵活，也更容易出错，所以必须加工具白名单、预算和终止条件。

## Act：动作必须改变 State

```python
def act(action: str, state: ResearchState) -> None:
    state.trace.append(action)
    if action == "load_prices":
        state.prices = PRICES.copy()
    elif action == "compute_momentum":
        state.momentum = state.prices[-1] / state.prices[0] - 1
    elif action == "write_answer":
        state.answer = f"5-day momentum is {state.momentum:.2%}."
    elif action == "finish":
        state.done = True
```

每个动作都对应一个确定的状态变化：

- `load_prices` 填充价格。
- `compute_momentum` 填充动量。
- `write_answer` 填充回答。
- `finish` 标记结束。

这点很重要：Agent 的动作不是“想一想”这么抽象，它必须可观察、可记录、可复现。量化研究里尤其如此，因为数值结论不能只存在于模型回复里。

## 循环和终止条件

```python
def run_agent(question: str, max_steps: int = 8) -> ResearchState:
    state = ResearchState(question=question)
    for _ in range(max_steps):
        if state.done:
            break
        action = decide(state)
        act(action, state)
    return state
```

这里有两层停止机制：

- 业务停止：`state.done == True`
- 安全停止：`max_steps`

真实 Agent 一定要有类似保护。没有最大步数的 Agent 很容易陷入“继续查、继续算、继续改”的循环。量化研究里这会变成参数挖掘和回测过拟合。

## 实际运行

```bash
python agent_loop.py
```

输出：

```text
trace: load_prices -> compute_momentum -> write_answer -> finish
answer: 5-day momentum is 8.00%.
```

这里的 `trace` 比最终回答更重要。因为它告诉你这个结论是怎么来的，而不是只给一个自然语言结果。

## 和普通函数调用有什么区别

普通脚本可以直接写：

```python
prices = PRICES
momentum = prices[-1] / prices[0] - 1
print(momentum)
```

Agent 循环的价值在于：下一步动作由状态决定，而不是完全写死。后续当状态变复杂，例如“数据缺失”“评估失败”“需要审批”“预算耗尽”，Agent 可以路由到不同动作。

但这也带来风险：Agent 越灵活，越需要约束。

## 常见误解

- Agent 不是“LLM + prompt”。
- Tool calling 不等于 Agent；没有循环和状态，也只是一次函数调用。
- Memory 不等于把所有聊天历史塞回 prompt。
- 多 Agent 不等于多个模型互相聊天。
- 在量化研究里，Agent 的灵活性必须服从数据、统计和回测纪律。

## 下一步

本节只有一个简单 dataclass。下一节 `02-agent-state-and-research-task` 会把 State 正式设计成量化研究任务状态：研究目标、标的、时间区间、候选因子、artifact 引用、指标和状态。
