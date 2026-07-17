# 03：Qlib 表达式引擎

这节直接把表达式字符串交给 Qlib `D.features` 计算，观察 `$close`、`Ref`、`Mean`、`Std`、`Rank` 如何从 provider 字段变成因子矩阵。

## 核心流程图

```text
Qlib provider 基础字段
  -> Qlib expression strings
  -> D.features 解析和计算表达式
  -> factor(datetime, instrument)
  -> 时间序列特征 + 横截面特征
```

表达式可以理解成一棵计算树：

```text
"$close / Ref($close, 20) - 1"
  -> Feature($close)
  -> Ref(Feature($close), 20)
  -> Div
  -> Sub(1)
  -> MOM20
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python qlib_expressions.py
```

## 本节表达式

脚本计算：

```text
$close
Ref($close, 1)
$close / Ref($close, 20) - 1
Mean($close, 20) / $close
Std($close / Ref($close, 1) - 1, 20)
Mean($volume, 5) / Mean($volume, 20)
Rank($close / Ref($close, 20) - 1)
```

## 核心原理

- `Ref($close, 1)` 引用过去一个交易周期的数据，可以作为特征。
- `Ref($close, -5)` 引用未来数据，只能用于标签或事后评估。
- `Mean / Std` 是每只股票自己的时间序列窗口计算。
- `Rank` 是横截面计算，用于同一天不同股票之间的比较。

## 常见坑

- 把未来收益表达式写进 feature。
- 忘记时间序列计算和横截面计算的边界。
- 只看某一天的 Rank，不做长期 IC / RankIC 验证。

## 下一步

进入 `04-data-handler-and-dataset`，把表达式组织成 Qlib `feature` / `label` 配置，并交给 `DataHandlerLP` 和 `DatasetH`。
