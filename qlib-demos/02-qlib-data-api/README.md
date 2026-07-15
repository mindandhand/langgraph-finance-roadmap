# 02：第一次读取 Qlib 数据

这节开始接触 Qlib 原生数据入口：`qlib.init(...)` 和 `D.features(...)`。如果没有真实 Qlib 数据，脚本会自动回退到内置 CSV；如果设置了 `QLIB_PROVIDER_URI`，它会优先尝试从真实 Qlib provider 读取。

## 这个示例想说明什么

Qlib 的 Data API 解决的是一个非常具体的问题：给定股票池、字段、起止日期和频率，返回一个带时间和标的索引的数据表。

在普通 Pandas 项目里，你可能会手动读很多 CSV，再自己过滤日期和股票。Qlib 则把这件事抽象成：

```python
qlib.init(provider_uri=provider_uri, region=REG_CN)
D.features(
    instruments=symbols,
    fields=["$close", "$volume"],
    start_time=start,
    end_time=end,
    freq="day",
)
```

这里最值得注意的是字段名：Qlib 表达式里常用 `$close`、`$volume` 这种写法，表示从数据 provider 中读取对应字段。

## 运行方式

无真实 Qlib 数据时：

```bash
python qlib_data_api.py
```

使用真实 Qlib 数据时：

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python qlib_data_api.py
```

如果 Qlib import、初始化或读取失败，脚本会打印失败原因，并回退到内置 CSV。这是教学示例的容错，不是生产代码建议。生产系统里应该让数据错误显式失败。

## 脚本的三段结构

第一段是 CSV 回退：

```python
def load_csv(symbols, start, end):
    ...
```

它模拟 Qlib Data API 的输出，让后面的例子即使没有真实数据也能继续运行。

第二段是真实 Qlib 读取：

```python
def load_qlib(provider_uri, symbols, start, end):
    import qlib
    from qlib.constant import REG_CN
    from qlib.data import D
    ...
```

`qlib` 在函数内部 import，是为了让没安装 Qlib 的环境也能运行 CSV 路径。

第三段是统一入口：

```python
if provider_uri:
    try:
        data = load_qlib(...)
    except Exception:
        data = load_csv(...)
else:
    data = load_csv(...)
```

这让“真实 Qlib 数据”和“教学小数据”拥有相同的下游 DataFrame 结构：`date`、`symbol`、`close`、`volume`。

## 你应该观察什么

输出第一行会告诉你数据来源：

```text
source: csv fallback; set QLIB_PROVIDER_URI to use real Qlib data
```

然后打印过滤后的行情表。只要输出包含 `date/symbol/close/volume`，后续章节就能继续基于同样结构构造表达式、标签、Dataset 和模型。

## 常见坑

- `pyqlib` 安装成功，但 `provider_uri` 没设置，仍然读不到真实数据。
- `provider_uri` 指向普通 CSV 目录，而不是 Qlib 格式目录。
- instruments 名称要和你的 Qlib 数据市场一致，A 股常见写法可能是 `SH600000`/`SZ000001`，不同数据源可能有差异。
- Qlib 返回的索引/列名不一定正好是你项目想要的命名，所以示例里统一 rename 成 `date`、`symbol`、`close`、`volume`。

## 下一步

有了字段读取之后，下一节进入 `03-qlib-expressions`：理解 `$close`、`Ref`、`Mean`、`Rank` 这类表达式到底在做什么。
