# 07：RAG 检索研究笔记

Agent 不应该凭空解释一个因子。它应该先检索已有研究笔记、数据合同或失败记录，再基于证据回答。

## 运行

```bash
python rag_research_notes.py
```

本例用最小关键词检索模拟 RAG，从内置研究笔记中找出和 momentum、turnover 相关的证据。

## 新增概念

RAG 的价值不是“让回答更长”，而是让 Agent 的结论可追溯到已有证据。
