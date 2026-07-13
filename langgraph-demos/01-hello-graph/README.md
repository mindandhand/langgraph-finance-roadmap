# LangGraph 入门：从一个最小示例理解它的基本逻辑

`hello_graph.py` 是一个不依赖任何 API Key、几秒钟就能跑起来的最小 LangGraph 示例。这篇文章带你逐行理解它，并搞清楚 LangGraph 到底在做什么。

## LangGraph 是什么

LangGraph 把一个"应用"建模成一张**图（Graph）**：数据（状态）在图上从起点流向终点，每经过一个节点，就被这个节点加工一次。相比手写一堆 if-else 和函数调用，LangGraph 的价值在于：

- 流程结构是显式的（图结构本身就是文档）
- 支持分支、循环、并行，天然适合"多步骤 / 多 Agent"场景
- 自带状态管理、断点续跑（checkpoint）、流式输出等能力

理解 LangGraph，本质就是理解 4 个概念：**State、Node、Edge、Graph**。

## 1. State —— 在图上流动的数据

```python
class State(TypedDict):
    name: str
    mood: str
    message: str
```

State 是贯穿整张图的"共享数据结构"。所有节点读的是同一份 State，写回去的也是同一份 State 里的字段。你可以把它想象成一个在流水线上传递的"包裹"，每个工位（节点）打开包裹，往里加东西，再传给下一个工位。

## 2. Node —— 只是一个函数

```python
def greet(state: State) -> dict:
    return {"message": f"Hello, {state['name']}!"}
```

节点的规则很简单：**接收当前 State，返回一个要更新的字段字典**。注意 `greet` 并没有返回整个 State，只返回了 `message` 这一个字段——LangGraph 会自动把这个返回值合并（merge）进当前 State，而不是替换掉整个 State。这也是为什么 `name` 和 `mood` 在后续节点里依然可以读到。

`route_by_mood` 是一种特殊的节点，叫**路由函数**：

```python
def route_by_mood(state: State) -> str:
    return "happy_reply" if state["mood"] == "happy" else "grumpy_reply"
```

它不更新 State，只返回一个字符串——"接下来该走哪个节点"。

## 3. Edge —— 节点之间怎么连

- **固定边**（`add_edge`）：走完 A 必然走 B，没有分支。
  ```python
  builder.add_edge(START, "greet")
  builder.add_edge("happy_reply", END)
  ```
- **条件边**（`add_conditional_edges`）：走完 A 之后，用一个路由函数决定去哪。
  ```python
  builder.add_conditional_edges("greet", route_by_mood)
  ```

`START` 和 `END` 是 LangGraph 内置的两个特殊节点，分别代表图的入口和出口。

## 4. Graph —— 把 State/Node/Edge 组装起来

```python
builder = StateGraph(State)
builder.add_node("greet", greet)
builder.add_node("happy_reply", happy_reply)
builder.add_node("grumpy_reply", grumpy_reply)

builder.add_edge(START, "greet")
builder.add_conditional_edges("greet", route_by_mood)
builder.add_edge("happy_reply", END)
builder.add_edge("grumpy_reply", END)

graph = builder.compile()
```

先用 `StateGraph(State)` 声明"这张图的数据长什么样"，然后依次注册节点（`add_node`）和边（`add_edge` / `add_conditional_edges`），最后调用 `.compile()`，把这张"设计图"编译成一个可以真正运行的 `graph` 对象。

## 整张图长这样

```
START -> greet -> route_by_mood -> happy_reply  -> END
                                 -> grumpy_reply -> END
```

## 5. 调用它

```python
result = graph.invoke({"name": "Neil", "mood": "happy", "message": ""})
```

`invoke` 传入初始 State，LangGraph 从 `START` 开始，按图的连接关系依次执行节点，每个节点的返回值不断合并进 State，直到走到 `END`，把最终 State 作为结果返回。

运行 `python hello_graph.py` 的输出：

```
[mood=happy] Hello, Neil! Great to see you in a good mood.
[mood=grumpy] Hello, Neil! Hope your mood improves soon.
```

同一张图，因为初始 `mood` 不同，走了不同的分支——这就是条件边的作用。

## 这套逻辑能扩展到哪里

这个 示例 里的节点只是拼字符串，但把某个节点的函数体换成"调用一次 LLM"，逻辑完全不用变：

```python
def call_llm(state: State) -> dict:
    response = model.invoke(state["message"])
    return {"message": response.content}
```

图的接线方式（State / Node / Edge / 条件路由）不变，你就得到了一个"LLM 节点"。再往上叠加：

- 节点里判断"要不要调用工具"，再用条件边分流 → 就是最基础的 **ReAct Agent**
- 让某条边指回前面的节点 → 就是**循环**（比如"重试直到满意为止"）
- 多个独立子图并行执行、结果汇总到一个节点 → 就是**多 Agent 协作**

也就是说，无论 LangGraph 的应用看起来多复杂（RAG、多 Agent、带人工审核的工作流……），骨架永远是这 4 个概念：State 在流动，Node 在加工，Edge（固定或条件）决定流向，Graph 把它们编译成一个可运行的整体。
