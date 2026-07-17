# 08：使用 Qlib Recorder 记录实验

这节使用 Qlib 原生 `qlib.workflow.R`，把一次因子评估记录为 experiment / recorder。

## 核心流程图

```text
factor expression + label expression
  -> evaluate_factor
  -> R.start(experiment_name, recorder_name)
  -> R.log_params
  -> R.log_metrics
  -> R.save_objects
  -> 可复查 / 可比较的实验记录
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python recorder_and_experiment.py
```

可选传入候选因子：

```bash
QLIB_FACTOR_EXPR='$close / Ref($close, 20) - 1' \
QLIB_LABEL_EXPR='Ref($close, -5) / $close - 1' \
python recorder_and_experiment.py
```

## 记录内容

脚本会在 `R.start(...)` 内：

```text
R.log_params：记录 factor expression 和 label expression
R.log_metrics：记录 coverage、IC、RankIC、ICIR
R.save_objects：保存 metrics 对象
```

自动因子挖掘系统不应该只看终端输出。每个候选表达式都需要可追踪的参数、指标和 artifact。

## 下一步

进入 `09-strategy-and-backtest`，把 Qlib 产生的 score 转成简单 top-k 组合检验。
