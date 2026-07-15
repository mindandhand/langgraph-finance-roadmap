# 03：Qlib 表达式不是魔法

这节不直接调用 Qlib 表达式引擎，而是用 Pandas 逐行模拟几个最常见的 Qlib 表达式。目的不是绕开 Qlib，而是先把表达式背后的量化含义讲清楚：它们本质上都是对“某只股票自己的时间序列”或“某一天所有股票的横截面”做计算。

## 这个示例想说明什么

Qlib 里常见的表达式长这样：

```text
$close
Ref($close, 1)
$close / Ref($close, 3) - 1
Mean($close, 3)
Rank($close / Ref($close, 3) - 1)
```

如果你直接从这些表达式入手，容易把注意力放在语法上。其实更重要的是区分两类计算：

- 时间序列计算：对每只股票分别计算，例如 `Ref`、`Mean`、过去 N 日收益。
- 横截面计算：对同一天的所有股票计算，例如每日排名、分位数、中性化。

这个脚本把两者都写成 Pandas 代码。

## 运行方式

```bash
python qlib_expressions.py
```

输出表里会看到：

- `ref_close_1`：上一日收盘价
- `momentum_3d`：当前收盘价相对 3 日前的涨跌幅
- `mean_close_3d`：3 日均价
- `momentum_rank`：同一天按 3 日动量做横截面排名

## 逐个表达式拆解

`$close` 对应原始字段：

```python
df["close"]
```

`Ref($close, 1)` 对应每只股票内部的 shift：

```python
df["ref_close_1"] = by_symbol["close"].shift(1)
```

3 日动量：

```python
df["momentum_3d"] = df["close"] / by_symbol["close"].shift(3) - 1
```

3 日均价：

```python
df["mean_close_3d"] = (
    by_symbol["close"].rolling(3).mean().reset_index(level=0, drop=True)
)
```

横截面排名：

```python
df["momentum_rank"] = (
    df.groupby("date")["momentum_3d"].rank(ascending=False, method="first")
)
```

注意最后一个是按 `date` 分组，不是按 `symbol` 分组。这是量化研究里非常重要的边界：因子通常先按股票时间序列构造，再在每日横截面上比较。

## 为什么这节还不用 Qlib 原生表达式

因为已有一点 Python/金融基础的读者，最需要先确认“表达式在金融上代表什么”。Qlib 原生表达式可以后续放进 Handler 或配置文件里，但如果你不知道 `Ref($close, 3)` 是否会引入未来信息，换成 Qlib 语法也不会自动安全。

## 常见坑

- 把 `shift(-1)` 写进特征，直接泄漏未来。
- 把全市场 rolling 写成一个大序列 rolling，导致不同股票之间串在一起。
- 横截面排名忘记按日期分组。
- 看到某一天排名第一，不等于这个因子长期有效，下一节之后还要做标签和评估。

## 下一步

表达式讲的是“特征怎么算”。接下来进入 `04-data-handler-and-dataset`：把特征、标签和时间切分组织成类似 Qlib Handler/Dataset 的结构。
