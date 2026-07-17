# 10：配置驱动的 Qlib 因子评估流程

Qlib 正式研究经常由配置描述数据、表达式、标签、模型、回测和记录方式。这节用一个 Python `CONFIG` dict 串起因子评估闭环，让配置和执行逻辑分离。

## 核心流程图

```text
CONFIG
  -> factor_expression
  -> label_expression
  -> evaluate_factor
  -> D.features
  -> coverage / IC / RankIC / ICIR / quantile returns
  -> artifacts/config.json
  -> artifacts/metrics.json
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python config_driven_alpha_workflow.py
```

运行后生成：

```text
artifacts/qlib_factor_eval_001/
├── config.json
└── metrics.json
```

## 配置控制了什么

脚本顶部的 `CONFIG` 是最小实验配置：

```python
CONFIG = {
    "experiment_id": "qlib_factor_eval_001",
    "factor_expression": "$close / Ref($close, 20) - 1",
    "label_expression": "Ref($close, -5) / $close - 1",
    "topk": 50,
    "cost_rate": 0.001,
}
```

当前脚本主要使用 `factor_expression` 和 `label_expression` 做预测层评估。`topk` 和 `cost_rate` 保留为后续策略层评估配置，完整组合回测见第 12 节。

## 核心原理

配置驱动的价值不是“少写代码”，而是让每次实验可以复查：

```text
候选表达式
  -> 固定标签
  -> 固定市场和时间区间
  -> 固定评估函数
  -> 固定输出目录
```

自动因子挖掘系统尤其需要这个边界。Agent 可以生成候选表达式，但评估逻辑和记录格式应保持确定。

## 下一步

进入 `11-alpha158-alpha360-feature-sets`，查看 Qlib 官方预定义 feature set 如何被组织成 DataHandler。
