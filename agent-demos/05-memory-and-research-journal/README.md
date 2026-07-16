# 研究记忆：不是聊天历史，而是 Journal

这篇文档讲的是 `research_journal.py`。它把 Agent memory 从“多轮聊天记录”改成“结构化研究日志”。

量化研究需要的长期记忆通常不是“用户刚才说了什么”，而是：

- 哪些数据被加载过。
- 哪些因子被计算过。
- 哪些实验失败过。
- 哪些 artifact 可以复查。
- 哪些指标支持或反驳某个结论。

## 这个示例想说明什么

脚本写出一个 JSONL 文件：

```text
artifacts/research_journal.jsonl
```

每一行是一个事件：

```json
{"step": "load_data", "artifact": "prices.csv", "status": "ok"}
{"step": "compute_factor", "factor": "momentum_3d", "artifact": "factor.csv", "status": "ok"}
{"step": "evaluate", "metric": "ic", "value": 0.04, "status": "weak"}
```

这种结构比自然语言聊天历史更适合审计。

## 为什么用 JSONL

JSONL 的好处是：

- 每个事件独立。
- 可以追加写入。
- 方便后续检索。
- 失败事件也能记录。
- 不要求一次加载完整日志。

真实系统可以换成数据库、Qlib Recorder、MLflow 或实验平台，但思想一样：记录结构化事件。

## Memory 应该保存什么

建议保存：

- tool call：调用了什么工具，参数是什么。
- artifact refs：产物路径或 ID。
- metrics：指标值和计算口径。
- decision：接受、拒绝、继续观察。
- failure：失败原因和异常信息。

不建议保存：

- 大型 DataFrame 全量内容。
- 未压缩的完整 prompt。
- 没有时间和版本的自然语言结论。

## 常见坑

- 只保存成功实验，不保存失败实验。
- 只保存最终报告，不保存中间 artifact。
- 聊天历史太长，后续无法检索。
- 没有 experiment_id，多个研究混在一起。
- Agent 根据记忆写结论，但没有引用具体证据。

## 设计原则一：Memory 要能被审计，而不是只被模型阅读

聊天型 Agent 常把 memory 设计成一段可追加的自然语言摘要：

```text
用户喜欢动量因子；上次我们研究过 SH510300；结果看起来不错。
```

这对闲聊可能够用，但对量化研究不够。研究记忆必须能被审计：

- 谁在什么时候做了什么？
- 输入数据是什么？
- 工具参数是什么？
- 输出 artifact 在哪里？
- 指标是多少？
- 结论是接受、拒绝还是继续观察？

所以本示例用 JSONL，而不是自然语言段落。每一行都是一个可独立审查的事件。

## 设计原则二：Journal 是 append-only 的研究轨迹

研究日志最好是追加式的，而不是不断覆盖。

覆盖式记录的问题：

```text
只知道当前状态，不知道如何走到当前状态。
```

追加式记录的价值：

```text
知道每一步发生了什么，也知道失败和修正过程。
```

这对自动因子挖掘尤其重要。一个搜索系统可能测试了 100 个表达式，其中 99 个失败。如果只保存成功的 1 个，最后的结果会严重选择性偏差。失败实验本身就是研究证据。

## 设计原则三：Memory 不应该替代重新计算

Journal 里记录了：

```json
{"metric": "ic", "value": 0.04}
```

这不意味着以后可以永远相信这个 IC。它只说明“某次实验算出了这个值”。如果数据版本、代码版本、因子定义、样本区间发生变化，就必须重新运行确定性工具。

正确关系是：

```text
Journal 记录历史结果
Tool    生成当前真值
Agent   对比和解释
```

Agent 可以引用 journal，但不能把 journal 当作永远正确的事实库。

## 设计原则四：Memory 要支持检索

下一节会讲 RAG。为了能检索，日志最好包含稳定字段：

```json
{
  "experiment_id": "exp-001",
  "factor": "momentum_3d",
  "step": "evaluate",
  "metric": "ic",
  "value": 0.04,
  "status": "weak",
  "artifact": "factor.csv"
}
```

这样后续可以按 factor、metric、status、experiment_id 检索，而不是只做全文搜索。

## Journal 和 LangGraph Checkpoint 的区别

两者容易混：

```text
Checkpoint: 让图可以恢复执行
Journal:    让研究可以被审计
```

Checkpoint 关注运行时恢复，例如中断后从哪个节点继续。Journal 关注研究证据，例如做过哪些实验、结果如何、为什么决策。

真实系统通常两个都需要。

## 下一步

有了记忆之后，Agent 仍然不能无限尝试。下一节 `06-planning-a-factor-study` 会给研究计划加预算和终止条件。
