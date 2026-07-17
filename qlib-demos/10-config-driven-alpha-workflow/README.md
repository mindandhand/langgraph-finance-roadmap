# 10：配置驱动的 Qlib 因子评估流程

这一节用一个 Python `CONFIG` dict 串起因子评估。它不是完整 `qrun`，但体现了 Qlib 项目常见思想：研究对象由配置描述，执行逻辑保持稳定。

## 图结构

```mermaid
graph TD
    A["CONFIG"] --> B["factor_expression"]
    A --> C["label_expression"]
    B --> D["evaluate_factor"]
    C --> D
    D --> E["D.features"]
    E --> F["metrics"]
    A --> G["artifacts/config.json"]
    F --> H["artifacts/metrics.json"]
```

## Python 文件逐段拆解

### `CONFIG`

配置包含：

```python
{
    "experiment_id": "qlib_factor_eval_001",
    "factor_expression": "...",
    "label_expression": "...",
    "topk": 50,
    "cost_rate": 0.001,
}
```

当前脚本主要使用 factor 和 label 做预测层评估。`topk` 和 `cost_rate` 是后续策略层评估参数，保留在配置中是为了让实验边界完整。

### `init_qlib()`

配置只是描述实验，真正执行前仍要初始化 Qlib provider。没有 provider，表达式无法被确定性计算。

### `evaluate_factor(...)`

这是第 6 节的核心评估函数。配置驱动并不改变评估逻辑，只改变输入参数。

### `artifacts`

脚本写出：

```text
config.json
metrics.json
```

这对应真实研究中的两个关键产物：实验输入和实验输出。自动因子系统必须同时保存两者。

## 一次运行的完整执行轨迹

1. 读取 `CONFIG`。
2. 初始化 Qlib。
3. 用配置里的 factor/label 调用 `evaluate_factor`。
4. 创建 `artifacts/<experiment_id>/`。
5. 保存 config 和 metrics。

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python config_driven_alpha_workflow.py
```

## 核心原理

配置驱动的价值是复现和批量化：

```mermaid
graph LR
    A["多个候选表达式"] --> B["同一个评估函数"]
    B --> C["统一 metrics schema"]
    C --> D["可比较结果"]
```

Agent 可以生成候选表达式，但评估函数、标签定义、时间区间和输出格式必须稳定。

## 下一步

进入 `11-alpha158-alpha360-feature-sets`，看 Qlib 官方预定义特征集合如何封装成 Handler。
