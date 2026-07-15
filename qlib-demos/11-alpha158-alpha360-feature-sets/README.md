# 11：Alpha158 / Alpha360 本质上是什么

很多人第一次看到 `Alpha158`、`Alpha360` 会以为它们是模型、策略或某种神秘 Alpha。它们都不是。它们本质上是 **Qlib 预定义的特征集合 / DataHandler 配置**：用一批 Qlib 表达式从行情字段中生成特征矩阵，再配上标签和处理器，供 Dataset 和模型使用。

这节用一个小脚本拆开它们的思想，并演示如何在同一套机制里加自定义因子。

## 这个示例想说明什么

在 Qlib 源码里，`Alpha158` 和 `Alpha360` 都是 `DataHandlerLP` 的子类。它们内部会构造 `QlibDataLoader`，并把 `feature` 和 `label` 配置交给 loader。官方实现里：

- `Alpha158` 使用一组人工设计的 K 线、价格、成交量、滚动统计和趋势类表达式。
- `Alpha360` 更接近“过去 60 天原始价格/成交量窗口”的展开表示，例如过去多日的 close/open/high/low/vwap/volume 归一化值。

所以更准确的理解是：

```text
Alpha158 / Alpha360
  = 预定义 feature expression 列表
  + 默认 label expression
  + DataHandler 处理流程
```

它们不是“保证有效的因子”，也不是“自动赚钱的模型”。

## 运行方式

```bash
python alpha_feature_sets.py
```

输出会展示：

- 一个简化版 Alpha158 特征配置。
- 一个简化版 Alpha360 特征配置。
- 一组自定义因子表达式。
- 用内置小数据计算出的部分特征。

## Alpha158 怎么理解

Alpha158 的名字来自一个预定义特征集合。真实实现会根据配置生成很多表达式，例如：

- K 线形态：`($close-$open)/$open`
- 当前价格相对收盘价：`$open/$close`
- 滚动均线：`Mean($close, 5)/$close`
- 滚动波动：`Std($close, 20)/$close`
- 趋势斜率：`Slope($close, 20)/$close`
- 过去窗口排名：`Rank($close, 20)`

这些表达式反映的是“从 OHLCV 中系统构造一批候选特征”。它们仍然需要经过 IC、样本外、成本和回测检验。

## Alpha360 怎么理解

Alpha360 更像一个固定长度历史窗口展开：

```text
CLOSE59, CLOSE58, ..., CLOSE0
OPEN59,  OPEN58,  ..., OPEN0
...
VOLUME59, ..., VOLUME0
```

真实 Qlib 实现里，过去 60 天的价格和成交量会按当前 close/volume 做归一化，形成 6 类字段 x 60 天 = 360 个特征。它适合让模型自己从历史窗口里学习模式。

## 自定义因子放在哪里

自定义因子本质上也是表达式。比如：

```text
momentum_5 = $close / Ref($close, 5) - 1
volume_shock_5 = $volume / Mean($volume, 5) - 1
intraday_strength = ($close - $open) / ($high - $low + 1e-12)
```

在真实 Qlib 里，你可以把这些表达式加入 `QlibDataLoader` 的 feature config，或者继承/改造 DataHandler。这个示例用 Pandas 等价实现，重点是说明“自定义因子并不是单独一套系统”，它和 Alpha158/Alpha360 一样，最终都要变成 feature matrix。

## 和自动因子挖掘的关系

自动因子挖掘系统可以让 Agent 或搜索程序提出候选表达式，但表达式是否有效，必须交给确定性评估流程：

```text
候选表达式
  -> 数据对齐和合法性检查
  -> 计算 feature matrix
  -> 构造 label
  -> IC / RankIC / 分层收益
  -> 回测和成本
  -> 记录实验
```

Qlib 适合承担这条链里的确定性执行和评估部分，而不是让 LLM 直接判断因子好坏。

## 常见坑

- 以为 Alpha158/Alpha360 是模型。
- 以为预定义特征集天然有效。
- 只增加表达式，不检查未来函数。
- 自定义因子没有统一命名和版本。
- 自动挖掘只保存“成功因子”，不保存失败候选。

## 下一步

进入 `12-native-backtest-architecture`，把第 9 节的手写回测扩展成 Qlib 原生回测架构里的四个角色：Strategy、Executor、Exchange、Account。
