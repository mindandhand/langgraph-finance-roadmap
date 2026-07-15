# 01：先把环境和数据入口跑通

这节不急着调用 Qlib。真正开始写研究代码前，先确认三件事：当前 Python 环境里有没有 `pyqlib`、有没有设置 Qlib 数据目录、即使两者都没有，示例还能不能用内置小数据跑通。

Qlib 学习最容易卡在“安装好了库，但没有数据”或“有数据，但 `provider_uri` 指错了”。这个示例把这些前置状态明确打印出来，后面每个例子都沿用同一个策略：**能用真实 Qlib 数据就用真实数据；不能用，也必须能靠内置数据讲清楚研究流程**。

## 这个示例想说明什么

Qlib 项目至少有两层依赖：

- Python 包：`pyqlib`，提供 `qlib.init`、`D.features`、Dataset、Recorder、Backtest 等 API。
- Qlib 格式数据目录：通常通过 `provider_uri` 指定，里面包含 calendar、instruments、features 等文件。

这两者不是一回事。只安装 `pyqlib` 不等于已经有可读行情数据；有一堆 CSV 也不等于已经是 Qlib 格式数据。正式 Qlib 数据访问要到示例 2 才开始，这一节只负责把“环境状态”说清楚。

## 运行方式

无 Qlib 数据也能跑：

```bash
python environment_and_data.py
```

如果已经准备好 Qlib 数据目录：

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python environment_and_data.py
```

输出类似：

```text
pyqlib installed: False
QLIB_PROVIDER_URI: <not set>
fallback sample rows: 12
symbols: ['SH600000', 'SZ000001']
```

这表示当前环境还不能读取真实 Qlib 数据，但内置样例数据可用，可以继续学习后续流程。

## 代码拆解

`importlib.util.find_spec("qlib")` 用来检查当前环境是否能 import Qlib：

```python
has_qlib = importlib.util.find_spec("qlib") is not None
```

`os.getenv("QLIB_PROVIDER_URI")` 读取数据目录配置：

```python
provider_uri = os.getenv("QLIB_PROVIDER_URI")
```

内置 CSV 用 `StringIO` 直接放在脚本里，目的是让每个目录独立运行，不依赖上级目录的数据文件：

```python
sample = pd.read_csv(StringIO(SAMPLE), parse_dates=["date"])
```

## 为什么不一开始就下载 Qlib 数据

因为这条学习线的目标是“循序渐进理解 Qlib 的研究流程”，不是先处理安装和数据下载的所有细节。真实数据当然重要，但一上来就要求下载、转换、配置完整数据，会把注意力从 Qlib 的核心抽象上移开。

后续示例的设计原则是：

- 概念用内置小数据讲清楚。
- Qlib 原生 API 在专门章节引入。
- 真实数据接入作为可选路径，不阻塞本地运行。

## 下一步

跑通本节后，进入 `02-qlib-data-api`。那里会第一次使用 Qlib 官方 Data API 的典型模式：

```python
qlib.init(provider_uri=..., region=REG_CN)
D.features(...)
```
