# 11：Agent 实验记录器

Agent 每做一次研究，都应该留下可复查记录：输入、计划、工具调用、指标、artifact、失败原因。

## 运行

```bash
python agent_experiment_recorder.py
```

脚本会生成 `artifacts/experiment.json`。

## 新增概念

没有记录的 Agent 研究不可复现；不可复现的结果不能进入决策。
