# 01：Agent 是循环，不是魔法

Agent 最小定义不是“能聊天的模型”，而是一个循环：

```text
observe -> decide -> act -> observe -> ...
```

在量化研究里，这个循环必须受约束：Agent 可以决定下一步调用哪个工具，但工具的数值计算必须是确定性的，循环也必须有最大步数或明确终止状态。

## 运行

```bash
python agent_loop.py
```

这个示例不用 LLM，只用一个规则模型模拟 Agent 决策。它会观察研究请求，决定先加载价格，再计算动量，最后输出摘要。

## 你应该观察什么

- `observe` 读取当前 state。
- `decide` 根据缺失信息选择下一步 action。
- `act` 调用确定性工具更新 state。
- 循环在 `done` 状态或最大步数处停止。

这就是后续 LangGraph Agent 的最小骨架。
