# 06：Qlib 单因子评估

这节把一个候选 Qlib 表达式和一个未来收益标签对齐，计算 coverage、IC、RankIC、ICIR 和分组收益。

## 核心流程图

```text
factor expression + label expression
  -> D.features([factor, label])
  -> dropna / 对齐 datetime, instrument
  -> 每日横截面 corr(score, label)
  -> IC / RankIC / ICIR
  -> 每日分组收益
  -> JSON metrics
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python factor_evaluation.py
```

可选传入候选表达式：

```bash
QLIB_FACTOR_EXPR='$close / Ref($close, 20) - 1' \
QLIB_LABEL_EXPR='Ref($close, -5) / $close - 1' \
python factor_evaluation.py
```

## 指标含义

- `coverage`：表达式计算后非空样本占比。
- `ic_mean`：每日 Pearson IC 的均值。
- `rank_ic_mean`：每日 Spearman RankIC 的均值。
- `icir`：IC 均值除以 IC 标准差。
- `quantile_return_mean`：按因子值分组后的未来收益均值。

## 核心原理

IC 衡量的是预测层质量，不是策略收益：

```text
factor(datetime, instrument)
  -> 当日横截面排序/数值
  -> 与未来 label 做相关性
  -> 判断信号是否有预测关系
```

后续还需要策略、换手、成本和 benchmark 检验。

## 常见坑

- 横截面标的太少时计算 IC 没有意义。
- 只看平均 IC，不看稳定性。
- 用最终测试集反复筛因子。
- 因子方向没有统一，导致正负号解释混乱。

## 下一步

进入 `07-model-training-baseline`，把多个 Qlib 特征放进模型，生成样本外预测分数。
