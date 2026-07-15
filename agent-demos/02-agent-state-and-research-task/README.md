# 02：Agent State 应该是研究任务，不只是聊天记录

很多 Agent 示例把 state 设计成 `messages`。这对聊天有用，但量化研究需要更结构化的状态：研究目标、股票池、时间区间、候选因子、artifact、指标、审批状态。

## 运行

```bash
python research_state.py
```

这个示例定义一个 `ResearchState`，并用几个确定性节点逐步填充它。

## 新增概念

State 不是越大越好。大型 DataFrame、模型文件、回测明细不应该长期放进 State；State 应保存小型摘要和 artifact 引用。
