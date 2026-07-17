# 04：Qlib DataHandlerLP 和 DatasetH

这节直接使用 Qlib 原生 `QlibDataLoader`、`DataHandlerLP` 和 `DatasetH`，不再用本地小类模拟。

## 核心流程图

```text
feature / label expression config
  -> QlibDataLoader
  -> DataHandlerLP(raw / infer / learn)
  -> Processor
  -> DatasetH segments(train / test)
  -> dataset.prepare(segment, data_key)
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python data_handler_and_dataset.py
```

## 这个示例想说明什么

三层职责：

```text
QlibDataLoader：定义要加载哪些 feature / label 表达式
DataHandlerLP：组织 raw / infer / learn 数据，并运行 Processor
DatasetH：按 train/test segment 切出模型需要的数据
```

脚本会打印 `DK_R` 和 `DK_L` 两种数据：

```text
DK_R：原始加载结果
DK_L：学习流程使用的数据
```

这两个 data key 和 `train/test` segment 不是一回事。前者表示处理流水线，后者表示时间切片。

## 本节特征

```text
MOM5
MOM20
VOL20
VOLUME_RATIO_5_20
```

标签：

```text
Ref($close, -2) / Ref($close, -1) - 1
```

## 下一步

进入 `05-labels-and-time-splits`，单独观察未来收益标签和时间切分。
