# 08：把一次性脚本变成可追踪实验

如果一个研究脚本只在终端打印几行结果，它很快就会失去审计价值。你过两天很难回答：当时用了哪些特征、哪个标签、哪个时间段、产生了什么预测文件、指标是多少。Qlib 的 Recorder/Experiment 就是为了解决这个问题。

本节不用真实 Qlib Recorder，而是用本地 JSON/CSV 模拟最小实验记录。这样先理解“该记录什么”，再理解“Qlib 怎么记录”。

## 这个示例想说明什么

一个最小实验记录至少包含三类东西：

- params：实验配置，例如模型、特征、标签、时间段。
- metrics：关键指标，例如 mean IC、样本数、收益。
- artifacts：可复查文件，例如 predictions、backtest、模型文件。

没有这些记录，研究结果就是一次性输出，不是可复现实验。

## 运行方式

```bash
python recorder_and_experiment.py
```

运行后会生成：

```text
artifacts/exp_001/
├── params.json
├── metrics.json
└── predictions.csv
```

`artifacts/` 已被 `.gitignore` 忽略，因为它是运行产物，不是源码。

## 代码结构

脚本先加载一份模拟预测表：

```python
date,symbol,score,label
```

然后计算每日 IC 的均值：

```python
daily_ic = predictions.groupby("date").apply(...)
```

接着写三类产物：

```python
predictions.to_csv(...)
params.json
metrics.json
```

这就是 Recorder 的最小精神：**代码生成结果，同时生成足够元数据让结果能被复查**。

## 为什么 Qlib 需要 Recorder

真实 Qlib 工作流里，一个实验可能涉及：

- 数据 handler 配置
- Dataset segments
- 模型参数
- 训练过程
- 预测结果
- SignalRecord
- Portfolio analysis
- 图表和指标

如果这些都靠手动命名文件，很快会失控。Recorder 提供统一实验管理，让你能回到某次实验，重新加载指标和 artifact。

## 常见坑

- 只保存最终指标，不保存预测明细。
- 保存了 artifact，但没有记录生成它的参数。
- 多次运行覆盖结果，却没有实验 ID。
- 把临时运行产物提交进 Git。
- 只记录好结果，不记录失败实验。

## 下一步

进入 `09-strategy-and-backtest`。有了预测分数和实验记录之后，下一步是把分数转成策略，并接受交易成本检验。
