# 13：如何接入自己的金融数据

这节解决一个真实落地问题：如果不用 Qlib 官方下载的数据，而是有自己的行情、财务、因子或另类数据，应该如何接入 Qlib 体系。

脚本不会真的生成 Qlib `.bin` 文件，因为那应该使用 Qlib 官方 `scripts/dump_bin.py`。本示例做的是接入前的最小准备：检查原始 CSV 字段、生成 calendar/instrument 摘要、模拟 provider 目录结构，并输出可以交给 `dump_bin.py` 的命令。

## 这个示例想说明什么

Qlib 数据不是普通 CSV 的原因在于：它要支持高效的时间序列读取、表达式计算、缓存、股票池和实验复现。官方文档说明 Qlib 使用专门的 `.bin` 格式管理金融数据，并提供 `scripts/dump_bin.py` 把格式正确的 CSV/Parquet 转换为 Qlib format。

所以自有数据接入不是“随便放一个 CSV 然后 import”，而是至少要解决：

- 字段命名：open、close、high、low、volume、factor 等。
- 日期字段：交易日必须可解析、可排序。
- 标的字段：symbol/instrument 必须稳定。
- 股票池：哪些标的在哪些日期可交易。
- 复权：价格和 factor 的定义要统一。
- 缺失：停牌、未上市、退市如何表示。
- 质量检查：是否有异常跳变、缺列、大量空值。

## 运行方式

```bash
python custom_data_provider.py
```

运行后会生成：

```text
artifacts/custom_provider_plan/
├── calendar.txt
├── instruments.txt
├── normalized_sample.csv
└── dump_bin_command.txt
```

这些不是最终 Qlib `.bin` 数据，而是接入前的准备产物。

## 用 AkShare 生成沪深 300 ETF 数据

本目录还提供了一个真实数据脚本：

```bash
python build_hs300_etf_from_akshare.py
```

它会用 AkShare 的 `fund_etf_hist_em` 下载 `510300`（华泰柏瑞沪深300ETF）日线，并生成：

```text
qlib-demos/qlib-data/hs300_etf_510300/
├── README.md
├── calendar.txt
├── instruments.txt
├── dump_bin_command.txt
└── csv/
    └── SH510300.csv
```

这仍然是 Qlib 转换前的规范 CSV 包。安装 Qlib 后，可以按 `dump_bin_command.txt` 里的命令转换成 Qlib bin provider。

## 原始数据最低要求

日频行情至少建议包含：

```text
symbol,date,open,high,low,close,volume,factor
```

其中：

- `date` 是交易日期。
- `symbol` 是标的代码。
- `open/high/low/close` 通常应使用复权口径。
- `volume` 是成交量。
- `factor` 是复权因子，口径必须明确。

如果有自定义因子，例如 PE、EPS、分析师预期，也可以作为额外字段一起转入 Qlib format，后续用 `$pe`、`$eps` 这类表达式读取。

## 和 Provider / DataLoader / DataHandler / Dataset 的关系

自有数据接入后，各层职责是：

- Provider：从 Qlib format 数据目录读取基础字段和表达式结果。
- DataLoader：根据 feature/label config 批量加载列。
- DataHandler：对列做清洗、标准化、缺失处理和学习/推理分离。
- Dataset：按 train/valid/test segment 给模型准备样本。

自有数据如果在 Provider 层就不干净，后面的 DataLoader、DataHandler、Dataset 都会继承这个问题。

## 自动因子挖掘系统怎么用 Qlib

自动因子挖掘可以把 Qlib 当成确定性评估引擎：

```text
Agent / Search 提出候选表达式
  ↓
检查表达式是否只用允许字段和过去数据
  ↓
Qlib Provider/DataLoader 计算 feature
  ↓
DataHandler/Dataset 构造样本
  ↓
IC / RankIC / 分层收益 / 回测
  ↓
Recorder 保存候选、参数、指标、artifact
  ↓
人或规则决定接受、拒绝、继续观察
```

关键原则：Agent 可以生成候选，但数值计算、时间对齐、评估和记录必须由确定性程序执行。

## 常见坑

- CSV 里价格未复权，但回测按复权收益解释。
- symbol 命名和 Qlib market/instrument 不一致。
- 缺少 factor 列，后续无法正确处理复权口径。
- 财务字段用报告期末日代替公告日，引入未来函数。
- 转换成 Qlib format 前没有做数据健康检查。

## 下一步

完成本节后，这条学习线已经覆盖 Qlib 的主要问题域：数据、表达式、特征集合、Dataset、模型、实验、回测、自有数据和自动因子评估。
