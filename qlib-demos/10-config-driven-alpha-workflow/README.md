# 10：用配置串起完整 Alpha Workflow

Qlib 正式项目经常是 config/task 驱动的：数据、特征、标签、模型、时间切分、记录器、回测参数都写进配置，再由 workflow 执行。这个示例用一个 Python dict 模拟配置驱动的最小 Alpha 研究闭环。

它不是 Qlib 原生 workflow 的替代品，而是进入原生配置前的可读版本：你能一眼看到配置如何影响每个步骤。

## 这个示例想说明什么

到这里为止，前 9 节已经分别讲过：

- 数据入口
- 表达式和特征
- Handler/Dataset
- 标签和时间切分
- 因子评估
- 模型训练
- 实验记录
- 策略回测

第 10 节把这些拼成一条完整流程：

```text
config
  -> load data
  -> build features and label
  -> split train/test
  -> train model
  -> predict
  -> evaluate IC
  -> top-k backtest
  -> write artifacts
```

## 运行方式

```bash
python config_driven_alpha_workflow.py
```

运行后生成：

```text
artifacts/config_alpha_001/
├── config.json
├── metrics.json
├── predictions.csv
└── backtest.csv
```

输出会打印：

```text
metrics: {'mean_ic': ..., 'total_net_return': ..., 'prediction_rows': ...}
artifacts: ...
```

## 配置控制了什么

脚本顶部的 `CONFIG` 是整个实验的最小配置：

```python
CONFIG = {
    "experiment_id": "config_alpha_001",
    "features": ["momentum_3d", "volume_change_3d"],
    "label": "next_1d_return",
    "train_end": "2024-01-09",
    "test_start": "2024-01-10",
    "topk": 1,
    "cost_rate": 0.001,
}
```

这几个字段分别影响：

- 生成哪些特征。
- 用哪个标签训练。
- 训练期和测试期怎么切。
- 策略每天选几只股票。
- 换手成本怎么扣。
- artifact 写到哪个实验目录。

真实 Qlib 项目里，这些通常会放进 YAML 配置或 task dict。

## 为什么配置驱动很重要

当你只有一个脚本时，硬编码参数还能忍。但研究一旦进入多实验阶段，配置驱动有几个明显好处：

- 实验之间差异清楚。
- 参数可以被 Recorder 记录。
- 同一 workflow 可以重复运行不同配置。
- 训练、预测、回测产物可以按 experiment_id 管理。
- 更容易接入自动化搜索或 Agent 编排。

## 这条 workflow 的边界

这个示例仍然很小，刻意没有处理：

- 真实 Qlib `DatasetH`
- 真实模型库如 LightGBM
- Qlib Recorder
- 原生 backtest engine
- benchmark 和风险分析
- 大规模股票池

它的价值在于把“完整 Alpha 研究流程”压缩成一个可读脚本。下一步如果继续扩展，应该把每个手写组件逐步替换为 Qlib 原生组件，而不是改变研究语义。

## 常见坑

- 配置里写了 feature，但代码里实际没用。
- 只保存 metrics，不保存 config。
- 改了 train/test 日期，却复用了旧 artifact。
- 把 strategy 参数和 model 参数混在一起。
- 根据 test 结果反复修改配置，没有记录尝试次数。

## 到这里你应该掌握什么

完成 10 个示例后，你应该能解释：

- Qlib 数据入口为什么需要 `provider_uri`。
- `$close`、`Ref`、`Mean` 这类表达式对应什么计算。
- Handler 和 Dataset 的职责边界。
- 为什么标签和时间切分是核心风控点。
- IC、Rank IC 和回测收益分别回答什么问题。
- 为什么需要 Recorder/Experiment。
- 为什么正式 Qlib 项目常采用配置驱动 workflow。
