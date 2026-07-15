# 09：单 Agent 因子评估

这节把前面的工具串起来：Agent 选择候选因子，工具计算 factor 和 label，再由评估工具计算 IC / RankIC。

## 运行

```bash
python single_agent_factor_evaluation.py
```

## 新增概念

Agent 写报告，但不自己算指标。报告里的数值必须来自工具输出。
