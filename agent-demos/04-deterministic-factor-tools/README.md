# 确定性因子工具：LLM 不负责算数值真值

这篇文档讲的是 `factor_tools.py`。它回答量化 Agent 的核心问题：Agent 能不能“计算因子”？答案是：**Agent 可以选择因子定义和参数，但具体数值必须由确定性工具计算**。

本例继续使用真实沪深 300 ETF 数据：

```text
../../qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv
```

这让示例从“演示公式”升级为“可复查的小型研究步骤”：同一份输入数据、同一段代码、同一组参数，会得到同一份因子 artifact。

## 这个示例想说明什么

脚本做五件事：

```text
读取 SH510300.csv
  ↓
过滤 symbol 和日期区间
  ↓
按 symbol 计算 lookback 日动量因子
  ↓
构造未来 label_horizon 日收益标签
  ↓
把结果写入 artifacts/momentum_5d.csv
```

输出不是一句“这个因子不错”，而是一份可被后续评估工具读取的因子矩阵。

## FactorSpec：Agent 应该产出配置，而不是数值

```python
@dataclass(frozen=True)
class FactorSpec:
    name: str
    symbol: str
    start_date: str
    end_date: str
    lookback: int
    label_horizon: int
```

这就是 Agent 在本节应该产生的东西：一个因子计算规格。

Agent 不应该直接输出：

```text
SH510300 的 5 日动量是 1.2%
```

它应该输出：

```json
{
  "name": "momentum",
  "symbol": "SH510300",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "lookback": 5,
  "label_horizon": 1
}
```

然后由工具读取数据并计算数值。

## 因子和标签的方向完全不同

核心计算是：

```python
data["factor"] = data["close"] / by_symbol["close"].shift(spec.lookback) - 1
data["label"] = by_symbol["close"].shift(-spec.label_horizon) / data["close"] - 1
```

这里有两个方向相反的 `shift`：

- `shift(lookback)`：使用过去价格，构造当下可见的特征。
- `shift(-label_horizon)`：使用未来价格，构造训练和评估用的标签。

这是量化研究最容易犯错的地方。特征一旦用了未来数据，回测就会虚高；标签如果没有和特征对齐，IC 就没有意义。

## 为什么必须写 artifact

`compute_momentum()` 不只是返回 DataFrame，还会写出：

```text
artifacts/momentum_5d.csv
```

这样做有三个目的：

- 后续评估工具可以只读取 `artifact_ref`，不需要重跑上游步骤。
- 报告可以引用具体文件，方便复查。
- 实验记录可以保存“参数 + artifact + 指标”的闭环。

这也是 Qlib、MLflow、实验数据库和研究平台常用的模式：不要只保存最终结论，要保存中间证据。

## 和 Qlib 表达式的关系

本例 Pandas 代码：

```python
close / Ref(close, 5) - 1
```

对应 Qlib 表达式：

```text
$close / Ref($close, 5) - 1
```

二者本质一样，差别在执行引擎。Pandas 适合教学和小样本调试，Qlib 适合大规模多标的、多字段、多频率的数据访问与表达式计算。

Agent 不应该依赖某一个引擎的内部细节。它应该依赖稳定的工具契约：

```text
FactorSpec -> factor artifact -> metrics / backtest
```

## 实际运行

```bash
python factor_tools.py
```

你会看到类似输出：

```text
artifact: ArtifactRef(path='.../artifacts/momentum_5d.csv', rows=52, columns=[...])
```

生成的 CSV 中包含：

- `date`
- `symbol`
- `close`
- `factor`
- `label`

这份文件会被 `.gitignore` 忽略，因为它是运行产物，不是源码。

## 常见坑

- 把未来收益误放进 feature。
- 没有按 symbol 分组，导致不同标的串线。
- 只返回最终指标，不保存因子矩阵。
- Agent 根据结果反复改 `lookback`，形成参数挖掘。
- 工具静默丢弃大量空值，却不返回行数和覆盖区间。

## 下一步

因子工具会产生中间结果。下一节 `05-memory-and-research-journal` 讲如何记录研究过程：不是把聊天历史当记忆，而是保存 research journal、artifact refs 和失败记录。
