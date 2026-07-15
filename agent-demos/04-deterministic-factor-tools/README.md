# 04：因子计算必须是确定性工具

Agent 可以决定“要计算 3 日动量”，但不能靠语言模型心算结果。因子值必须由确定性 Python/Pandas 工具计算。

## 运行

```bash
python factor_tools.py
```

本例读取内置价格表，计算 3 日动量和未来 1 日收益。

## 新增概念

Agent 的输出应该是工具配置，而不是数值结论：

```text
factor = momentum
lookback = 3
```

工具负责把配置变成 DataFrame 和 artifact。
