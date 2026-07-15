# 03：工具调用读取市场数据

Agent 不应该自己“想象”行情。它应该选择一个受控工具，由工具读取或返回市场数据。

## 运行

```bash
python market_data_tools.py
```

本例仍然不用外部网络。Agent 根据问题选择 `get_prices` 工具，工具返回内置 ETF 价格序列。

## 新增概念

工具调用至少包含三层：

- tool name：工具叫什么。
- tool args：参数是什么。
- tool result：确定性返回什么。

后续接 AkShare、Qlib 或数据库时，只替换工具实现，不改变 Agent 的职责边界。
