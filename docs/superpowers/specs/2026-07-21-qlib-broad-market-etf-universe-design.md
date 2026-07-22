# Qlib 宽基 ETF 多品种数据设计

## 背景

当前 `qlib-demos/qlib-data` 只包含沪深 300 ETF（`sh510300`）。单一标的可以演示时间序列表达式，却无法形成有意义的横截面，因此 IC、RankIC、分组收益和 top-k 策略示例缺少足够的数据基础。

本次扩充的目标是提供一个小而有代表性的宽基 ETF 股票池，同时保持仓库体积、下载耗时和教学复杂度可控。

## 标的池

默认包含五个宽基 ETF：

| Qlib instrument | ETF 代码 | 代表指数 |
|---|---:|---|
| `sh510050` | 510050 | 上证 50 |
| `sh510300` | 510300 | 沪深 300 |
| `sh510500` | 510500 | 中证 500 |
| `sz159915` | 159915 | 创业板 |
| `sh588000` | 588000 | 科创 50 |

这些标的覆盖大盘、核心宽基、中小盘、创业板和科创板。它们不是生产级资产池，但足以让教学 demo 展示多品种读取、横截面排序和组合选择。

## 数据范围与语义

- 数据频率为日频。
- 优先使用 AkShare EastMoney ETF 历史行情接口获取请求复权口径的 OHLCV；成交额只在数据源真实返回时保留。
- 每个 ETF 保留自身真实上市日期和数据结束日期，不强制裁剪到共同区间。
- 默认下载起点为 `2005-02-23`，覆盖标的池中最早上市的上证 50 ETF（`sh510050`）完整历史。
- Qlib calendar 使用所有 ETF 交易日的并集。
- 每个 feature 文件只覆盖该 ETF 的有效日期范围；有效范围内的缺失交易日写为 `NaN`。
- `instruments/all.txt` 为每个 ETF 单独记录真实起止日期。
- `factor` 固定为 `1.0`；其含义是价格值已按所选数据源的返回口径直接写入，而不是另行提供可用于复权的因子序列。

## 2026-07-22 实施决定：Sina 回退与可选成交额

在较早的生成尝试中，EastMoney 接口在当时网络环境持续断开连接，而 AkShare Sina ETF 日线接口可以稳定返回五只标的的 OHLCV。经用户批准，下载器保留 EastMoney 为主数据源，并在其外部请求或响应失败时，使用已校验 `InstrumentSpec` 中的交易所限定 `qlib_symbol` 调用 Sina，避免猜测 `sh`/`sz` 前缀。

Sina ETF 日线不提供 `amount`，也没有 `qfq`/`hfq` 调整选择器。因此核心必需字段调整为 `open`、`close`、`high`、`low`、`volume`、`factor`，`amount` 仅在数据源真实提供时作为可选 feature 写入，绝不估算或合成。Sina 回退值按源端原样保存，并明确告警其价格口径不能保证与请求的复权选项一致。Provider 校验仍逐 instrument 严格匹配 DataFrame 实际字段、元数据、日历、二进制头、长度和 payload；任一核心字段或任一标的缺失都会使整体构建失败。Task 4 最终提交的内置 provider 后续由 EastMoney 主数据源对五只 ETF 全部生成成功，因此每个标的目录均含 7 个 feature 文件，其中 `amount` 为上游真实返回的成交额。

## 组件设计

### 默认标的清单

`download_to_qlib.py` 将单个 `SYMBOL`/`QLIB_SYMBOL` 常量替换为结构化的默认 ETF 清单。每项至少包含数据源代码、Qlib instrument 和说明名称。

命令行保留单标的覆盖能力，并增加批量默认行为。无显式标的参数时下载默认五个 ETF；显式传入时只构建指定标的，便于调试和扩展。

### 批量下载与 provider 构建

下载阶段先获取全部 DataFrame，再开始写 provider：

1. 逐个下载并标准化字段。
2. 校验每个结果非空、日期有序、必要字段存在。
3. 汇总所有日期，生成排序去重后的联合 calendar。
4. 写入每个 instrument 的二进制 feature 文件，并在首个 float 中保存其 calendar 起始索引。
5. 一次性写出全部 instrument 的起止日期。

先下载后写入可以避免某个标的下载失败后留下看似可用、实际不完整的 provider。

### Demo 默认股票池

`qlib-demos/01` 至 `14` 的 `run.sh` 统一将 `QLIB_INSTRUMENTS` 设置为五个默认 instrument 的逗号分隔列表。共享的 `qlib_demo_common.instruments()` 已支持这种格式，无需改变调用接口。

README 将说明默认数据是教学用 ETF 横截面，而不是完整股票池，并明确不同 ETF 上市时间不同。

## 错误处理

- 任一默认 ETF 下载失败、返回空数据或缺少必要字段时，构建整体失败。
- 错误信息必须包含 ETF 代码和失败阶段。
- 在全部下载和校验成功前，不覆盖现有 provider 文件。
- 写入阶段使用独立的临时 provider 目录；完整写入并验证后再替换目标目录，以避免中断导致半成品数据。
- 不静默跳过失败标的，也不自动回退到单标的模式。

## 测试与验收

自动化测试使用合成 DataFrame，不依赖实时网络，覆盖：

1. 多个 instrument 生成联合 calendar。
2. 不同上市日期产生正确的 feature 起始索引。
3. `instruments/all.txt` 包含五条独立起止区间记录。
4. feature 文件包含 Qlib 要求的索引头和正确数据。
5. 默认 instrument 清单能被共享环境变量格式正确解析。
6. `03-qlib-expressions/run.sh` 成功执行，输出非空并包含多个 instrument。

最终验收还包括：

- 使用实际 AkShare 数据重新生成仓库内 provider。
- 通过 Qlib `D.features` 读取五个 instrument 的 OHLCV。
- 运行 `01`、`02`、`03`、`06` 和 `09`，确认基础数据、表达式、横截面指标和策略示例能够执行。
- 检查二进制文件、calendar 和 instruments 元数据相互一致。

## 非目标

- 不扩展到完整 A 股股票池。
- 不引入分钟级数据、实时行情或自动定时更新。
- 不处理指数成分股历史、退市股票和生产级 point-in-time 股票池。
- 不引入 YAML/JSON 配置系统；默认清单直接保留在下载脚本中，以控制当前改动范围。
