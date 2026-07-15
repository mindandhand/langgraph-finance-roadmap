# 04：Handler 和 Dataset 的职责边界

Qlib 里一个容易混淆的点是：数据读取、特征构造、标签构造、样本切分不是同一层职责。这个示例用两个很小的 Python 类模拟 Qlib 的 Handler/Dataset 思路，让你先看懂边界，再去看 `DataHandlerLP`、`DatasetH` 之类的原生组件。

## 这个示例想说明什么

可以先用一句话区分：

- Handler：负责把原始行情处理成“可训练表”，包含特征列和标签列。
- Dataset：负责按 segment 返回不同时间段的数据，例如 train、valid、test。

也就是说，Handler 更关心“列怎么来”，Dataset 更关心“哪些行属于哪个阶段”。

## 运行方式

```bash
python data_handler_and_dataset.py
```

输出会分三段打印：

```text
train: rows=...
valid: rows=...
test: rows=...
```

每段都包含 `feature_momentum_3d` 和 `label_return_1d`。这正是后续模型训练需要的最小结构。

## Handler 做了什么

脚本里的 `MiniDataHandler` 接收原始行情：

```python
handler = MiniDataHandler(raw)
```

然后在 `fetch()` 里生成两类列：

```python
df["feature_momentum_3d"] = ...
df["feature_volume_change_3d"] = ...
df["label_return_1d"] = ...
```

这里的标签是未来 1 日收益：

```python
df["label_return_1d"] = by_symbol["close"].shift(-1) / df["close"] - 1
```

`shift(-1)` 只能出现在标签里，不能出现在特征里。这个边界要非常清楚。

## Dataset 做了什么

`MiniDataset` 保存完整可训练表和时间段配置：

```python
segments = {
    "train": ("2024-01-01", "2024-01-08"),
    "valid": ("2024-01-09", "2024-01-09"),
    "test": ("2024-01-10", "2024-01-31"),
}
```

调用：

```python
dataset.prepare("train")
```

只返回 train 时间段的行。真实 Qlib 的 Dataset 也是类似思想，只是支持更复杂的数据 handler、processor、cache 和 segment 配置。

## 为什么不直接在一个函数里全做完

小脚本当然可以“一把梭”：读数据、算特征、切分、训练都写在一个函数里。但研究项目一旦变大，这会带来几个问题：

- 换标签时容易不小心改到切分逻辑。
- 换 train/test 日期时容易不小心重算特征。
- 多个模型共用同一批特征时，重复计算且难以追踪。
- 实验记录里说不清楚数据版本和 segment 版本。

Handler/Dataset 的分层就是为了避免这些混乱。

## 常见坑

- 在 Handler 里根据 test 表现筛特征，这是数据窥探。
- 在 Dataset 里随机打乱时间序列，这是金融任务常见错误。
- 标签列和特征列命名不清，训练时把 label 当 feature。
- 把完整 DataFrame 到处传，后续很难追踪版本。

## 下一步

进入 `05-labels-and-time-splits`，专门把标签和时间切分再讲细一点：什么时候是信号日，什么时候是收益实现日，为什么不能随机划分。
