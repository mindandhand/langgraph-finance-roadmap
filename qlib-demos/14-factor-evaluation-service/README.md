# 14：自动因子评估服务

这一节把前面的 Qlib 数据读取、表达式计算、标签构造、IC/RankIC 和分组收益收口成一个可调用入口。

它不使用本地样本数据。输入必须是 Qlib 表达式，数据必须来自 `QLIB_PROVIDER_URI` 指向的 Qlib provider。

## 核心流程图

```text
CLI 参数 / Agent 候选表达式
  -> expression + label
  -> init_qlib
  -> evaluate_factor
  -> D.features
  -> coverage / IC / RankIC / ICIR / quantile returns
  -> JSON stdout 或 output file
```

## 运行

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data \
python factor_evaluation_service.py \
  --expression '$close / Ref($close, 20) - 1' \
  --label 'Ref($close, -5) / $close - 1'
```

可选输出到文件：

```bash
python factor_evaluation_service.py \
  --expression '$close / Ref($close, 20) - 1' \
  --output artifacts/mom20.json
```

## 输出

```json
{
  "expression": "$close / Ref($close, 20) - 1",
  "label": "Ref($close, -5) / $close - 1",
  "coverage": 0.98,
  "ic_mean": 0.02,
  "rank_ic_mean": 0.03,
  "icir": 0.4,
  "rank_icir": 0.5,
  "quantile_return_mean": {}
}
```

这个脚本就是后续 LangGraph / Agent 自动因子挖掘系统应调用的确定性评估内核。
