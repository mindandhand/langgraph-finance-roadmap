# 09：从 Qlib score 到简化 top-k 回测

这节仍然使用 Qlib provider 和表达式生成 `score` / `label`，但回测逻辑保持轻量，目的是先看清“分数如何变成组合收益”。完整 Qlib 原生组合回测放在 `12-native-backtest-architecture`。

## 核心流程图

```text
score expression + label expression
  -> D.features([score, label])
  -> 每日按 score 排序
  -> 选 top-k
  -> 计算持有期 label 均值
  -> 根据持仓变化估算 turnover
  -> 扣交易成本
  -> net_return / equity
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python strategy_and_backtest.py
```

可选参数：

```bash
QLIB_SCORE_EXPR='$close / Ref($close, 20) - 1'
QLIB_LABEL_EXPR='Ref($close, -2) / Ref($close, -1) - 1'
QLIB_TOPK=50
QLIB_COST_RATE=0.001
```

## 核心原理

预测层和策略层是两件事：

```text
score
  -> 选股规则
  -> 持仓集合
  -> 换手
  -> 成本
  -> 组合收益
```

一个因子可能 IC 不错，但如果换手过高或收益集中在不可交易标的上，策略层结果仍可能不好。

## 和第 12 节的区别

本节是简化 top-k 检验，只估算换手和成本。

第 12 节使用 Qlib 原生：

```text
SignalRecord
  -> TopkDropoutStrategy
  -> SimulatorExecutor
  -> Exchange / Account
  -> PortAnaRecord
```

## 常见坑

- 把 IC 当成策略收益。
- 忽略换手率。
- 成本设为 0 后直接下结论。
- 没有区分信号、策略和成交。

## 下一步

进入 `10-config-driven-alpha-workflow`，把因子评估流程配置化，为自动评估服务做准备。
