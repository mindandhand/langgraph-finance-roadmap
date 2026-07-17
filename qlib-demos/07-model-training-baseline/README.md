# 07：Qlib 模型训练基线

这节使用 Qlib `DataHandlerLP`、`DatasetH` 和 `LGBModel` 训练一个 LightGBM 基线模型，并在 test segment 上产生预测分数。

## 核心流程图

```text
feature / label expression config
  -> DataHandlerLP + Processor
  -> DatasetH(train / test)
  -> LGBModel.fit(dataset)
  -> LGBModel.predict(dataset, segment="test")
  -> score(datetime, instrument)
  -> join label
  -> daily IC
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python model_training_baseline.py
```

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

## 核心原理

模型输出的是 `score`，不是收益：

```text
feature matrix
  -> model
  -> score
  -> 与 label 计算 IC
  -> 后续再进入 strategy / backtest
```

`score` 只表达模型对横截面相对表现的判断。它还没有持仓、成交、成本和账户状态。

## 常见坑

- `learn_processors` 和 `infer_processors` 不一致，导致训练和预测特征处理不同。
- 用全样本训练后报告 test 表现。
- 把 label 混进 feature。
- 只看训练损失，不看样本外 IC。

## 下一步

进入 `08-recorder-and-experiment`，用 Qlib Recorder 记录参数、指标和 artifact。
