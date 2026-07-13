# LangGraph + Human-in-the-loop：让图在关键动作前停下来等人

这篇文档讲的是 `review_graph.py`——把 示例 3 的"工具调用循环"和 示例 4 的"checkpointer 记忆"合在一起用，解决一个真实场景：Agent 要发一封邮件（或者删文件、转账……任何有真实副作用的动作）之前，先暂停，等人确认，人说"可以"才真正执行。

## 为什么这个能力必须依赖 checkpointer

"暂停等人"这件事，本质上要求：图在某个节点中途**真的停下来**，把控制权交还给你的代码；然后可能过了几秒、几分钟甚至几天，你的代码再把"人的决定"喂回去，图要能从**暂停的那个精确位置**继续跑，而不是从头再来一遍。

示例 4 已经讲过：State 能不能跨越多次 `invoke()` 存活，全靠 checkpointer。人工审核就是这个能力最典型的应用——没有 checkpointer，图压根没有"暂停后还能接得上"这个选项。

## 新出现的原语：`interrupt()`

```python
from langgraph.types import interrupt

def human_review(state: State) -> dict:
    last_message = state["messages"][-1]
    pending = [{"name": c["name"], "args": c["args"]} for c in last_message.tool_calls]
    decision = interrupt({"pending_tool_calls": pending})
    return {"decision": decision}
```

在节点函数里调用 `interrupt(payload)`，图会立刻冻结在这里——`graph.invoke()` 不会往下走，而是直接返回，返回值里带一个 `"__interrupt__"` 键，值就是你传给 `interrupt()` 的 `payload`。

要continue 这次执行，你需要用**同一个 `thread_id`**再调用一次：

```python
from langgraph.types import Command

result = graph.invoke(Command(resume="approve"), config)
```

`Command(resume=...)` 里的值，就是 `interrupt()` 这次调用的返回值——`human_review` 函数会**从 `interrupt()` 那一行继续往下执行**，`decision` 变量拿到的正是你传的 `"approve"`。这是这个 示例 里唯一一个新概念，其余的图结构（agent/tools 循环、State 的 `messages` 字段）全部照搬 示例 3。

## 图结构：多了一条"拒绝"分支

```
START -> agent -> should_continue -> human_review -> route_after_review -> tools        -> agent -> ...
                                                                          -> reject_tools -> agent -> ...
```

- `should_continue`：和 示例 3 完全一样，看 LLM 的回复有没有 `tool_calls`，有就走向下一步（这里是 `human_review`，示例 3 里是直接 `tools`）。
- `human_review`：调用 `interrupt()` 冻结图，把待执行的工具调用列表交给外面的代码。
- `route_after_review`：读 `state["decision"]`（`human_review` 恢复执行后写入的），决定走 `tools`（真正执行）还是 `reject_tools`（不执行）。
- `reject_tools`：**每一个 `tool_use` 都必须配一个 `tool_result`**，哪怕是被拒绝的——不然下一轮把消息历史发给 Anthropic API 时，格式是不合法的（模型请求了工具，但历史里找不到对应的执行结果）。所以拒绝时依然要生成 `ToolMessage`，只是内容是"User rejected this action."。
- `tools` 和 `reject_tools` 都固定连回 `agent`，和 示例 3 的循环写法一样。

## 主循环：一次拒绝可能不够

```python
result = graph.invoke({"messages": [HumanMessage(question)]}, config)

while "__interrupt__" in result:
    pending = result["__interrupt__"][0].value["pending_tool_calls"]
    print(f"\nThe agent wants to run: {pending}")
    answer = input("Approve? (yes/no): ").strip().lower()
    decision = "approve" if answer in ("y", "yes") else "reject"
    result = graph.invoke(Command(resume=decision), config)
```

用 `while` 而不是 `if`，是因为实测发现：**拒绝一次不代表 Agent 就放弃了**。`reject_tools` 只是往对话历史里加了一条"User rejected this action."，`agent` 节点看到这条消息之后，可能会：

- 换一种措辞，重新请求同一个工具（又会再次触发 `human_review`，需要人再审一轮）
- 反问用户"你希望我怎么调整？"，不再请求工具，图正常走到 `END`

这两种情况在实际跑的时候都遇到过——同一份代码，同样选择"拒绝"，LLM 有时候自己重试，有时候转而向人提问。`while "__interrupt__" in result` 这一行，就是让脚本能应付"审核不止一轮"这种真实情况，而不是假设一次批准/拒绝就能盖棺定论。

## 实际跑起来的输出

**批准路径**（`answer = "yes"`）：

```
The agent wants to run: [{'name': 'send_email', 'args': {'to': 'boss@example.com', ...}}]
Approve? (yes/no): yes
================================== Ai Message ==================================
I've sent an email to **boss@example.com** letting them know you'll be 10 minutes late...
```

**拒绝路径**（`answer = "no"`）：

```
The agent wants to run: [{'name': 'send_email', 'args': {'to': 'boss@example.com', ...}}]
Approve? (yes/no): no
================================== Ai Message ==================================
It looks like the email was rejected. Could you let me know how you'd like to adjust it?
```

这次跑的时候，模型选择了反问而不是重试，图在这里就正常结束了（`should_continue` 判断这条回复没有 `tool_calls`，直接路由到 `END`）——印证了上一节说的：拒绝之后发生什么，是 LLM 自己决定的，不是图结构写死的。

## 和前面 示例 的关键区别

| | 示例 3 | 示例 4 | 示例 6 |
|---|---|---|---|
| 图会不会中途停下来 | 不会，一次 `invoke()` 跑到底 | 不会 | 会，`interrupt()` 主动冻结 |
| 需要 checkpointer 吗 | 不需要 | 需要（记住历史） | 需要（记住"冻结在哪"） |
| 恢复执行的方式 | — | 正常的 `invoke()` | `invoke(Command(resume=...), config)` |
| 谁决定继续还是停止 | LLM（要不要调用工具） | — | 人（`interrupt()` 那一刻） + LLM（`reject_tools` 之后要不要重试） |

## 下一步可以扩展的方向

- 用 `interrupt()` 的返回值携带更丰富的信息，而不只是 approve/reject——比如让人在批准前**修改**工具参数（`decision = interrupt(...)` 拿到的可以是一个带修改后 `args` 的字典），`tools` 节点执行时用人改过的参数而不是 LLM 原始生成的。
- 结合 示例 5 的流式输出：`graph.stream()` 同样支持 `interrupt()`，可以在网页应用里一边流式展示 Agent 的思考过程，一边在需要审核时弹出确认框。
- 只对"敏感"工具触发 `human_review`，其他工具（比如 示例 3 的 `get_weather`）直接放行——在 `should_continue` 里按工具名分流，而不是所有工具调用都强制走审核。
- 换成持久化的 checkpointer（`SqliteSaver`/`PostgresSaver`，示例 4 提到过），审核请求可以真正"挂起几天"，比如生成一个审批链接发给人工，人工点击链接时才触发 `Command(resume=...)`。
