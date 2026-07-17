# 12：Qlib 原生组合回测

这一节使用 Qlib 原生回测链路，不再手写 `Strategy / Executor / Exchange / Account` 模拟器。

## 核心流程图

```text
Alpha158 / DatasetH
  -> LGBModel
  -> SignalRecord
  -> TopkDropoutStrategy
  -> SimulatorExecutor
  -> PortAnaRecord
  -> portfolio_analysis artifacts
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python native_backtest_architecture.py
```

可选参数：

```bash
QLIB_MARKET=csi300
QLIB_BENCHMARK=SH000300
QLIB_TOPK=50
QLIB_N_DROP=5
QLIB_DEAL_PRICE=close
QLIB_OPEN_COST=0.0005
QLIB_CLOSE_COST=0.0015
```

## 这个示例想说明什么

Qlib 组合回测不是把 `score` 乘以下期收益。`PortAnaRecord` 会基于预测信号调用：

- `TopkDropoutStrategy`：把 score 转成持仓/交易决策。
- `SimulatorExecutor`：按交易日推进模拟执行。
- `Exchange`：处理成交价格、成本、涨跌停等市场规则。
- `Account`：维护现金、持仓、成本和净值。

最终结果保存在 Recorder 的 `portfolio_analysis/` artifact 中，包括：

```text
report_normal_1day.pkl
positions_normal_1day.pkl
indicators_normal_1day.pkl
port_analysis_1day.pkl
```

## 和自动因子评估的关系

`06` 和 `14` 解决的是预测层评估：coverage、IC、RankIC、分组收益。

本节解决的是策略层评估：候选信号经过 top-k、换手、成本和 benchmark 后，是否还能形成可执行组合表现。
