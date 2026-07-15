# 05：标签和时间切分决定研究是否可信

这节专门讲一件事：金融样本不能像普通表格任务那样随便随机切分。你预测的是未来收益，所以特征、标签、训练集和测试集必须有清楚的时间语义。

## 这个示例想说明什么

同一行样本可以这样理解：

```text
date = 信号日
feature_momentum_3d = 信号日及以前可以知道的信息
label_next_return = 信号日之后一个交易日实现的收益
```

模型在 `date` 这一天只能看到特征，不能看到标签。训练集也不能包含测试期之后的信息。

## 运行方式

```bash
python labels_and_time_splits.py
```

输出会先打印每个 split 的日期范围：

```text
train: rows=..., dates=[...]
valid: rows=..., dates=[...]
test: rows=..., dates=[...]
```

然后打印整理后的特征和标签表。

## 特征和标签的方向

特征使用过去：

```python
df["feature_momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
```

标签使用未来：

```python
df["label_next_return"] = by_symbol["close"].shift(-1) / df["close"] - 1
```

这里的 `shift(3)` 和 `shift(-1)` 方向完全相反。`shift(3)` 表示“取 3 个交易日前的数据”，是当时可知的；`shift(-1)` 表示“取下一个交易日的数据”，只能作为训练标签或事后评估。

## 为什么不能随机切分

如果随机划分，训练集可能包含 2024-01-12 的样本，测试集却包含 2024-01-08 的样本。模型等于用未来市场状态训练，再回头预测过去。这在统计上会高估效果，在投资上没有意义。

正确做法是按时间切分：

```python
train = dataset[dataset["date"] <= "2024-01-08"]
valid = dataset[(dataset["date"] > "2024-01-08") & ...]
test = dataset[dataset["date"] > "2024-01-10"]
```

真实项目里还要进一步区分 research、validation、final holdout，不能反复查看最终测试集。

## 你应该检查什么

- 每个 split 的日期是否连续且不重叠。
- test 的日期是否晚于 train。
- feature 列是否只使用过去数据。
- label 列是否只用于训练目标和评估，不作为输入特征。

## 常见坑

- 用 `train_test_split(shuffle=True)`。
- 先用全样本标准化，再切 train/test。
- 先看 test 表现，再回头改标签或特征。
- 把当天收盘价产生的信号假设可以当天收盘成交。

## 下一步

有了特征和标签之后，不要立刻训练模型。先进入 `06-factor-evaluation`，看单个候选因子有没有基本预测关系。
