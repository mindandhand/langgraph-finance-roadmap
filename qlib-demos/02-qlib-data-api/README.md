# 02：第一次读取 Qlib 数据

这节使用 Qlib 原生数据入口：`qlib.init(...)` 和 `D.features(...)`。脚本不再提供 CSV fallback。

## 核心流程图

```text
QLIB_PROVIDER_URI + QLIB_MARKET / QLIB_INSTRUMENTS
  -> qlib.init
  -> D.features(fields=["$open", "$high", "$low", "$close", "$volume"])
  -> MultiIndex DataFrame(datetime, instrument)
  -> 检查字段列、索引层级和数据范围
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python qlib_data_api.py
```

默认读取：

```text
$open
$high
$low
$close
$volume
```

默认股票池来自：

```bash
QLIB_MARKET=csi300
```

也可以指定少量标的：

```bash
QLIB_INSTRUMENTS=SH600000,SZ000001 python qlib_data_api.py
```

## 这个示例想说明什么

Qlib 的 Data API 负责根据：

```text
provider_uri
instruments / market
fields
start_time / end_time
freq
```

返回带 `datetime` 和 `instrument` 索引的数据表。字段名中的 `$close`、`$volume` 不是普通 CSV 列名，而是 Qlib expression engine 读取 provider 字段的写法。

## 下一步

进入 `03-qlib-expressions`，把字段扩展成 `Ref`、`Mean`、`Std`、`Rank` 等 Qlib 表达式。
