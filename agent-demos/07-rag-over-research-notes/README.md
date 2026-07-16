# RAG 研究笔记：让 Agent 基于证据回答

这篇文档讲的是 `rag_research_notes.py`。它用最小关键词检索模拟 RAG：给定一个问题，从已有研究笔记中找出相关证据。

RAG 在量化研究里的价值不是“让回答更长”，而是让 Agent 的解释和建议能追溯到已有材料。

## 这个示例想说明什么

内置笔记：

```python
NOTES = [
    {"id": "note-001", "text": "Short-term momentum can be unstable after costs because turnover is high."},
    {"id": "note-002", "text": "Rank IC is preferred when factor scale is unstable but ordering may still help."},
    {"id": "note-003", "text": "Do not use final holdout repeatedly when tuning factor windows."},
]
```

查询：

```text
Should I trust a short-term momentum factor with high turnover?
```

返回：

```text
note-001: Short-term momentum can be unstable after costs because turnover is high.
note-002: Rank IC is preferred when factor scale is unstable but ordering may still help.
```

## RAG 和 Memory 的区别

示例 5 的 journal 是“写入记忆”。本节是“检索记忆”。

```text
Journal: 记录发生过什么
RAG:     在需要回答时检索相关证据
```

两者结合起来，Agent 才能从过去实验和研究规范中找依据，而不是每次从 prompt 重新开始。

## 为什么这里不用向量数据库

因为本节要讲的是机制，不是工具选型。真实项目可以把 `retrieve()` 替换成：

- 向量数据库
- BM25
- SQLite FTS
- 文档检索服务
- 实验记录查询

关键不变：Agent 先取证据，再写结论。

## 常见坑

- 检索结果没有 ID，报告无法引用。
- RAG 返回了笔记，但 Agent 忽略证据继续发挥。
- 只检索支持性证据，不检索失败记录。
- 把 RAG 当事实来源，忘记原始数据和指标仍需工具验证。
- 检索范围混入未来实验记录，造成泄漏。

## 设计原则一：RAG 提供上下文，不提供数值真值

RAG 很容易被误用。检索到一条笔记：

```text
Short-term momentum can be unstable after costs because turnover is high.
```

这不等于当前因子一定无效。它只是提醒 Agent：评估短期动量时应该检查换手和成本。

数值真值仍然来自工具：

```text
turnover -> backtest tool
cost     -> exchange/cost model
IC       -> evaluation tool
```

所以 RAG 在量化 Agent 里的角色是“证据和规则检索”，不是“替代计算”。

## 设计原则二：检索结果必须可引用

每条 note 都有 `id`：

```python
{"id": "note-001", "text": "..."}
```

报告里应该引用：

```text
According to note-001, short-term momentum may fail after costs.
```

没有 ID 的检索结果很难审计。你不知道 Agent 的说法来自哪条材料，也无法检查材料是否可靠。

真实系统里，ID 可以是：

- 文档路径
- 实验 ID
- 数据合同版本
- 研究报告段落 ID
- issue / PR / notebook hash

## 设计原则三：检索范围要防止时间泄漏

量化研究里，RAG 也可能泄漏未来信息。

例如你在研究 2020 年以前的策略，却允许 Agent 检索 2024 年写的“这个因子后来失效了”的笔记，这就可能污染研究过程。

更严谨的检索应带时间过滤：

```text
只检索 research_date 之前已经存在的笔记
```

本示例没有实现时间过滤，但真实系统应该考虑。

## 设计原则四：要同时检索反证

如果 query 是：

```text
Should I trust short-term momentum?
```

系统不应该只找支持 momentum 的笔记，也应该找：

- 成本风险
- 换手风险
- 样本外失效记录
- 参数挖掘警告
- 相关失败实验

好的研究 Agent 不只是找理由支持候选因子，也要主动检索反证。

## 从关键词检索到真实 RAG

本例用最简单的关键词匹配：

```python
score = sum(1 for word in words if word in note["text"].lower())
```

真实系统可以替换成 BM25、向量数据库、hybrid search、metadata filter 或 reranker。但无论实现多复杂，输出都应该保持同样结构：

```json
{
  "id": "note-001",
  "text": "...",
  "source": "...",
  "created_at": "...",
  "relevance": 0.82
}
```

## 下一步

RAG 能提供证据，但不能替代审批。下一节 `08-human-review-before-backtest` 会在回测前加入人工确认。
