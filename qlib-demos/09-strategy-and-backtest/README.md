# 09：从预测分数到策略回测

模型输出 `score` 之后，研究还没有结束。分数只是排序信号，必须经过策略规则、持仓构造和交易成本，才会变成可以讨论的回测收益。

这一节用最小 top-k 策略说明这个转换过程。真实 Qlib 中可以进一步映射到 `TopkDropoutStrategy` 和 backtest 组件。

## 这个示例想说明什么

策略规则明确写成：

- 每天按 `score` 从高到低排序。
- 选排名最高的 1 只股票。
- 持有到下一日，收益用 `label` 表示。
- 如果和上一天持仓不同，就产生换手。
- 换手按 10bp 成本扣减。

这几个步骤比模型本身更接近交易现实。很多看起来不错的模型分数，一旦加上换手和成本，可能就失效。

## 运行方式

```bash
python strategy_and_backtest.py
```

输出包括：

```text
date, symbol, score, label, turnover, cost, net_return, equity
```

最后打印总成本后收益：

```text
total net return: ...
```

## 时间线怎么理解

同一行可以这样读：

```text
date = 信号日
score = 信号日产生的预测分数
label = 下一持有期实现收益
net_return = label - turnover cost
```

真实交易里还要区分信号生成时间、下单时间、成交价格、停牌涨跌停、冲击成本等。本例只保留最小时间线，避免一开始就陷入完整交易模拟。

## 策略核心代码

每天选 score 最高的一只：

```python
picks = pred.sort_values(["date", "score"], ascending=[True, False]).groupby("date").head(1)
```

判断是否换仓：

```python
picks["turnover"] = (picks["symbol"] != picks["symbol"].shift(1)).astype(float)
```

扣成本并计算净值：

```python
picks["net_return"] = picks["label"] - picks["cost"]
picks["equity"] = (1 + picks["net_return"]).cumprod()
```

## 和 Qlib Strategy/Backtest 的关系

这个脚本是手写最小版。Qlib 原生策略/回测会更完整地处理：

- top-k/dropout 换仓规则
- benchmark
- 交易日历
- 成本配置
- portfolio analysis
- report artifacts

但理解手写版很重要，因为它让你知道 Qlib 回测结果背后到底在做哪些动作。

## 常见坑

- 把模型 IC 当成策略收益。
- 忽略换手率，尤其是每天全量换仓的策略。
- 成本用 0，导致结果虚高。
- 信号日和成交日混在一起。
- 只看累计收益，不看回撤、波动和风险暴露。

## 下一步

最后进入 `10-config-driven-alpha-workflow`。那里会用一个配置对象串起数据、特征、模型、评估、回测和 artifact 输出，模拟 Qlib 正式项目常见的配置驱动方式。
