# LangGraph + Send：动态并行 fan-out

前六个 示例 的图，节点数量和连接方式在 `compile()` 的时候就已经固定了。这篇文档讲的是 `fanout_graph.py`——图跑起来之前，**根本不知道 `research_city` 这个节点会被执行几次**：次数是从输入的 `cities` 列表长度动态决定的。而且和 示例 3 的工具调用循环不一样：那里的多个工具调用是在一个 Python `for` 循环里**依次**执行的；这里动态派生出来的分支是**真正并行**执行的——三次慢速的 LLM 调用，花的时间跟一次差不多，而不是三次的总和。

## 这个 示例 想说明什么

```
START -> dispatch -> research_city(city=Paris) -\
                   -> research_city(city=Tokyo) --> END
                   -> research_city(city=Cairo) -/
```

`dispatch` 不是前六个 示例 里那种路由函数——它不返回一个"下一个节点的名字"，而是返回一个 **`Send` 对象的列表**，每个 `Send` 都带着自己独立的输入：

```python
def dispatch(state: OverallState) -> list[Send]:
    return [Send("research_city", {"city": city}) for city in state["cities"]]
```

`Send("research_city", {"city": "Paris"})` 的意思是："在这一步里，用 `{"city": "Paris"}` 作为输入，跑一次 `research_city` 节点"。`dispatch` 返回几个 `Send`，`research_city` 这一步就会被并行触发几次——这个数字直到 `dispatch` 真正执行时才知道，图的静态结构里根本没写死"三次"这个数。

## 两套 State：整体的和每个分支自己的

```python
class OverallState(TypedDict):
    cities: list[str]
    facts: Annotated[list[str], operator.add]

class CityState(TypedDict):
    city: str
```

前六个 示例 都只有一套 State，贯穿整张图。这里第一次出现了两套：

- `OverallState` 是图对外的输入输出，`cities` 是要处理的列表，`facts` 是收集结果的地方。
- `CityState` 是**每个并行分支自己看到的输入**——`Send("research_city", {"city": "Paris"})` 传进去的 `{"city": "Paris"}`，形状对应的正是 `CityState`，而不是整个 `OverallState`。跑 Paris 那个分支的 `research_city`，压根不知道 Tokyo、Cairo 的存在，它只看到自己的 `city` 字段。

## `operator.add` 归约器：并行结果怎么汇总

```python
facts: Annotated[list[str], operator.add]
```

三个并行分支各自跑完 `research_city`，各自返回 `{"facts": ["Paris: ..."]}`、`{"facts": ["Tokyo: ..."]}`、`{"facts": ["Cairo: ..."]}`。如果没有归约器，三次更新会互相覆盖，只剩最后一个。`operator.add` 告诉 LangGraph："这个字段的更新方式是列表拼接"（`operator.add([a], [b])` 就是 `[a] + [b]`）——三次并行更新会被依次拼接成 `["Paris: ...", "Tokyo: ...", "Cairo: ..."]`。这和 示例 3、4 里 `add_messages`（把新消息追加到历史）是同一类机制，只是这次换成了通用的 `operator.add`，处理的是普通列表而不是消息列表。

## 实际跑起来的输出：并行确实更快

脚本先跑了一遍**顺序版本**（一个个 `model.invoke()`）作为对照组，再跑并行版本，两边都打了时间戳：

```
--- sequential baseline: one model.invoke() at a time ---
[12.52s] Paris: The Eiffel Tower was originally built as a temporary structure...
[14.35s] Tokyo: Tokyo was originally a small fishing village called Edo...
[18.41s] Cairo: Cairo is home to Al-Azhar University...

--- parallel fan-out: all three research_city branches at once ---
[ 3.02s] Paris: The Eiffel Tower was almost demolished in 1909...
[ 9.74s] Cairo: Cairo is home to the only surviving Ancient Wonder...
[11.03s] Tokyo: Tokyo has more Michelin-starred restaurants...

sequential total: 18.41s | parallel total: 11.03s
```

顺序版本：三次调用一个接一个，总耗时是三次调用时间的**和**（18.41s）。并行版本：三个 `research_city` 分支同时发起，总耗时约等于**最慢那一个分支单独跑**的时间（11.03s，就是 Tokyo 这一支自己花的时间）——另外两支虽然更早完成，但整体等待的是最慢的那个。这就是并行 fan-out 的收益模型：**总耗时 ≈ 最慢的那个分支，而不是所有分支的总和**。分支数越多、单个分支越慢，这个差距就越明显。

## 和前六个 示例 的关键区别

| | 示例 1-6 | 示例 7 |
|---|---|---|
| 节点执行次数 | 编译时就固定（最多 1 次，或循环到 LLM 决定停） | 运行时才知道，由输入长度决定 |
| 多个分支之间的关系 | 循环是**串行**的（一次只跑一个） | fan-out 出来的分支是**并行**的 |
| State 的形状 | 全图共用一套 | 整体一套（`OverallState`），每个分支自己一套（`CityState`） |
| 结果怎么合并 | `add_messages`（追加消息） | `operator.add`（拼接列表），同一类归约器机制的另一种用法 |

## 下一步可以扩展的方向

- 在 `research_city` 后面加一个真正的"汇总"节点（`facts` 收集完之后，`add_edge("research_city", "summarize")`），用一次 LLM 调用把三条零散事实整理成一段连贯的介绍——这是经典的 map-reduce 模式：`dispatch` 是 map，新加的汇总节点是 reduce。
- 把 `research_city` 换成会失败的操作（比如访问一个不稳定的 API），观察某个并行分支出错时，整个 `invoke()` 是什么行为——这决定了要不要在节点内部自己加 `try/except` 兜底。
- 结合 示例 6 的人工审核：如果并行分支里有些是"敏感操作"（比如同时给多个客户发邮件），可以给每个分支单独接一个 `interrupt()`，实现"逐个批准，其余分支继续并行推进"。
- 试试分支数量本身也是动态计算出来的（比如先用一次 LLM 调用列出"应该调研哪些城市"，再把这个列表传给 `dispatch`），体会"图的形状由上一步的 LLM 输出决定"这件事能做到多灵活。
