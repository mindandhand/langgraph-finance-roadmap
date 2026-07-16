# 多 Agent 审查：不是投票，是分权

这篇文档讲的是 `multi_agent_review.py`。它演示量化研究里多 Agent 最有价值的一种用法：**把提出结论、审查证据、挑战假设分给不同角色**。

多 Agent 不是让几个模型围在一起聊天，也不是少数服从多数。量化研究的最终裁决应该来自数据、统计、回测和人工判断。多 Agent 的作用是降低遗漏和确认偏误。

## 为什么这里用 LangGraph

本节有多个角色节点，每个节点负责不同审查维度：

```text
researcher
  ↓
reviewer
  ↓
red_team
  ↓
synthesize
```

这已经是图工作流，而不是单个函数。LangGraph 的价值在于：

- 每个角色节点只写自己的输出字段。
- State 保留原始 claim 和各角色 findings。
- `synthesize` 可以基于结构化 findings 做裁决。
- 后续可以改成并行审查、人工审批或失败重跑。

## ReviewState：多 Agent 共享事实，不共享职责

```python
class ReviewState(TypedDict):
    claim: dict
    researcher_claims: list[dict]
    reviewer_findings: list[dict]
    red_team_findings: list[dict]
    decision: str
```

`claim` 是待审查的研究声明，例如：

```python
{
    "factor": "momentum_5d",
    "ic": 0.018,
    "rank_ic": 0.021,
    "rows": 80,
    "backtest_done": False,
    "cost_checked": False,
}
```

三个角色都看同一个 claim，但写入不同字段。这样可以避免角色混在一起：Researcher 不负责挑刺，Reviewer 不负责美化结论，Red-Team 不负责批准。

## Researcher：提出支持性说法

```python
def researcher(state: ReviewState) -> dict:
    return {
        "researcher_claims": [{
            "role": "researcher",
            "statement": f"{claim['factor']} has IC={claim['ic']:.4f}",
            "evidence": {"ic": claim["ic"], "rank_ic": claim["rank_ic"]},
        }]
    }
```

Researcher 的职责是把研究发现表达清楚，并附带证据字段。它天然容易偏向“这个因子有用”，所以它不应该拥有最终批准权。

## Reviewer：检查证据完整性

Reviewer 检查的是研究声明是否达到最低证据要求：

- 样本数是否足够。
- 是否已经做组合回测。
- IC 是否太弱。

本例中，如果 `rows < 120` 或缺少 backtest，就会产生 high severity finding。

这类检查非常适合工具化，因为它们不是风格偏好，而是研究质量门槛。

## Red-Team：主动找失败路径

Red-Team 检查的是结论可能失效的原因：

- 成本敏感性是否缺失。
- 动量因子是否可能依赖市场状态。
- 是否可能由少数时期贡献。
- 是否存在容量、流动性或风险暴露问题。

本例只实现了两个规则，但输出是结构化 finding：

```python
{"severity": "high", "message": "cost sensitivity is missing"}
```

结构化输出比自然语言争论更适合进入后续决策。

## synthesize：不是多数投票

```python
decision = "requires_more_evidence" if high_findings else "can_continue_to_human_review"
```

只要存在 high severity 缺口，就不能因为 Researcher 语气积极而通过。量化研究里的冲突应该按证据处理：

- 数值冲突：重新运行确定性工具。
- 数据冲突：检查数据版本和时间对齐。
- 统计解释冲突：补充检验或披露不确定性。
- 经济解释冲突：保留不同解释并继续验证。

## 实际运行

```bash
python multi_agent_review.py
```

你会看到类似输出：

```text
researcher_claims: [...]
reviewer_findings: [{'severity': 'high', 'message': 'sample is too short'}, ...]
red_team_findings: [{'severity': 'high', 'message': 'cost sensitivity is missing'}, ...]
decision: requires_more_evidence
```

这个结果不是投票结果，而是证据门槛的结果。

## 常见坑

- 让所有 Agent 做同一件事，只是换个角色名。
- 用多数投票替代证据缺口检查。
- Reviewer 也参与生成候选因子，角色混乱。
- Red-Team 只输出泛泛风险，不绑定具体字段。
- 多 Agent 增加成本，但没有提高研究质量。

## 下一步

多 Agent 审查会产生更多记录。下一节 `11-agent-experiment-recorder` 讲如何保存计划、工具调用、指标、artifact 和最终决策。
