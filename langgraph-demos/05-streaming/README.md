# LangGraph + 流式输出：不用等图跑完就能看到结果

前四个 示例 全部用 `graph.invoke()`：调用之后阻塞等待，直到图走到 `END`，才拿到完整的最终 State。这篇文档讲的是 `stream_graph.py`——把 示例 3 那个"agent 决定要不要调用工具"的循环图，换一种方式调用：`graph.stream()`。

> 这一版 示例 特意复用了 示例 3 的多节点循环图（而不是 示例 4 那种一步就完事的单节点聊天图），并且给每个输出片段都打上了时间戳。原因很直接：如果图只有一步、回答又很短，`invoke()` 和 `stream()` 打印出来的东西几乎没区别，看不出"流式"到底流在哪。有了多步骤 + 时间戳，`stream()` 和 `invoke()` 的差异才是**肉眼可见、不需要在真终端里盯着看逐字蹦出来**才能确认的。

## 这个 示例 想说明什么

图本身和 示例 3 完全一样，一个节点都没多加：

```python
def agent(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

`agent` 节点还是老老实实调用 `model.invoke(...)`。流式输出不是节点要支持的能力，而是**调用图的方式**从 `invoke()` 换成 `stream()`。这一点值得强调，因为很容易误以为要为了"支持流式"去改写节点逻辑——实际上完全不需要。

## 两种 `stream_mode`

### `stream_mode="updates"` —— 按节点粒度看进度

```python
for chunk in graph.stream(inputs, stream_mode="updates"):
    for node_name, update in chunk.items():
        ...
```

每当图里**某个节点执行完**，就吐出一个 `{节点名: 这个节点返回的更新}` 的 chunk。示例 3 那种"agent → tools → agent"的循环图，正好能让你在真正跑第二次 LLM 调用、拿到最终答案*之前*，先看到第一轮的"我要调用哪些工具"和工具的执行结果。

### `stream_mode="messages"` —— 按 token 粒度看 LLM 生成过程

```python
for token, metadata in graph.stream(inputs, stream_mode="messages"):
    ...
```

这个模式更细：不是等某个节点整体执行完，而是**只要图里任何一次 LLM 调用在吐 token，就实时吐给你**。`metadata["langgraph_node"]` 会告诉你这个 token 来自哪个节点。

最值得注意的一点：`agent` 节点里用的是 `model.invoke(...)`（一次性拿到完整回复），不是 `model.stream(...)`。但 `graph.stream(stream_mode="messages")` 依然能拿到逐 token 的流——LangGraph 在背后接管了节点内部发生的 LLM 调用，把它的流式过程接到了图的流式接口上，节点作者完全不用关心这件事。

## 实际跑起来的输出：`updates` 模式

```
--- stream_mode='updates': one timestamped chunk per finished node ---
[10.46s] [agent] requests tool call(s): get_weather({'city': 'Beijing'}), get_weather({'city': 'Tokyo'}), add({'a': 23, 'b': 19})
[10.46s] [tools] tool result: Sunny, 25°C
[10.46s] [tools] tool result: Cloudy, 20°C
[10.46s] [tools] tool result: 42.0
[11.49s] [agent] Here you go!

- **Beijing**: ☀️ Sunny, **25°C**
- **Tokyo**: ☁️ Cloudy, **20°C**
- **23 + 19** = **42**
```

看时间戳：`agent` 第一次决定调用三个工具、`tools` 执行完三个工具，全部发生在 **10.46s**；但**第二次** `agent`（读了工具结果、给出最终答案）是在 **11.49s** 才出现——中间这 1 秒多，是第二次 LLM 调用真实花掉的时间。如果用 `invoke()`，你要在这 1 秒多里什么都看不到，一直等到最后才能拿到这整段结果；用 `stream(stream_mode="updates")`，"工具调用决定" 和 "工具执行结果" 这两条信息，在最终答案生成*之前*就已经到手了。这才是这个模式真正的用处：**在多步骤的图里，提前看到中间步骤，而不是死等最后一步**。

## 实际跑起来的输出：`messages` 模式（节选）

```
--- stream_mode='messages': one timestamped chunk per LLM token ---
[ 0.92s] [agent] 'Sure'
[ 0.92s] [agent] '!'
[ 0.92s] [agent] ' Let'
[ 0.92s] [agent] ' me'
...
[ 0.97s] [agent] '.'
[ 1.58s] [tools] 'Sunny, 25°C'
[ 1.58s] [tools] 'Cloudy, 20°C'
[ 1.58s] [tools] '42.0'
[ 2.76s] [agent] 'Here'
[ 2.76s] [agent] ' you'
[ 2.78s] [agent] ' go'
...
[ 3.25s] [agent] '!'
```

这段更能说明问题：第一次 `agent` 调用，模型先吐了几个词的"开场白"（"Sure! Let me get that information for you..."），然后才在同一轮里请求工具——这些开场白的 token 是从 **0.92s 到 0.97s** 陆续到达的，不是一次性给你的。`tools` 的三条结果在 **1.58s** 一起出现（工具执行本身不是 LLM 调用，不会被拆成逐 token，一次性就是一条）。第二次 `agent` 从 **2.76s** 开始，又是一路逐词吐到 **3.25s** 结束。整段跨越了三秒多，每个 token 到达的时间点都不一样——这就是"流式"字面意思：数据是**分批、随时间陆续到达**的，不是攒够了一起给你。

## 两个帮助函数：为什么要区分 thinking 和 text

```python
def text_blocks(content):
    """跳过 'thinking' 类型的 block，只 yield 'text' 类型的内容片段。"""
    ...
```

示例 2 里介绍过：这个模型开了 extended thinking，`.content` 不是纯字符串，而是一串 block。流式场景下这一点被放大了——每个 token chunk 都带着 `type` 字段（`"thinking"` 或 `"text"`），如果不过滤，你会把模型的"内心独白"也一个字一个字打印出来。`text_blocks()` 就是专门为流式场景写的过滤器，思路和 示例 2 的 `extract_text()` 一样，只是处理的是"单个 chunk"而不是"完整的一条消息"。

## 和前四个 示例 的关键区别

| | 示例 1-4 | 示例 5 |
|---|---|---|
| 调用方式 | `graph.invoke()` | `graph.stream()` |
| 图的结构 | 各不相同 | 和 示例 3 完全一样（agent/tools 循环） |
| 拿到结果的时机 | 图走到 `END` 才拿到 | 每个节点 / 每个 token 产出时就能拿到 |
| 节点代码需要改吗 | — | 不需要 |

## 下一步可以扩展的方向

- 试试 `stream_mode="values"`：每次 chunk 拿到的是**当前完整的 State**（而不是这一步的增量更新），适合只关心"现在整体状态长什么样"、不关心是哪个节点改的场景。
- `stream_mode` 可以传一个列表，比如 `["updates", "messages"]`，同时拿两种粒度的事件，chunk 会带上 `(mode, data)` 告诉你这条属于哪种模式。
- 如果要在网页或终端里做真正的打字机效果，`text_blocks()` 配合 `print(text, end="", flush=True)` 就是关键——`flush=True` 保证每个片段立刻显示，不被 Python 的输出缓冲攒起来一次性打印。这次为了打印时间戳每条单独一行，牺牲了打字机的视觉效果，实际做 UI 时通常是不换行、直接拼接输出。
