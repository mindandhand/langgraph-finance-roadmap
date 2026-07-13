# LangGraph 从零到能用：8 个可运行的最小 示例

这是一条循序渐进的 LangGraph 学习路径，每个子目录都是一个**独立可运行**的最小示例，配一篇讲清楚"这一步新在哪"的文章。建议按顺序读，因为后面的 示例 大多复用前面 示例 讲过的东西，只加一个新概念。

## 先搞懂这四个词，剩下的都是排列组合

- **State**：贯穿整张图的共享数据结构，节点读它、写它。
- **Node**：一个函数，`(state) -> dict`，返回自己想更新的字段。
- **Edge**：节点之间怎么连——固定边（`add_edge`）或者条件边（`add_conditional_edges`，用一个路由函数决定走向）。
- **Graph**：把 State/Node/Edge 组装起来，`StateGraph(...).compile()` 得到一个可以 `.invoke()` / `.stream()` 的对象。

LangGraph 的核心建模抽象始终是 State、Node、Edge 和 Graph；Checkpoint、Streaming、Interrupt、Send 和 Subgraph 则进一步定义了图的执行、持久化、并行和组合语义。

## 运行前准备（对所有 示例 通用）

```bash
pip install langgraph langchain-anthropic python-dotenv
```

在这个目录（`langgraph-demos/.env`，已加入 `.gitignore`）里填好：

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=   # 可选，走自建/代理端点时才需要
```

每个 示例 脚本启动时会自动 `load_dotenv()` 读取这个文件，不需要在每个子目录里各放一份。如果你的网络需要走 SOCKS 代理（`ALL_PROXY=socks5://...`），额外装一下：

```bash
pip install "httpx[socks]"
```

## 学习路径

| # | 目录 | 一句话说清楚新在哪 | 依赖谁 |
|---|------|------|------|
| 1 | [`01-hello-graph`](01-hello-graph) | State / Node / Edge / Graph 是什么，纯本地逻辑，不调用任何 LLM | — |
| 2 | [`02-llm-call`](02-llm-call) | 节点内部换成真实 LLM 调用；路由依据从"写死的字段"变成"LLM 自己判断的结果" | 示例 1 |
| 3 | [`03-tool-calling-agent`](03-tool-calling-agent) | 第一次出现**循环边**：`tools -> agent` 连回上游，图能循环到 LLM 自己决定停 | 示例 2 |
| 4 | [`04-checkpointer-memory`](04-checkpointer-memory) | State 能跨越多次 `invoke()` 存活，靠 `checkpointer` + `thread_id` | 示例 1（图结构不变，只加 `compile()` 参数） |
| 5 | [`05-streaming`](05-streaming) | 同一张图（复用 示例 3）换一种调用方式：`graph.stream()`，不用等图跑完就能看到中间结果 | 示例 3 |
| 6 | [`06-human-in-the-loop`](06-human-in-the-loop) | `interrupt()` 让图在敏感操作前真正暂停，`Command(resume=...)` 恢复——必须搭配 checkpointer | 示例 3 + 示例 4 |
| 7 | [`07-parallel-fanout`](07-parallel-fanout) | `Send` 让图动态派生出多个**并行**分支，节点执行次数运行时才确定，不像 示例 3 的循环是串行的 | 示例 3 的循环写法做对照 |
| 8 | [`08-subgraphs`](08-subgraphs) | 把编译好的图直接当成另一张图的节点用——最基础的"多 Agent"组织方式 | 示例 2（分类路由）+ 示例 3（子图本身就是 agent/tools 循环）|

## 概念地图

```
State / Node / Edge / Graph（示例 1）
        │
        ├─ 节点内部换成 LLM 调用，路由依据来自 LLM 输出（示例 2）
        │       │
        │       └─ 加一条循环边，LLM 自己决定要不要再循环一轮（示例 3）
        │               │
        │               ├─ 换一种调用方式：stream() 而不是 invoke()（示例 5）
        │               ├─ 循环前插一个 interrupt() 暂停点（示例 6，还需要 示例 4 的 checkpointer）
        │               ├─ 把整张循环图当积木，复用两份拼进父图（示例 8）
        │               └─ 对照组：循环是串行的，Send 派生的分支是并行的（示例 7）
        │
        └─ State 能不能跨调用存活，取决于 compile() 时加不加 checkpointer（示例 4）
```

## 贯穿多个 示例 的坑（不是 bug，是真实会遇到的事）

- **`.content` 不一定是字符串**：模型开了 extended thinking 时，`AIMessage.content` 是一串 `{"type": "thinking"/"text", ...}` block，不是 str，直接 `.strip()` 会报错。示例 2 开始每个 示例 都写了 `extract_text()`（完整消息用）或 `text_blocks()`（流式单个 chunk 用）来处理这件事。
- **`langchain_core` 的 pydantic v1 兼容警告**：`import langgraph` 在 Python 3.14 + pydantic 2.12 组合下会报一条 `UserWarning`，纯粹是上游库的兼容性提示，跟这些 示例 的正确性无关，每个脚本顶部都用一行 `warnings.filterwarnings(...)` 消掉了。
- **SOCKS 代理**：如果 shell 里设了 `ALL_PROXY=socks5://...`，`httpx`（LangChain 底层用的 HTTP 客户端）需要 `httpx[socks]` 才能连得上，不然会在第一次调用模型时报 `ImportError`。

## 每个 示例 的运行方式都一样

```bash
cd 0X-xxx
python3 xxx_graph.py
```

`06-human-in-the-loop` 例外——它会在终端暂停，等你手动输入 `yes`/`no`。
