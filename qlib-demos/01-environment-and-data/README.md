# 01：先把 Qlib 环境和数据入口跑通

这节只做一件事：确认当前 Python 导入的是 Microsoft `pyqlib`，并且 `QLIB_PROVIDER_URI` 指向可读取的 Qlib 数据目录。

如果没有 Qlib provider，本示例会直接失败。学习 Qlib 数据层时不应该静默回退到本地 CSV，因为那会绕过 Provider、calendar、instruments 和 expression engine。

## 核心流程图

```text
Python 环境
  -> import Microsoft pyqlib
  -> 读取 QLIB_PROVIDER_URI / QLIB_REGION
  -> qlib.init(provider_uri, region)
  -> D.calendar(start_time, end_time)
  -> 确认 provider、交易日历和市场配置可用
```

## 运行方式

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python environment_and_data.py
```

可选：

```bash
QLIB_REGION=cn
QLIB_MARKET=csi300
QLIB_START_TIME=2020-01-01
QLIB_END_TIME=2020-12-31
```

## 你应该看到什么

脚本会打印：

```text
provider_uri
market
instruments
date range
qlib module
calendar rows
calendar range
```

如果提示导入的 `qlib` 不是 Microsoft `pyqlib`，说明环境中安装了同名冲突包，需要移除错误的 `qlib` 包后再运行。

## 下一步

进入 `02-qlib-data-api`，用 `D.features` 从 provider 中读取真实字段。
