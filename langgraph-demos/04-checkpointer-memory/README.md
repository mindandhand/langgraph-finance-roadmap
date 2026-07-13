# LangGraph + Checkpointer：让图"记住"之前的对话

示例 1、2、3 都只调用了一次 `graph.invoke()` 就结束了。这篇文档讲的是 `memory_graph.py`：同一个 `graph` 对象被反复调用，而且第二次问"我叫什么名字"的时候，LLM 真的记得——即使我们没有手动把第一轮的消息重新传进去。

## 这个 示例 想说明什么

前三个 示例 里，"State 会持续到哪"这件事其实很清楚：一次 `invoke()` 从 `START` 走到 `END`，State 就跟着活多久，`invoke()` 一返回，这次的 State 就没了。下一次 `invoke()` 是全新的一次。

Checkpointer 打破的就是这一点：它在**每一步之后**把 State 存起来，用一个 `thread_id` 当索引。下次你用同一个 `thread_id` 调 `invoke()`，LangGraph 会先把存好的 State 读出来，再把你这次传入的新内容合并进去。图的结构完全不知道这件事在发生——它只是照常从 `START` 走到 `END`；"记忆"是 compile 时挂的这一个组件在背后做的。

```python
graph = builder.compile(checkpointer=InMemorySaver())
```

示例 里图的形状和 示例 1 一样简单：

```
START -> chatbot -> END
```

新东西不在图的结构里，而在 `compile()` 的参数和每次 `invoke()` 传的 `config` 里。

## 关键代码

```python
graph = builder.compile(checkpointer=InMemorySaver())

thread_a = {"configurable": {"thread_id": "conversation-a"}}

graph.invoke({"messages": [HumanMessage("My name is Neil.")]}, thread_a)
graph.invoke({"messages": [HumanMessage("What's my name?")]}, thread_a)
```

第二次调用只传了新的一句话，`messages` 列表里并没有手动带上"My name is Neil."——但 `chatbot` 节点执行时，`state["messages"]` 里已经有历史消息了。发生的事情是：

1. LangGraph 用 `thread_id = "conversation-a"` 去 checkpointer 里查上一次存的 State，读到 `messages = [Human("My name is Neil."), AI("Nice to meet you...")]`。
2. 把这次新传入的 `{"messages": [HumanMessage("What's my name?")]}` 通过 `add_messages` 归约器**追加**到读出来的历史后面（`add_messages` 已经在 示例 3 里出现过，这里的用法完全一样，只是这次追加的"旧历史"来自 checkpointer，而不是同一次 `invoke()` 内部）。
3. `chatbot` 节点看到的是完整的三条消息，所以能正确回答"你叫 Neil"。
4. 这一步结束后，checkpointer 又把新的 State（四条消息）存回 `conversation-a` 这个 `thread_id` 下。

## 实际跑起来的输出

```
Nice to meet you, Neil! How can I help you today?
```
```
Your name is Neil.
```
```
I don't know your name yet! Could you please tell me what it is?
```

前两句都是 `thread_a`：第一轮打招呼，第二轮正确答出名字。第三句换成了 `thread_b`（一个全新的 `thread_id`），同样问"我叫什么"，LLM 表示不知道——因为 checkpointer 里根本没有这个 `thread_id` 对应的历史，图是从空 State 开始跑的。这就是"记忆"的边界：**不是模型记住了，是某个 `thread_id` 下的 State 被存下来了**。

> 顺带一提：这里用的模型开了 extended thinking，`pretty_print()` 会先把原始的 content block 列表整段打出来，再打一次格式化后的文本——这和 示例 2 里 `.content` 是列表而不是字符串是同一件事，只是 `pretty_print()` 自己处理的方式比手写 `.strip()` 更宽容，不会直接报错。

## `InMemorySaver` 只是最简单的一种

```python
from langgraph.checkpoint.memory import InMemorySaver
```

`InMemorySaver` 把所有 checkpoint 存在进程内存里——进程一退出，所有 `thread_id` 的历史就没了，本 示例 用它纯粹是因为不需要额外装东西、跑起来最快。LangGraph 生态里还有 `SqliteSaver`、`PostgresSaver` 等实现，接口完全一样（都实现了同一个 `BaseCheckpointSaver` 接口），换一行 `compile(checkpointer=...)` 就能把内存换成真正持久化的存储，图和节点的代码不用动分毫——这也是为什么"记忆"被设计成一个可插拔组件，而不是让你在节点里自己手写"读数据库、拼历史"的逻辑。

## 和前三个 示例 的关键区别

| | 示例 1/2 | 示例 3 | 示例 4 |
|---|---|---|---|
| 图的形状 | DAG | 有循环 | DAG（和 demo1 一样简单） |
| 新概念在哪 | 节点内部逻辑 | 边的连接方式 | `compile()` 的参数 + 调用时的 `config` |
| State 的生命周期 | 一次 `invoke()` | 一次 `invoke()`（哪怕循环多轮） | 跨越多次 `invoke()`，只要 `thread_id` 相同 |

## 下一步可以扩展的方向

- 用 `graph.get_state(thread_a)` 查看某个 `thread_id` 当前存的完整 State，或用 `graph.get_state_history(thread_a)` 遍历这个线程每一步的历史快照——这是调试"LLM 为什么这么回答"的利器。
- 把 `InMemorySaver` 换成 `SqliteSaver`，验证进程重启后 `thread_id` 对应的对话还能继续。
- 结合 示例 3 的工具调用循环：一个既能循环调用工具、又能跨多轮 `invoke()` 记住历史的 Agent，只需要把两个 示例 的 `compile()` 参数和 `add_edge("tools", "agent")` 合在一起，State、Node 的写法完全不用变。
- 了解 `interrupt()` + checkpointer 组合出的 human-in-the-loop：因为每一步的 State 都被存了下来，图可以在某个节点暂停、等人工审核后再从暂停的地方继续跑，而不是重新跑一遍。
