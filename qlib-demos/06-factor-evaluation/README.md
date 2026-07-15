# 06：训练模型前，先评估单因子

很多量化研究问题不需要一上来就训练模型。先问一个更基础的问题：这个候选因子和未来收益有没有稳定关系？本节用 3 日动量因子演示最小评估流程。

## 这个示例想说明什么

一个单因子评估至少要回答：

- 因子值和未来收益的线性相关性如何？对应 Pearson IC。
- 因子排序和未来收益排序是否一致？对应 Rank IC。
- 每天买因子最高、卖因子最低，方向是否大致合理？对应 top-minus-bottom。

这些指标不能证明因子未来有效，但能帮助你快速识别明显无效或方向错误的候选。

## 运行方式

```bash
python factor_evaluation.py
```

输出类似：

```text
                  ic  rank_ic  top_minus_bottom
date
2024-01-05 ...
...

mean IC: ...
mean Rank IC: ...
```

这个样本非常小，所以数值只用于理解计算流程，不能解读为真实投资证据。

## 核心计算

先准备因子和标签：

```python
df["factor"] = df["close"] / by_symbol["close"].shift(3) - 1
df["label"] = by_symbol["close"].shift(-1) / df["close"] - 1
```

每天分组评估：

```python
prepare().groupby("date").apply(score_day)
```

Pearson IC：

```python
group["factor"].corr(group["label"])
```

Rank IC：

```python
group["factor"].corr(group["label"], method="spearman")
```

top-minus-bottom：

```python
ranked.iloc[0]["label"] - ranked.iloc[-1]["label"]
```

## IC 和 Rank IC 的区别

Pearson IC 更关注数值关系。如果极端值很大，它会受到明显影响。Rank IC 更关注排序关系，常用于横截面选股，因为很多策略更关心“谁排前面”，而不是因子原始数值相差多少。

如果一个因子 Rank IC 较好，但 Pearson IC 不稳定，可能说明排序有用但尺度不稳。真实研究中还需要检查分组收益、因子覆盖率、行业/市值暴露、换手率和成本。

## 常见坑

- 只看平均 IC，不看每日分布和稳定性。
- 样本太短就下结论。
- 因子方向没统一，导致正负号解释混乱。
- 用同一个最终测试集反复筛因子。
- 忽略交易成本，尤其是高换手因子。

## 下一步

单因子评估之后，进入 `07-model-training-baseline`：把多个特征组合起来，训练一个最小可复现模型，并产生样本外预测分数。
