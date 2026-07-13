# LangGraph + 真实 LLM 调用：把节点从"拼字符串"换成"调用 Claude"

在 [示例 1](../01-hello-graph) 里，我们搭了一张最小的图，节点只做字符串拼接，路由靠的是初始状态里写死的 `mood` 字段。这篇文档讲的是 `llm_graph.py`：同一套 State / Node / Edge / Graph 接线方式，但节点内部真正调用了 Claude，而且**路由的判断依据也变成了 LLM 自己产出的结果**。

## 这个 示例 想说明什么

示例 1 的结尾提到过一句话：把节点的函数体换成一次 LLM 调用，图的接线方式完全不用变。这个 示例 就是把这句话落地：

```python
# 示例 1 的节点：纯本地计算
def greet(state: State) -> dict:
    return {"message": f"Hello, {state['name']}!"}

# 示例 2 的节点：一次真实的 LLM 调用
def classify_sentiment(state: State) -> dict:
    response = model.invoke(prompt)
    return {"sentiment": extract_text(response.content).strip().lower()}
```

两个函数的**签名和返回方式**是一样的——都是 `(state) -> dict`，只更新自己关心的字段。区别只在于函数体里数据是怎么算出来的。这意味着你已经掌握的"State 在流动、Node 在加工、Edge 决定流向"的心智模型，不需要因为引入了 LLM 而重新学一遍。

## 图结构

```
START -> classify_sentiment -> route_by_sentiment -> positive_reply -> END
                                                    -> negative_reply -> END
```

三个节点，一次条件路由，整张图会产生 **两次真实的 API 调用**（一次分类，一次生成回复）。

## 逐个节点拆解

### `classify_sentiment` —— LLM 调用 #1，产出路由依据

```python
def classify_sentiment(state: State) -> dict:
    prompt = (
        "Classify the sentiment of this message as exactly one word, "
        f"either 'positive' or 'negative':\n\n{state['user_input']}"
    )
    response = model.invoke(prompt)
    sentiment = extract_text(response.content).strip().lower()
    return {"sentiment": sentiment}
```

`model.invoke(prompt)` 返回一个 `AIMessage`，文本在 `.content` 里。这个节点做的事情和 示例 1 的 `greet` 一模一样——读 State，算一个值，写回 `dict`——唯一区别是"算"这一步现在是网络调用。

> **一个真实踩到的坑**：`.content` 不总是字符串。默认关闭思考模式的 Claude 返回纯字符串，但只要模型开启了 extended thinking（比如某些代理端点默认打开），`.content` 就会变成一个 block 列表：`[{"type": "thinking", ...}, {"type": "text", "text": "positive"}]`。直接对它调用 `.strip()` 会报 `AttributeError: 'list' object has no attribute 'strip'`。示例 里的 `extract_text()` 就是为了兼容这两种情况——判断类型，如果是列表就只拼接 `type == "text"` 的 block。这是把 LangChain 输出当函数返回值处理时最容易被文档忽略、但实际运行时一定会遇到的细节。

### `route_by_sentiment` —— 路由函数，读的是 LLM 的输出

```python
def route_by_sentiment(state: State) -> str:
    return "positive_reply" if state["sentiment"] == "positive" else "negative_reply"
```

对比 示例 1 的 `route_by_mood`：那里的 `state["mood"]` 是调用方在 `invoke()` 时手动传进去的固定值；这里的 `state["sentiment"]` 是上一个节点用 LLM **现算出来**的。路由函数本身完全不知道、也不需要知道这个区别——它只关心 State 里有没有这个字段。这就是"State 是流水线上的包裹"这个比喻的价值：产生数据的方式可以随意替换，读数据的一方不用改。

### `positive_reply` / `negative_reply` —— LLM 调用 #2，生成最终回复

```python
def positive_reply(state: State) -> dict:
    prompt = f"Reply enthusiastically to: {state['user_input']}"
    response = model.invoke(prompt)
    return {"reply": extract_text(response.content)}
```

两个节点结构完全一样，只有 prompt 里的语气要求不同。走到这一步说明路由已经决定好了，图不会同时执行这两个节点。

## 一次 `invoke()` 的完整执行轨迹

以 `graph.invoke({"user_input": "I just got promoted!", "sentiment": "", "reply": ""})` 为例：

1. `START` → `classify_sentiment`：调用 Claude，得到 `"positive"`，State 变成 `{..., "sentiment": "positive"}`。
2. `route_by_sentiment` 读到 `sentiment == "positive"`，返回字符串 `"positive_reply"`。
3. 图跳到 `positive_reply` 节点：调用 Claude，生成一段热情的回复，State 变成 `{..., "reply": "..."}`。
4. 到达 `END`，`invoke()` 返回最终的 State。

整个过程里 State 只在累加字段，从来没有被整体替换过——这也是为什么最后 `result["user_input"]` 依然能读到最初传入的原文。

## 运行前准备

```bash
pip install langgraph langchain-anthropic python-dotenv
```

在 [`langgraph-demos/.env`](../.env)（仓库根目录的上一层，已加入 `.gitignore`）里填入：

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=   # 可选，走自建/代理端点时才需要
```

`llm_graph.py` 启动时会用 `load_dotenv()` 自动读取这个文件，然后：

```bash
python llm_graph.py
```

### 实际跑起来的输出

```
[input] I just got promoted!
[sentiment] positive
[reply] Congratulations! That's absolutely amazing news! ...

[input] My cat ran away yesterday.
[sentiment] negative
[reply] I'm so sorry to hear that. That's truly heartbreaking...
```

两次真实调用，`sentiment` 分别被分类成 `positive` / `negative`，图也确实按预期各自走到了对应的回复节点。

### 如果用了 SOCKS 代理

如果你的网络环境设置了 `ALL_PROXY=socks5://...` 之类的环境变量，`httpx`（LangChain 底层用的 HTTP 客户端）需要额外的依赖才能走 SOCKS：

```bash
pip install "httpx[socks]"
```

否则会报 `ImportError: Using SOCKS proxy, but the 'socksio' package is not installed`。

## 和 示例 1 的关键区别

| | 示例 1 | 示例 2 |
|---|---|---|
| 节点做什么 | 字符串拼接 | 调用 `ChatAnthropic` |
| 路由依据 | 初始状态里写死的 `mood` 字段 | LLM 自己判断出的 `sentiment` |
| 每次 `invoke` 的开销 | 纯本地计算，毫秒级 | 1~2 次真实 API 调用，有网络延迟和 token 费用 |
| 确定性 | 完全确定 | LLM 输出有一定随机性，`sentiment` 的解析依赖字符串匹配 |

最后一点值得注意：`classify_sentiment` 用 `response.content.strip().lower() == "positive"` 这种字符串匹配来判断分类结果，如果 LLM 偶尔多说了几个字（比如返回 `"Positive."` 而不是 `"positive"`），匹配就可能失手。这是把 LLM 输出当"控制流依据"时最常见的坑，下面的扩展方向第一条就是针对它的。

## 下一步可以扩展的方向

- 把 `classify_sentiment` 换成结构化输出（`with_structured_output` + Pydantic 模型），用类型化字段代替字符串匹配，从根上避免解析出错。
- 给 `positive_reply` / `negative_reply` 加一个"调用工具"的分支，就是最基础的 ReAct Agent 雏形。
- 用 `graph.stream(...)` 代替 `graph.invoke(...)`，可以边生成边看到每个节点的输出，适合调试和展示中间过程。
- 给图加一个 checkpointer（`builder.compile(checkpointer=...)`），让多轮对话可以在进程重启后继续——这是 LangGraph 相对纯手写调用链的核心优势之一。
