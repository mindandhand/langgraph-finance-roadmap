# Qlib 从基础到完整可运行示例

这是一条面向“已有一点金融和 Python 基础”的 Qlib 学习路径。每个子目录都是一个**独立可运行**的最小示例：前面尽快进入 Qlib 原生接口，后面逐步补齐 Dataset、模型、Recorder、策略回测和配置驱动 workflow。

Qlib 官方定位是 AI-oriented Quant investment platform，覆盖数据、特征、Dataset、模型、工作流、回测和实验记录。本目录不重复讲 Python/Pandas 基础，只保留必要的量化研究语义。

这条路径的目标不是“把 Qlib 所有 API 都扫一遍”，而是回答一个更实际的问题：

```text
如何从数据读取开始，一步步做出一个可运行、可复现、可记录、可回测的 Alpha 研究流程？
```

## 先理解 Qlib 的主线

可以把 Qlib 的核心工作流压缩成这条链：

```text
Data Provider
  ↓
Expression / Feature
  ↓
DataHandler
  ↓
Dataset / Segments
  ↓
Model
  ↓
Prediction Score
  ↓
Recorder / Experiment
  ↓
Strategy / Backtest
  ↓
Analysis / Report
```

本目录的 10 个示例就是按这条链铺开的。前几节用小数据把概念讲清楚，中间开始模拟 Qlib 的 Handler/Dataset/Recorder 思路，最后用配置把整条 Alpha workflow 串起来。

## 运行准备

大多数示例只需要：

```bash
pip install pandas numpy
```

涉及真实 Qlib 数据或原生 Qlib 组件时，需要：

```bash
pip install pyqlib
```

并准备 Qlib 数据目录，例如：

```bash
QLIB_PROVIDER_URI=~/.qlib/qlib_data/cn_data python qlib_data_api.py
```

## 学习路径

| # | 目录 | 主题 | 新增能力 |
|---|---|---|---|
| 1 | [`01-environment-and-data`](01-environment-and-data) | 环境和数据入口 | 检查 pyqlib、`QLIB_PROVIDER_URI`、内置数据回退 |
| 2 | [`02-qlib-data-api`](02-qlib-data-api) | Qlib Data API | `qlib.init`、`D.features`、字段读取 |
| 3 | [`03-qlib-expressions`](03-qlib-expressions) | Qlib 表达式 | `$close`、`Ref`、`Mean`、`Rank` 的研究含义 |
| 4 | [`04-data-handler-and-dataset`](04-data-handler-and-dataset) | Handler / Dataset | 特征列、标签列、segment prepare |
| 5 | [`05-labels-and-time-splits`](05-labels-and-time-splits) | 标签和时间切分 | forward return、train/valid/test、避免随机打乱 |
| 6 | [`06-factor-evaluation`](06-factor-evaluation) | 因子评估 | IC、Rank IC、分组收益 |
| 7 | [`07-model-training-baseline`](07-model-training-baseline) | 模型训练基线 | 最小线性模型、预测分数、样本外评估 |
| 8 | [`08-recorder-and-experiment`](08-recorder-and-experiment) | 实验记录 | params、metrics、artifacts、可复现记录 |
| 9 | [`09-strategy-and-backtest`](09-strategy-and-backtest) | 策略和回测 | top-k、换手、成本、Qlib strategy/backtest 对应关系 |
| 10 | [`10-config-driven-alpha-workflow`](10-config-driven-alpha-workflow) | 配置驱动 Alpha 流程 | 用 YAML/JSON 风格配置串起完整研究 |
| 11 | [`11-alpha158-alpha360-feature-sets`](11-alpha158-alpha360-feature-sets) | Alpha158 / Alpha360 | 预定义特征集合的本质和自定义因子扩展 |
| 12 | [`12-native-backtest-architecture`](12-native-backtest-architecture) | 原生回测架构 | Strategy、Executor、Exchange、Account 的协作 |
| 13 | [`13-custom-data-provider`](13-custom-data-provider) | 自有数据接入 | CSV/Parquet 到 Qlib format 的字段、目录、校验思路 |

## 每节之间怎么衔接

```text
01 先确认环境和数据入口
 ↓
02 第一次用 Qlib Data API 的方式读取字段
 ↓
03 理解 Qlib 表达式背后的时间序列/横截面计算
 ↓
04 把特征和标签组织成 Handler/Dataset 风格
 ↓
05 明确标签和 train/valid/test 时间切分
 ↓
06 在训练模型前先做单因子评估
 ↓
07 训练一个最小模型并产生样本外 score
 ↓
08 把一次性输出变成可追踪实验
 ↓
09 把 score 转成 top-k 策略并扣成本
 ↓
10 用配置串起完整 Alpha workflow
 ↓
11 拆开 Alpha158/Alpha360，理解预定义特征集合
 ↓
12 拆开 Qlib 原生回测架构
 ↓
13 学会把自己的金融数据接入 Qlib 体系
```

如果你已经熟悉 Pandas 和量化标签，可以从 `02-qlib-data-api` 开始。但建议至少快速跑一遍 `01`，确认当前环境有没有真实 Qlib 数据。

## 贯穿原则

- 不随机打乱金融时间序列。
- 模型分数不是交易收益，必须经过回测和成本检验。
- LLM/Agent 可以编排研究流程，但数值真值由确定性 Python、Pandas、NumPy 或 Qlib 计算。
- 每个实验都要能复现：固定输入、固定时间区间、固定输出路径。

## 为什么大量示例仍然用内置小数据

真实 Qlib 数据当然更接近生产研究，但教学示例如果一开始依赖完整数据下载、格式转换和市场配置，会把学习门槛抬得太高。这里采用“两层路径”：

- 默认路径：内置小数据，保证每个目录都能独立运行。
- 真实路径：设置 `QLIB_PROVIDER_URI` 后，相关示例优先尝试真实 Qlib 数据。

这样读者可以先理解 Qlib 的研究抽象，再替换成自己的数据目录。

## 和正式 Qlib 项目的差距

这个目录是学习路径，不是生产模板。它刻意简化了很多正式项目必须处理的问题：

- 大规模股票池和交易日历
- Qlib 原生 `DataHandlerLP` / `DatasetH`
- LightGBM 或深度模型
- 原生 Recorder 和 workflow manager
- 原生 portfolio analysis
- benchmark、风险归因、容量和交易约束

这些没有被忽略，而是被推迟。等 10 个示例跑通后，下一步才适合把手写组件逐个替换为 Qlib 原生组件。

## 建议的学习方式

每个目录都按同样节奏学习：

1. 先读 README，弄清楚这一节新增了什么。
2. 直接运行脚本，确认能看到输出。
3. 改一个小参数，例如日期、特征窗口、top-k 数量或成本率。
4. 再读代码，看输出变化从哪里来。
5. 最后想清楚这一节在完整 Alpha workflow 里负责哪一层。

不要一上来就改成真实市场大数据。先在小样本上把语义走通，再扩大数据规模。

## 官方文档入口

- Qlib Data Layer: https://qlib.readthedocs.io/en/latest/component/data.html
- Qlib Workflow: https://qlib.readthedocs.io/en/latest/component/workflow.html
- Qlib GitHub: https://github.com/microsoft/qlib

## 问题覆盖矩阵

完成 13 个示例后，可以系统回答这些问题：

| 问题 | 主要对应章节 |
|---|---|
| Qlib 解决了量化研究中的哪些问题 | 01、08、10、12 |
| Qlib 数据为何不是普通 CSV | 01、02、13 |
| Provider、DataLoader、DataHandler 和 Dataset 分别负责什么 | 02、04、11、13 |
| Alpha158、Alpha360 本质上是什么 | 11 |
| 如何用 Qlib 表达式实现自定义因子 | 03、11 |
| 标签、特征和预测分数之间是什么关系 | 04、05、07 |
| IC、RankIC、分层收益和组合回测分别衡量什么 | 06、09、12 |
| 模型预测结果为什么不能直接等同于策略收益 | 07、09、12 |
| Strategy、Executor、Exchange 和 Account 如何共同完成回测 | 12 |
| 如何记录、复现和比较实验 | 08、10 |
| 如何接入自己的金融数据 | 13 |
| 如何将 Qlib 用作自动因子挖掘系统的确定性评估引擎 | 06、08、10、11、13 |

## 完成后能做什么

跑完这 10 个示例后，你应该能独立解释并实现：

- 如何检查 Qlib 环境和数据入口。
- 如何用 Qlib Data API 读取基础字段。
- 如何把表达式理解成时间序列和横截面计算。
- 如何构造特征、标签和时间切分。
- 如何用 IC/Rank IC 做单因子评估。
- 如何训练一个最小模型并产生样本外 score。
- 如何记录实验参数、指标和 artifact。
- 如何把 score 转成策略回测。
- 如何用配置驱动一条完整 Alpha workflow。
- Alpha158 / Alpha360 这类预定义特征集合到底是什么。
- Qlib 原生回测里 Strategy、Executor、Exchange、Account 的职责边界。
- 自有数据接入 Qlib 前需要满足哪些字段、目录和质量约束。
