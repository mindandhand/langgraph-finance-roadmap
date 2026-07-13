# LangGraph + 工具调用：图第一次真正"循环"起来

示例 1 和 示例 2 的图都是**有向无环图（DAG）**：数据从 `START` 流到 `END`，每个节点最多跑一次，不会走回头路。这篇文档讲的是 `agent_graph.py`——LangGraph 真正区别于"写一条 LLM 调用链"的地方：**一条指向自己上游的边**，让图可以循环，直到 LLM 自己决定停下来。

## 这个 示例 想说明什么

一个 ReAct 风格的工具调用 Agent，本质上就是一句话："让 LLM 自己决定要不要再多问一轮"。用图来表达就是：

```
START -> agent -> should_continue -> tools -> agent -> ... -> END
                \_____________________________________/
                        （tools 执行完总是绕回 agent）
```

- `agent` 节点：把当前对话丢给 LLM。LLM 要么直接回答，要么在回复里附带一个或多个 `tool_calls`。
- `should_continue` 路由：看 LLM 最新这条回复有没有 `tool_calls`。有 → 走向 `tools`；没有 → 走向 `END`。
- `tools` 节点：把 LLM 要求调用的工具真正跑一遍，把结果包装成 `ToolMessage` 追加进对话。
- `tools` 执行完之后**固定**连回 `agent`（`builder.add_edge("tools", "agent")`），这就是循环产生的地方——`agent` 会再看一次（这次带着工具结果的）对话，决定是直接回答还是继续调用工具。

和 示例 1、示例 2 相比，State / Node / Edge / Graph 这套接线方式还是没变，只是第一次出现了"某条边指向的节点，恰好是这条边的来源节点也能到达的上游"——这就是"循环"在图论意义上的样子。

## State 里新出现的东西：`add_messages` 归约器

```python
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

示例 1、示例 2 的 State 字段（`message`、`sentiment`、`reply`）都是"整个替换"：节点返回 `{"reply": "..."}`，新值直接覆盖旧值。但对话历史不能这么处理——如果每次 `agent` 节点返回的新消息覆盖掉整个 `messages` 列表，历史就全丢了。

`Annotated[list[BaseMessage], add_messages]` 告诉 LangGraph："这个字段更新时不要覆盖，要**追加**"。所以：

```python
def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}   # 只返回新增的这一条，LangGraph 自动追加
```

`agent` 节点返回的永远只是"新增的消息"，不需要手动拼接历史——这是 `add_messages` 这个归约器（reducer）在背后做的事。

## 逐个节点拆解

### `agent` —— 把对话交给绑定了工具的模型

```python
model = ChatAnthropic(model="claude-sonnet-5").bind_tools(tools)

def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

`bind_tools(tools)` 把工具的名字、描述、参数 schema 一起发给模型，模型据此决定要不要在回复里带上 `tool_calls`。这一步跟 示例 2 的 `model.invoke(prompt)` 没有本质区别，只是现在传的是整个消息列表（多轮对话），而不是一个 prompt 字符串。

### `call_tools` —— 真正执行 LLM 要求的调用

```python
def call_tools(state: State) -> dict:
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        output = tools_by_name[call["name"]].invoke(call["args"])
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}
```

注意 `for call in last_message.tool_calls`——一次回复里可能包含**多个**并行的工具调用（本 示例 跑起来的例子里，LLM 同时请求了 `get_weather` 和 `add`，见下方实际输出）。每个调用结果都要包成一条 `ToolMessage`，并且 `tool_call_id` 要和请求时的 `id` 对上，LLM 才能知道哪个结果对应哪个调用。

### `should_continue` —— 决定是循环还是结束

```python
def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END
```

和 示例 1、示例 2 的路由函数写法完全一样——读 State，返回下一个节点的名字。区别只是这次多了一个选项：直接返回 `END`。`add_conditional_edges` 支持路由函数返回 `END` 常量，图会正确地结束在这里，不需要额外声明。

## 图的接线：循环从哪来

```python
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")   # <- 就是这一行，把 tools 指回 agent
```

`add_conditional_edges("agent", should_continue)` 让 `agent` 之后的走向不固定；`add_edge("tools", "agent")` 则是一条固定边，但它指向的 `agent` 已经在图里出现过一次了。这两条边合起来，就让"`agent` → `tools` → `agent` → ..."可以重复任意多次，直到 `should_continue` 返回 `END`。

## 实际跑起来发生了什么

```
question = "What's the weather in Beijing, and what is 23 + 19?"
graph.invoke({"messages": [HumanMessage(question)]})
```

执行轨迹：

1. `agent`：LLM 看到问题，判断需要查天气 + 算加法，一次性返回**两个** `tool_calls`（`get_weather(city="Beijing")` 和 `add(a=23, b=19)`）。
2. `should_continue` 看到 `tool_calls` 非空 → 路由到 `tools`。
3. `call_tools`：依次执行两个工具，得到 `"Sunny, 25°C"` 和 `42.0`，各自包成一条 `ToolMessage` 追加进 `messages`。
4. 固定边把流程带回 `agent`：这次 LLM 看到的对话里已经有了两个工具的结果，直接生成最终回答，回复里**没有** `tool_calls`。
5. `should_continue` 返回 `END`，图结束。

真实输出（节选）：

```
================================== Ai Message ==================================
Tool Calls:
  get_weather (call_00_...)
    city: Beijing
  add (call_01_...)
    a: 23
    b: 19
================================= Tool Message =================================
Sunny, 25°C
================================= Tool Message =================================
42.0
================================== Ai Message ==================================
Here are the answers:
1. **Weather in Beijing**: ☀️ Sunny and 25°C.
2. **23 + 19 = 42** 🎉
```

`agent` 节点在这次 `invoke()` 里一共被执行了**两次**——这是 示例 1、示例 2 里从未发生过的事，因为它们的每个节点在一次 `invoke()` 里最多跑一次。

## 安全网：`recursion_limit`

万一 LLM 一直不停地请求工具（比如陷入某种循环推理），图不会无限跑下去——LangGraph 默认给每次 `invoke()` 设了 25 步的递归上限，超过会抛 `GraphRecursionError`。这是循环类图必须有的兜底，写这类 Agent 时不需要自己再实现一个计数器。

## 和前两个 示例 的关键区别

| | 示例 1 | 示例 2 | 示例 3 |
|---|---|---|---|
| 图的形状 | DAG，纯分支 | DAG，纯分支 | 有循环 |
| State 更新方式 | 整字段覆盖 | 整字段覆盖 | `messages` 用 `add_messages` 追加 |
| 一次 invoke 里同一节点执行次数 | 最多 1 次 | 最多 1 次 | 可能多次 |
| 谁决定"是否结束" | 图结构本身固定 | 图结构本身固定 | LLM 每一轮自己决定 |

## 下一步可以扩展的方向

- 用 `langgraph.prebuilt.ToolNode` 和 `create_react_agent` 替换手写的 `call_tools`/`agent`/接线——这几行代码等价于本 示例 手动搭的整张图，官方封装省掉了样板代码，但理解了这个 示例 之后再用封装会更清楚它内部在做什么。
- 加一个 checkpointer（`builder.compile(checkpointer=...)`），让多轮对话在进程重启后还能接着聊，`thread_id` 对应一段独立的对话历史。
- 在 `tools` 之前插一个人工审核节点（human-in-the-loop，`interrupt()`），执行敏感工具前先暂停等人确认。
- 把 `get_weather` 换成真实的天气 API 调用，体会"工具的实现细节对图结构完全透明"这件事——图只关心工具的名字、参数 schema 和返回值。
