# LangGraph + 子图：把一整张图当成一个节点用

前七个 示例 每次都只搭一张图、编译一次、跑一次。这篇文档讲的是 `subgraph_router.py`——搭两个各自完整、能独立工作的小 Agent（都是 示例 3 那种 agent/tools 循环，只是各自绑定一个工具），然后把这两个**已经编译好的图**，当成节点塞进第三张更大的图里，由它决定该把问题交给谁。

## 这个 示例 想说明什么

```
weather_agent：一整张 agent/tools 循环图，工具是 get_weather
math_agent：   一整张 agent/tools 循环图，工具是 add

父图：
START -> classify -> route -> weather_agent -> END
                             -> math_agent    -> END
```

`classify` 和 `route` 这一对，就是 示例 2 的 `classify_sentiment` + `route_by_sentiment` 原样照搬——一次 LLM 调用打标签，一个纯函数读标签决定下一步。真正新的地方在于 `route` 路由**到**的东西：`"weather_agent"` 和 `"math_agent"` 不是写在这张图里的普通节点函数，而是两个**编译好的图**：

```python
weather_agent = make_agent([get_weather])   # 这是 graph.compile() 的返回值
math_agent = make_agent([add])              # 同样是 graph.compile() 的返回值

parent_builder.add_node("weather_agent", weather_agent)  # 直接当节点用
parent_builder.add_node("math_agent", math_agent)
```

`add_node` 通常接收一个普通函数（`(state) -> dict`）。这里传进去的是一个编译好的 `StateGraph`——它同样可以被当成"一个函数"来调用（`.invoke(state)`），所以完全可以塞进 `add_node`，LangGraph 分不出、也不需要分出"这是一个普通节点还是一整张子图"。对父图来说，`weather_agent` 就是一个黑盒：给它一个 State，它自己在内部跑完整套 agent/tools 循环（可能循环好几轮），最后返回一个更新后的 State。

## 为什么可以直接塞进去：State 形状要对得上

```python
class AgentState(TypedDict):          # 两个子图用的
    messages: Annotated[list[BaseMessage], add_messages]

class ParentState(TypedDict):         # 父图用的
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
```

子图的 `AgentState` 和父图的 `ParentState` 都有一个 `messages` 字段，而且用的是**同一个归约器** `add_messages`。子图跑完之后返回的 `{"messages": [...]}` 更新，能被父图按 `messages` 这个字段名、用同样的追加逻辑合并回父图的 State——`topic` 这个父图独有的字段，子图完全不知道它的存在，也不需要知道，子图只管读写自己认识的 `messages`。

这就是"直接把编译好的图塞进 `add_node`"能生效的前提：**子图和父图共享的字段，字段名和归约器要一致**。如果子图的 State 和父图长得完全不一样（比如子图内部叫 `history` 而不是 `messages`），就不能直接塞进去了，得包一层普通的转换节点：

```python
def run_weather_agent(state: ParentState) -> dict:
    sub_result = weather_agent.invoke({"history": state["messages"]})  # 父->子：字段改名
    return {"messages": sub_result["history"]}                         # 子->父：字段改名

parent_builder.add_node("weather_agent", run_weather_agent)  # 包一层普通函数
```

本质上就是手写一个"翻译"节点，在调用子图前后做字段映射。示例 里选择让两个子图的 State 形状和父图完全对齐，就是为了避免这一层，让"子图即节点"这件事看起来更直接。

## 实际跑起来的输出

```
[question] What is the weather in Tokyo?
[routed to] weather_agent
[answer] The current weather in Tokyo is **cloudy** with a temperature of **20°C**.

[question] What is 17 plus 25?
[routed to] math_agent
[answer] 17 plus 25 equals **42**.
```

第一个问题被分类成 `weather`，父图路由到 `weather_agent` 这个子图，子图内部完整跑了一轮"LLM 决定调用 `get_weather` → 执行 → LLM 读结果生成回答"（示例 3 讲过的那整套循环）；第二个问题同理路由到 `math_agent`。从父图的视角看，这两次调用没有任何区别——都是"调用一个节点，等它返回更新后的 State"，至于这个节点内部是一行代码还是一整套循环，父图并不关心。

## 为什么要这么做：子图解决的是什么问题

如果不用子图，你完全可以把 `weather_agent` 和 `math_agent` 内部的节点（`agent`、`tools`）都摊平写进父图里，用更复杂的路由把它们串起来——图不大的时候，这样做完全可行，示例 3 就是这么写的。子图的价值在图变大、变多的时候才明显：

- **复用**：`weather_agent` 这张图本身是完整、可独立测试、可独立运行的，除了塞进这个 示例 的父图，它也可以单独 `weather_agent.invoke(...)`，或者被塞进另一个完全不同的父图。
- **封装**：父图完全不需要知道 `weather_agent` 内部有几个节点、循环了几轮——它只关心"给它 messages，它还我 messages"这一个接口，内部想怎么重构、加节点、换模型，父图代码一行都不用改。
- **可组合的"多 Agent"**：这正是"多 Agent 系统"最常见的实现方式——每个 Agent 是一张独立的图，一个"supervisor"图负责决定该把任务交给哪个 Agent，子图之间互不知道彼此存在。

## 和前七个 示例 的关键区别

| | 示例 1-7 | 示例 8 |
|---|---|---|
| 图的数量 | 一张 | 三张（两个子图 + 一个父图） |
| 节点是什么 | 普通函数 | 普通函数，或者一整张编译好的图 |
| 复用方式 | 图内部的节点函数可以复用（比如 demo3/5/8 都写了相似的 agent/tools 循环） | 整张编译好的图可以被复用，作为另一张图的一个节点 |

## 下一步可以扩展的方向

- 给 `weather_agent`、`math_agent` 各自单独调用 `.invoke()`，不经过父图，验证它们确实是完全独立、可以单测的图。
- 加第三个子图（比如 示例 6 的人工审核 Agent），`classify` 改成三分类，体会子图数量增加时，父图的改动有多小——只需要多一个 `add_node` + 多一条路由分支。
- 用 `StateGraph.add_node` 官方支持的另一种子图写法：如果子图和父图的 State **不完全一致但有共同字段**，可以直接把子图对象传给 `add_node`，LangGraph 会自动按共享字段做部分合并——不需要手写转换节点。查阅 LangGraph 官方文档里 "Subgraphs" 一节，看这条自动映射规则具体的适用边界。
- 结合 示例 7 的并行 fan-out：如果一个问题需要**同时**问 `weather_agent` 和 `math_agent`（而不是二选一），可以把 `route` 换成 `dispatch` 返回多个 `Send`，两张子图并行跑，回答互不干扰地合并到同一个父图 State 里。
