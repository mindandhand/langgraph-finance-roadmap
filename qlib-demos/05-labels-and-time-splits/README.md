# 05：标签和时间切分

这节用 Qlib 表达式同时读取特征和未来收益标签，重点检查金融时间序列任务里的时间语义。

## 核心流程图

```text
Qlib expressions
  -> feature: "$close / Ref($close, 20) - 1"
  -> label: "Ref($close, -5) / $close - 1"
  -> D.features 对齐 datetime / instrument
  -> 按时间切 train / test
  -> 检查 feature 只看过去、label 只用于训练和评估
```

单行样本的时间线：

```text
t-20 ... t-1, t
  -> feature 在信号日 t 可知
  -> label 使用 t 之后 5 个交易周期的收益
  -> 模型训练时学习 feature(t) 和 label(t) 的关系
  -> 实盘预测时只能看到 feature(t)
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python labels_and_time_splits.py
```

## 为什么不能随机切分

金融样本必须按时间切分：

```text
过去数据 -> train
未来数据 -> test
```

随机切分会让训练集看到测试期之后的市场状态，造成回测结果虚高。

## 你应该检查什么

- train/test 日期是否不重叠。
- test 是否晚于 train。
- feature 表达式是否只使用当前和历史数据。
- label 表达式是否没有进入 feature 列。
- 切分前后索引仍然是 `datetime, instrument`。

## 下一步

进入 `06-factor-evaluation`，用同样的 feature / label 对齐结果计算 IC、RankIC 和分组收益。
