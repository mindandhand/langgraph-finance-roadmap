# 规划因子研究：限制 Agent 的试错空间

这篇文档讲的是 `factor_study_plan.py`。它解决 Agent 在量化研究里最危险的问题之一：**无限试错**。

一个不受约束的 Agent 很容易形成这样的循环：

```text
试一个因子 -> IC 不好 -> 换窗口 -> 回测不好 -> 换区间 -> 再换标签 -> 继续看结果
```

这看起来像勤奋研究，实际可能是参数挖掘和回测过拟合。量化研究 Agent 必须先有计划和预算，之后执行系统按计划推进。

## 这个示例想说明什么

脚本包含三个层次：

```text
ResearchBudget 定义预算
  ↓
make_plan() 生成研究计划
  ↓
run_plan() 校验预算并逐步执行
```

它不是只打印一个计划，而是把计划变成可检查、可执行、可追踪的流程。

## ResearchBudget：把研究纪律变成代码

```python
@dataclass(frozen=True)
class ResearchBudget:
    max_factors: int
    max_windows: int
    max_backtests: int
```

本例限制三个东西：

- 最多研究多少个候选因子。
- 每个因子最多试多少个参数窗口。
- 最多运行多少次回测。

这些限制不是为了让 Agent 变笨，而是为了避免它用历史数据反复调参。对量化研究来说，回测次数本身就是一种预算，因为每看一次回测结果，研究者就多一次根据历史表现调整设计的机会。

## 计划不是建议，是约束

`make_plan()` 生成的计划类似：

```python
[
    {"step": "define_factor", "factor": "momentum", "windows": [3, 5]},
    {"step": "compute_ic"},
    {"step": "request_review"},
    {"step": "run_simple_backtest"},
    {"step": "write_report"},
]
```

很多 Agent 系统会让模型先“列一个计划”，但后续执行并不强制遵守。这种计划只是装饰。

本例的关键是 `run_plan()` 会先调用 `validate_plan()`。如果因子数、窗口数或回测次数超预算，就直接拒绝执行。

## PlanState：执行过程也要可追踪

```python
@dataclass
class PlanState:
    trace: list[str] = field(default_factory=list)
    backtests_used: int = 0
    status: str = "created"
```

`run_plan()` 每执行一步都会更新 `trace`。这使得输出不是一句“完成了”，而是能看到实际经过了哪些阶段：

```text
define_factor -> compute_ic -> request_review -> run_simple_backtest -> write_report
```

真实研究系统应该继续扩展这个状态：

- 记录每个工具调用参数。
- 记录 artifact 路径。
- 记录审批人和审批时间。
- 记录失败原因。
- 记录是否访问过 holdout。

## 为什么这里仍然不用 LangGraph

本节已经有“状态”和“步骤”，但流程仍然是线性的，没有暂停恢复、条件分支或多角色协作。用普通 Python 写执行器更容易看清研究预算的本质。

等到第 8 节开始出现人工中断，第 9 节开始出现完整状态图，第 10 节出现多角色审查，第 12 节出现端到端条件路由，就会使用 LangGraph。

## 实际运行

```bash
python factor_study_plan.py
```

你会看到类似输出：

```text
status: completed
trace: define_factor -> compute_ic -> request_review -> run_simple_backtest -> write_report
backtests_used: 1
```

如果把 `windows` 改成 `[3, 5, 10]`，或者增加多个 `run_simple_backtest` 步骤，预算检查应该拒绝执行。

## Agent 在这里做什么

Agent 可以帮助生成计划，比如：

- 根据研究目标建议候选因子。
- 建议少量合理窗口。
- 指定先做 IC 还是先做覆盖率检查。
- 标记哪些步骤必须人工审批。

但计划生成后，执行系统必须检查预算。不能因为 Agent 说“再试一次可能更好”，就自动扩大试错空间。

## 常见坑

- 计划只写在 prompt 里，不被程序检查。
- 没有最大回测次数。
- 失败后允许 Agent 无限修改参数。
- 最终报告只展示最好的一次。
- 没有记录被拒绝或失败的实验。

## 下一步

计划解决“能做什么”。下一节 `07-rag-over-research-notes` 解决“依据什么做”：Agent 在解释因子和风险时，应该检索已有研究笔记，而不是凭空编造。
