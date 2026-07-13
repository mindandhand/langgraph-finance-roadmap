# 使用 LangGraph 支持量化研究：从统计基础到多 Agent 因子挖掘

> **路线定位**：以中低频股票截面量化研究为主线，系统学习点时数据、因子构造、统计检验、稳健性验证、真实回测、风险模型、组合优化、机器学习和多 Agent 协同。LangGraph 作为研究流程的编排、约束、恢复和审计工具，而不是课程的最终目标。
>
> **最终目标**：形成接近顶级系统化量化机构研究岗位所要求的能力结构——能够提出可证伪的研究假设，使用严格数据和统计方法检验信号，识别数据窥探与虚假发现，将有效信号转化为受风险和成本约束的组合，并使用 LangGraph 构建可重复、可审查、可恢复的研究工作流。
>
> **安全边界**：本路线只涵盖历史研究、模拟回测、纸面组合和人工审批，不连接真实交易账户，不自动下单，不将历史表现描述为未来收益保证。

---

# 一、路线边界与目标定义

## 1.1 研究方向

本路线聚焦：

- 股票截面选股
- 日频或周频数据
- 1—60 个交易日左右的预测与持有周期
- 价值、质量、盈利、成长、投资、动量、反转、波动率、流动性、分析师预期和量价特征
- 单因子、多因子和机器学习 Alpha 模型
- 市场中性或受约束多空组合
- 因子研究自动化和多 Agent 协同验证

本路线暂不系统覆盖：

- 高频做市和订单簿建模
- 期权定价和波动率曲面
- 宏观 CTA
- 固定收益定价
- 加密货币微观结构
- 实盘订单执行系统
- 企业级多租户平台架构
- LangGraph 内核源码和 Runtime 实现

这些方向可以在完成本路线后作为独立分支继续学习。

## 1.2 LangGraph 在量化研究中的角色

LangGraph 主要解决：

- 将研究流程显式表示为 State、Node 和 Edge
- 控制研究步骤和依赖关系
- 在数据不足或检查失败时走不同路径
- 限制循环、工具调用和计算预算
- 并行运行不同样本、周期、成本和模型实验
- 保存研究状态并从中断位置恢复
- 在关键节点暂停并等待人工审核
- 组织多个研究 Agent 独立工作和相互复核
- 保存执行轨迹、证据引用和最终决策

LangGraph 不负责：

- 代替概率统计和计量经济学
- 代替研究员提出真正有价值的经济假设
- 代替确定性数值计算
- 自动证明因子具有未来 Alpha
- 消除数据质量、过拟合和市场变化风险

## 1.3 最重要的职责边界

```text
LLM / Agent：
- 提出候选研究假设
- 把自然语言转换为受约束的研究配置
- 选择需要运行的预定义检查
- 拆分任务和分配研究角色
- 识别证据缺口和解释冲突
- 汇总结构化证据并撰写报告

确定性 Python：
- 数据时间对齐
- 复权和公司行动处理
- 因子计算
- 截面预处理
- IC 和回归
- 多重检验
- 回测和交易成本
- 风险模型
- 组合优化
- 数值测试和发布门禁

人工研究员：
- 确认研究假设是否有价值
- 决定研究预算和最终测试集
- 审核统计证据与经济逻辑
- 处理无法由程序解决的冲突
- 批准、拒绝或要求补充测试
```

原则：**LLM 负责研究编排，Python 负责数值真值，研究员负责最终判断。**

---

# 二、最终能力模型

完成全部路线后，应具备以下六类能力。

## 2.1 数学与统计能力

- 理解概率、抽样分布、估计和假设检验
- 正确解释 p 值、置信区间、标准误和统计功效
- 使用多元回归、截面回归和稳健标准误
- 识别异方差、自相关、共线性和非独立样本
- 处理多重检验、虚假发现和回测过拟合
- 区分统计显著性、经济显著性和可交易性

## 2.2 数据与因子研究能力

- 构建点时正确的研究数据集
- 处理公告日、财报修订、退市、停牌和历史股票池
- 构造、预处理和标准化截面因子
- 完成 IC、分组收益、截面回归和因子衰减研究
- 评估因子在不同市场、股票池、周期和参数下的稳定性
- 判断因子是有效、无效、冗余、不可交易还是证据不足

## 2.3 回测和组合能力

- 正确区分信号日、下单日、成交日和收益实现区间
- 模拟手续费、价差、冲击、借券和容量约束
- 计算风险暴露、特异风险、风险贡献和收益归因
- 构建多因子 Alpha 模型
- 使用风险模型和约束优化形成组合
- 分析收益是否由少数股票、行业或市场阶段驱动

## 2.4 机器学习能力

- 构建时间顺序正确的训练、验证和测试集
- 使用线性、正则化和树模型建立可靠基线
- 处理标签重叠、Purging 和 Embargo
- 评估特征稳定性、模型漂移和预测衰减
- 比较模型的统计效果、成本后收益和增量价值

## 2.5 LangGraph 能力

- 设计量化研究 State Schema
- 区分 Agent、Subgraph、Node 和 Tool
- 构建条件路由、有限循环、并行分支和结果聚合
- 使用 Checkpoint、Interrupt 和 Resume
- 设计研究预算、终止条件和失败回退
- 测试节点、路由、Graph 和执行轨迹

## 2.6 多 Agent 协同能力

- 设计 Supervisor、Hypothesis、Auditor、Reviewer 和 Red-Team 角色
- 通过上下文隔离实现盲化评审
- 使用结构化任务和结果协议进行通信
- 处理 Agent 之间的冲突、重复任务和相关错误
- 比较单 Agent 与多 Agent 的成本和增量价值
- 确保多数意见不能替代统计证据

---

# 三、学习原则与研究纪律

## 3.1 学习比例

建议整体投入比例：

- 25%：概率统计、计量经济学和资产定价
- 30%：因子研究、稳健性和多重检验
- 20%：回测、风险模型和组合构建
- 15%：Python 研究工程和测试
- 10%：LangGraph 与多 Agent 编排

## 3.2 每一级必须完成的内容

每一级都包含：

1. 核心概念学习
2. 最小代码案例
3. 独立练习
4. 综合项目
5. 数值或流程测试
6. 失败案例复盘
7. 晋级考核

## 3.3 贯穿全路线的研究产物

每一级持续维护：

```text
research_protocol.md       # 研究协议、允许修改的范围和终止条件
data_contract.md           # 字段定义、时间语义、缺失规则和来源
factor_registry.yaml       # 因子定义、方向、版本和状态
experiment_manifest.yaml   # 数据、代码、参数、区间和产物版本
failure_log.md             # 失败实验、错误原因和修复记录
artifacts/                 # 因子矩阵、回测结果、图表和模型
reports/                   # 研究报告和审批记录
tests/                     # 数值、数据泄漏、节点和 Graph 测试
```

## 3.4 每个实验的最低元数据

```yaml
experiment_id:
factor_id:
factor_version:
economic_hypothesis:
formula:
dataset_version:
universe_version:
code_commit:
random_seed:
research_period:
validation_period:
final_holdout_period:
forward_horizon:
cost_model_version:
number_of_variants_tested:
multiple_testing_method:
artifact_refs:
decision:
```

## 3.5 研究循环的硬性限制

研究不得以“找到正 IC”或“达到显著性”为循环终止条件。

允许的最终状态：

```text
validated
rejected
insufficient_data
data_leakage_detected
statistically_weak
economically_weak
unstable
redundant
not_tradeable
budget_exhausted
requires_human_judgment
```

必须预先限制：

- 最大候选因子数量
- 最大参数变体数量
- 最大回测次数
- 最大研究循环次数
- 最大 LLM 调用次数
- 最大 Token 预算
- 最大计算预算
- 最终 Holdout 的查看次数

---

# 四、项目代码结构

建议使用 Monorepo：

```text
quant-research-langgraph/
├── README.md
├── pyproject.toml
├── .env.example
├── configs/
│   ├── factors/
│   ├── universes/
│   ├── backtests/
│   └── models/
├── src/
│   ├── data/
│   │   ├── loaders.py
│   │   ├── point_in_time.py
│   │   ├── corporate_actions.py
│   │   └── validators.py
│   ├── factors/
│   │   ├── definitions.py
│   │   ├── preprocess.py
│   │   ├── neutralization.py
│   │   └── registry.py
│   ├── statistics/
│   │   ├── ic.py
│   │   ├── regressions.py
│   │   ├── multiple_testing.py
│   │   └── bootstrap.py
│   ├── backtest/
│   │   ├── portfolio.py
│   │   ├── costs.py
│   │   ├── capacity.py
│   │   └── attribution.py
│   ├── risk/
│   │   ├── covariance.py
│   │   ├── factor_model.py
│   │   └── optimizer.py
│   ├── ml/
│   │   ├── datasets.py
│   │   ├── validation.py
│   │   ├── models.py
│   │   └── diagnostics.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes/
│   │   ├── routers/
│   │   ├── subgraphs/
│   │   └── workflows.py
│   ├── agents/
│   │   ├── supervisor.py
│   │   ├── hypothesis.py
│   │   ├── auditors.py
│   │   ├── reviewers.py
│   │   └── protocols.py
│   └── evaluation/
│       ├── datasets.py
│       ├── metrics.py
│       └── regression_suite.py
├── tests/
│   ├── unit/
│   ├── data_leakage/
│   ├── graph/
│   └── integration/
├── experiments/
├── artifacts/
├── reports/
└── docs/
```

大型 DataFrame、回测明细和模型文件不得直接放入 Graph State，只保存 URI、Artifact ID、版本和指标摘要。

---

# Level 0：前置能力检查

## 定位

Level 0 不是正式研究阶段，而是确保学习者具备进入路线所需的最低基础。

## 必须掌握

### Python

- 函数、类、模块和包
- NumPy 数组运算
- Pandas 索引、GroupBy、Merge 和 Rolling
- 虚拟环境和依赖管理
- Git 基础
- 单元测试基础

### 数学

- 代数运算
- 函数和导数
- 向量和矩阵
- 均值、方差和相关系数
- 基础概率

### 金融

- 股票价格和收益率
- 市值、成交量和换手率
- 多头、空头和基准
- 复权的基本含义

## 入门测试

学习者应能独立完成：

1. 从 CSV 读取多只股票的日频价格。
2. 按股票计算收益率和滚动波动率。
3. 使用 GroupBy 计算每日截面排名。
4. 编写一个简单的单元测试。
5. 解释为什么不能随机打乱金融时间序列后再划分训练集。

未通过时，先补充 Python、线性代数或概率基础。

---

# Level 1：量化研究数学、统计与 Python 基础

## 项目名称

**量化统计与研究工具库**

## 学习目标

建立后续因子研究必须依赖的概率统计、回归、矩阵计算和可测试 Python 工程基础。

## 量化与统计知识

### 收益与风险

- 简单收益率与对数收益率
- 累计收益与年化收益
- 超额收益
- 波动率、下行波动率
- 协方差和相关系数
- 偏度、峰度
- 最大回撤与回撤持续时间
- Sharpe、Sortino 和 Information Ratio

### 概率与抽样

- 随机变量
- 条件概率和贝叶斯公式
- 常见分布
- 期望、方差和协方差
- 大数定律
- 中心极限定理
- 抽样分布
- 标准误

### 统计推断

- 点估计和区间估计
- 置信区间
- 原假设和备择假设
- 一类错误、二类错误和统计功效
- p 值的正确解释
- 单侧和双侧检验
- 统计显著性与经济显著性

### 回归基础

- 一元与多元线性回归
- OLS 推导和矩阵形式
- 回归系数和残差
- 拟合优度
- 共线性
- 异方差
- 自相关
- 稳健标准误
- 模型设定错误

### 线性代数与优化

- 向量和矩阵运算
- 矩阵转置和逆
- 正定和半正定矩阵
- 特征值和特征向量
- 协方差矩阵
- 梯度和 Hessian 的基本含义
- 约束优化和凸优化基础

## Python 知识

- NumPy 向量化
- Pandas MultiIndex
- 时间序列索引
- Rolling、Expanding 和 EWM
- 分组运算与横截面变换
- 类型提示、`TypedDict`、`dataclass` 和 Pydantic
- 异常处理和日志
- 配置管理
- 可复现随机种子
- 单元测试和参数化测试
- 浮点误差和数值容差

## LangGraph 知识

本级只学习：

- Workflow 与 Agent 的区别
- 为什么应先实现普通 Python 基线
- Node 可以是普通确定性函数
- 最简单的线性 StateGraph
- State 中保存小型结构化数据

## 最小案例

1. 手工推导并用 NumPy 实现 OLS。
2. 计算收益、波动率、Sharpe 和最大回撤。
3. 使用模拟数据验证置信区间覆盖率。
4. 对异方差模拟数据比较普通标准误和稳健标准误。
5. 建立一个“加载数据 → 计算统计量 → 输出报告”的线性 Graph。

## 综合项目

构建可复用的量化统计工具库，至少包含：

- 收益与风险指标
- 描述统计
- 相关和秩相关
- OLS 和稳健标准误
- Bootstrap 基础
- 数值测试

## 常见错误

- 把高 Sharpe 直接解释为未来可持续
- 用相关关系替代因果关系
- 忽略样本数量和标准误
- 对金融收益直接假设完全独立同分布
- 使用循环而不是向量化进行大规模计算
- 没有设置数值容差导致测试不稳定

## 交付物

- `statistics/` 工具库
- 至少 30 个数值单元测试
- 一份模拟数据验证报告
- 一个基础线性 Graph

## 晋级标准

- 能手算并解释 OLS
- 能解释 p 值不是“原假设为真的概率”
- 能区分统计显著和经济显著
- 能独立实现 Rank Correlation
- 数值工具对标准模拟数据测试通过
- 不依赖 LLM 完成任何数值计算

---

# Level 2：点时数据、标签构造与研究数据工程

## 项目名称

**点时量化数据质量系统**

## 学习目标

建立不会因为未来函数、幸存者偏差或时间错位而产生虚假 Alpha 的研究数据集。

## 核心知识

### 时间语义

- Observation Date
- Period End Date
- Publication Date
- Effective Date
- Signal Date
- Order Date
- Fill Date
- Return Realization Window
- Point-in-time 数据
- As-of Join

### 行情和公司行动

- 前复权、后复权和总回报价格
- 股票拆分、分红和配股
- 退市收益
- 停牌、涨跌停和不可交易状态
- IPO 和退市股票
- 交易日历和时区

### 股票池

- 历史指数成分
- 上市时长要求
- 流动性过滤
- 微盘股过滤
- 可交易性过滤
- 幸存者偏差
- Universe Drift

### 财务与分析师数据

- 财报期末日与公告日
- 财报修订
- 同比和环比
- TTM 数据
- 分析师预测版本
- 一致预期的时间戳
- 数据供应商回填

### 标签构造

- 前瞻收益
- 开盘到开盘、收盘到收盘和 VWAP 收益
- 不同预测周期
- 重叠标签
- 标签泄漏
- 基准调整和行业调整收益

### 数据质量

- 缺失值机制
- 重复记录
- 异常值
- 覆盖率
- 字段单位
- 数据版本
- 数据血缘
- Schema 和 Data Contract

## LangGraph 知识

- `StateGraph`
- `TypedDict` State Schema
- Node
- Normal Edge
- Conditional Edge
- `START` 和 `END`
- 错误路由
- Artifact Reference
- Node 输入输出契约

## State 示例

```python
from typing import TypedDict


class DataResearchState(TypedDict):
    research_id: str
    dataset_version: str
    universe_version: str
    required_fields: list[str]
    validation_status: str
    validation_findings: list[dict]
    artifact_refs: dict[str, str]
    next_action: str
```

## 工作流程

```text
研究配置
  ↓
验证数据版本
  ↓
验证股票池历史成分
  ↓
验证字段时间语义
  ↓
检查复权和公司行动
  ↓
构造标签
  ↓
检查特征—标签时间重叠
  ├─ 失败 → 输出数据质量报告并终止
  └─ 通过 → 保存研究数据引用
```

## 最小案例

1. 对财报数据使用公告日执行 As-of Join。
2. 构造历史指数股票池并与当前成分对比。
3. 模拟退市股票被遗漏后对回测的影响。
4. 构造 1、5、20 日前瞻收益并验证日期边界。
5. 编写自动检测负向 Shift、未来字段和错误公告日的测试。

## 综合项目

构建“点时数据质量 Graph”，能够自动检查：

- 当前成分回填历史
- 财报期末日代替公告日
- 缺少退市股票
- 特征与标签时间重叠
- 复权价格使用不一致
- 股票不可交易但被假设成交
- 数据字段覆盖率突然变化

## 常见错误

- 使用今天的指数成分回测十年前
- 使用财报期末日作为信息可用时间
- 先看完整样本再决定缺失值过滤规则
- 对停牌股票假设可按收盘价成交
- 忽略退市收益
- 把完整 DataFrame 写入 Graph State

## 交付物

- 数据合同
- 点时 Join 工具
- 标签构造工具
- 数据质量 Graph
- 至少 20 个未来函数和时间对齐测试

## 晋级标准

- 能解释至少五类数据泄漏
- 能构造点时正确的财务数据集
- 能生成历史股票池
- 所有标签对齐测试通过
- Graph 在数据质量失败时不得继续计算因子

---

# Level 3：因子假设、因子构造与受约束 Tool Calling

## 项目名称

**结构化因子定义与计算 Agent**

## 学习目标

学会从经济假设出发设计因子，并使用受约束的 LLM 和 Tool Calling 将自然语言研究需求转换为可验证、可执行的因子配置。

## 量化知识

### 因子假设来源

- 风险补偿
- 行为偏差
- 信息扩散
- 投资者注意力
- 机构约束
- 流动性和交易摩擦
- 会计信息迟滞
- 数据伪相关

一个合格的因子假设必须说明：

- 为什么可能存在预测关系
- 预测方向
- 预测周期
- 适用股票池
- 信息可得时间
- 可能失效的市场环境
- 与已知因子的差异

### 因子构造方法

- 水平值
- 比率
- 差分
- 增长率
- 滚动均值与标准差
- 趋势斜率
- 残差
- 排名
- 条件特征
- 指数衰减
- 多字段组合

### 常见因子类别

- 价值：EP、BP、CFP 等
- 质量：ROE、毛利率、现金流质量等
- 盈利：利润率、资产回报等
- 投资：资产增长、资本开支等
- 成长：收入和利润增长等
- 动量：中期动量、残差动量等
- 反转：短期反转等
- 波动率：特异波动率、下行风险等
- 流动性：换手、Amihud 类指标等
- 分析师：预测修正、分歧等
- 量价：成交量变化、价格趋势和量价交互等

### 截面预处理

- 分位数裁剪
- MAD 去极值
- Rank Transform
- Z-score
- 行业中性化
- 市值中性化
- 多变量残差化
- 缺失值填补
- 因子方向统一
- 覆盖率和极端暴露

## LangGraph 与 LLM 知识

- Message 和 Prompt Template
- Structured Output
- Pydantic Schema
- Tool Calling
- Tool 参数验证
- 工具白名单
- 调用预算
- Tool 错误回退
- Agent Loop 的风险
- 确定性 Workflow 与 Agent 的边界
- 受约束因子 DSL

## 因子配置示例

```python
from pydantic import BaseModel, Field
from typing import Literal


class FactorSpec(BaseModel):
    factor_name: str
    family: Literal[
        "value", "quality", "growth", "investment",
        "momentum", "reversal", "volatility",
        "liquidity", "analyst", "price_volume"
    ]
    input_fields: list[str]
    operator: Literal[
        "level", "ratio", "difference", "growth",
        "rolling_mean", "rolling_std", "slope",
        "rank", "residual", "decay"
    ]
    lookback: int | None = None
    skip_recent: int = 0
    expected_direction: Literal[-1, 1]
    forward_horizons: list[int]
    winsorization: Literal["none", "quantile", "mad"]
    standardization: Literal["none", "rank", "zscore"]
    neutralize: list[Literal["industry", "log_market_cap"]]
    economic_rationale: str
    failure_conditions: list[str]
```

早期只允许使用预定义 Operator 和字段白名单，不允许模型自由生成并执行 Python。

## 工作流程

```text
自然语言研究需求
  ↓
解析经济假设
  ↓
生成 FactorSpec
  ↓
Schema 校验
  ↓
字段与时间语义检查
  ↓
调用确定性因子工具
  ↓
预处理和质量检查
  ↓
输出因子工件引用
```

## 最小案例

1. 将“过去一年收益，跳过最近一个月”转换为动量配置。
2. 将“盈利能力对行业和市值中性化”转换为基本面配置。
3. 拒绝不存在的字段和非法窗口。
4. 限制模型只能选择预定义操作符。
5. 对相同配置重复执行并验证结果一致。

## 综合项目

构建“受约束因子研究 Tool Calling Agent”，支持：

- 自然语言因子定义
- 经济逻辑说明
- 参数 Schema 校验
- 因子计算
- 去极值、标准化和中性化
- 数据和因子质量报告
- 因子版本创建

## 常见错误

- 让模型直接生成任意 Python 并执行
- 因子公式与经济假设不一致
- 先看结果再修改预测方向
- 没有记录尝试过的参数变体
- 中性化时使用未来行业分类
- 用自然语言结果替代数值工件

## 交付物

- Factor DSL
- Pydantic Schema
- 至少 10 个确定性因子工具
- Tool Calling Agent
- 因子定义和参数测试集

## 晋级标准

- 能解释因子假设与公式的区别
- 能判断一个任务应使用 Tool 还是 Agent
- 非法参数必须在执行前被拒绝
- 模型不得访问任意代码执行工具
- 每个因子都有版本和经济逻辑

---

# Level 4：单因子有效性研究与独立复核

## 项目名称

**单因子研究与双重审查系统**

## 学习目标

掌握从因子值到统计证据、经济解释和独立复核的完整单因子研究闭环。

## 量化知识

### IC 分析

- Pearson IC
- Spearman Rank IC
- 日度、周度和月度 IC
- IC 均值和标准差
- ICIR
- IC 胜率
- 滚动 IC
- IC 衰减
- 不同预测周期

### 分组与多空组合

- 等数量和等权重分组
- 分位数组合
- 分组单调性
- Top-Bottom Spread
- 多空收益和 Sharpe
- 因子覆盖率
- 换手率
- 持有期重叠

### 截面回归

- 单变量和多变量截面回归
- Fama–MacBeth 方法
- 时序平均系数
- Newey–West/HAC 标准误
- 控制行业、市值和已知风格因子
- 回归系数的经济含义

### 条件分析

- 行业分组
- 市值分组
- 流动性分组
- 市场涨跌状态
- 高低波动状态
- 因子暴露集中度

## LangGraph 知识

- 固定研究 Workflow
- 条件路由
- 研究步骤状态
- 数值节点与报告节点分离
- 结构化证据
- 结论一致性检查
- 单研究 Agent + 独立 Reviewer
- Agent 私有上下文基础

## Agent 角色

### Research Agent

- 根据研究协议解释结果
- 提出可能的经济机制
- 识别缺失的预定义检查
- 输出初步结论

### Statistical Reviewer Agent

- 读取匿名化指标
- 检查统计结论是否被夸大
- 检查 IC、分组和回归是否一致
- 检查样本量和标准误
- 输出接受、驳回或补充检查建议

Reviewer 在首次评审前不应看到因子名称和 Research Agent 的乐观叙事。

## State 示例

```python
class SingleFactorState(TypedDict):
    research_id: str
    factor_id: str
    factor_version: str
    dataset_version: str
    universe_version: str
    research_protocol: dict
    completed_steps: list[str]
    metrics_summary: dict
    evidence_refs: list[str]
    research_claims: list[dict]
    reviewer_findings: list[dict]
    decision: str
```

## 工作流程

```text
因子配置
  ↓
数据门禁
  ↓
因子计算和预处理
  ↓
IC 分析
  ↓
分组收益
  ↓
截面回归
  ↓
条件分析
  ↓
Research Agent 初步解释
  ↓
匿名 Statistical Reviewer
  ├─ 通过 → 输出研究报告
  ├─ 缺失检查 → 执行预定义补充检查
  └─ 证据弱 → 拒绝
```

## 最小案例

1. 研究 12-1 动量因子。
2. 研究一个随机噪声因子并正确拒绝。
3. 比较 IC 结论与分组收益是否一致。
4. 使用 Fama–MacBeth 控制市值和行业。
5. 让 Reviewer 识别“均值为正但不稳定”的结论夸大。

## 综合项目

完成至少三个因子的完整研究：

- 一个预期有效因子
- 一个明显无效因子
- 一个可能与已知因子冗余的因子

## 必须输出

- 经济假设
- 因子公式和版本
- 数据时间范围
- IC 和 ICIR
- 分组收益和单调性
- 截面回归
- 行业和市值条件结果
- 覆盖率和换手率
- 支持证据
- 反对证据
- 局限和失败场景
- 接受、拒绝或待验证结论

## 常见错误

- 只展示最好的持有周期
- 用全样本结果替代样本外结果
- 把平均 IC 为正直接解释为稳定 Alpha
- Reviewer 和 Research Agent 使用完全相同上下文
- 用 Agent 一致意见代替数值证据

## 交付物

- 单因子研究 Graph
- 三份完整研究报告
- Reviewer 结构化评分表
- 无效因子拒绝案例
- 至少 20 个 Graph 和结果一致性测试

## 晋级标准

- 能独立完成 IC、分组和 Fama–MacBeth
- 至少正确拒绝一个无效因子
- Reviewer 能发现预设的结论夸大案例
- 每项报告结论能追溯到具体证据工件
- 所有补充检查来自预注册白名单

---

# Level 5：稳健性、多重检验与有界研究循环

## 项目名称

**因子稳健性与虚假发现控制 Agent**

## 学习目标

建立能够识别数据窥探、参数挖掘、虚假显著和样本外衰减的严格验证流程。

## 量化知识

### 样本划分

- 样本内、验证集和最终 Holdout
- Expanding Window
- Rolling Window
- Walk-forward
- 时间顺序划分
- 市场阶段划分
- 地区和股票池外推

### 稳健性分析

- 子区间稳定性
- 参数邻域敏感性
- 持有周期敏感性
- 股票池敏感性
- 行业和市值分组
- 高低波动和牛熊市场
- 数据供应商差异
- 因子衰减和结构变化

### Bootstrap

- 普通 Bootstrap 的假设
- Block Bootstrap
- 时间依赖数据
- 置信区间
- 稳健性分布而不是单一数值

### 数据窥探与多重检验

- Researcher Degrees of Freedom
- Multiple Hypothesis Testing
- Family-wise Error Rate
- Bonferroni
- Holm 方法
- False Discovery Rate
- Benjamini–Hochberg
- 因子动物园
- 选择性报告
- Backtest Overfitting
- Deflated Sharpe Ratio 的思想
- 记录候选数量的重要性

## LangGraph 知识

- State 更新和 Reducer
- Conditional Routing
- 有限 Loop
- Recursion Limit
- `Command`
- 最大研究预算
- Retry 与错误回退
- Checkpoint 基础
- 提前终止
- 预定义验证计划

## 工作流程

```text
单因子初步结果
  ↓
锁定研究协议和最终 Holdout
  ↓
样本外验证
  ↓
参数邻域测试
  ↓
子区间与市场状态测试
  ↓
Block Bootstrap
  ↓
多重检验校正
  ↓
证据完整性检查
  ├─ 缺少预定义测试且预算允许 → 补充测试
  ├─ 结果不稳定 → 拒绝
  ├─ 数据不足 → 终止
  └─ 通过 → 进入可交易性研究
```

## 有界循环规则

循环只能用于补齐预注册检查，不允许：

- 自动尝试新窗口直到结果显著
- 自动替换股票池
- 反复查看最终 Holdout
- 删除表现不佳的市场阶段
- 改变因子方向
- 隐藏失败变体

## 最小案例

1. 对多个动量窗口执行 FDR 校正。
2. 构造只有样本内有效的模拟因子并拒绝。
3. 使用 Block Bootstrap 评估 IC 不确定性。
4. 对不同市场状态执行并行稳健性测试。
5. 达到最大研究预算后安全终止。

## 综合项目

构建“稳健性验证 Graph”，能够对候选因子输出：

- 样本内结果
- 样本外结果
- 参数敏感性
- 子区间稳定性
- 多重检验结果
- 因子衰减
- 研究尝试次数
- 最终接受或拒绝理由

## 常见错误

- 把验证集当作可以无限查看的训练集
- 对每个参数单独使用 5% 显著性水平
- 只报告最优窗口
- 普通 Bootstrap 忽略时间依赖
- 循环以结果变好作为终止条件

## 交付物

- 稳健性 Subgraph
- 多重检验工具
- Block Bootstrap 工具
- 研究预算和终止规则
- 至少一个回测过拟合模拟案例

## 晋级标准

- 能解释为什么测试 100 个因子会产生虚假发现
- 能正确实施至少一种 FDR 控制
- 能锁定并保护最终 Holdout
- Graph 永远不超过预设循环和预算
- 无法通过样本外测试的因子必须被拒绝

---

# Level 6：真实回测、交易成本与策略容量

## 项目名称

**成本和容量约束的因子回测系统**

## 学习目标

将统计上有效的因子转换为时间、成交和成本假设正确的可交易性研究。

## 量化知识

### 回测时间线

- Signal Date
- Order Date
- Fill Date
- Holding Period
- Return Realization Window
- 开盘、收盘和 VWAP 成交假设
- 调仓频率
- 权重漂移
- 重叠持仓

### 组合构建基础

- 等权和因子权重
- 分位数组合
- 多空组合
- Dollar Neutral
- Beta Neutral
- 行业中性
- 个股和行业权重限制

### 交易成本

- 手续费
- 买卖价差
- 滑点
- 市场冲击
- 换手率
- ADV 参与率
- 成交延迟
- 借券费率
- Short Availability

### 容量和可交易性

- 流动性
- 仓位规模
- 市场冲击随规模变化
- 微盘股依赖
- 集中度
- 容量曲线
- 成本后 Alpha 衰减

### 风险和归因

- 年化收益和波动率
- Sharpe 和 Sortino
- 最大回撤
- 尾部损失
- 行业和风格暴露
- 收益贡献
- 成本贡献
- 个股集中贡献

## LangGraph 知识

- Parallel Fan-out/Fan-in
- Subgraph
- Reducer
- 并发限制
- Timeout
- 失败分支
- 参数情景并行
- 结果汇总节点

## 工作流程

```text
已通过统计验证的因子
  ↓
构造信号和目标权重
  ↓
并行回测
  ├─ 低成本假设
  ├─ 基准成本假设
  ├─ 高成本假设
  ├─ 容量约束
  ├─ 借券约束
  └─ 成交延迟假设
       ↓
Reducer 合并结果
       ↓
风险和收益归因
       ↓
可交易性结论
```

## 最小案例

1. 比较 Close-to-Close 与 Next-Open 成交假设。
2. 模拟 10、50 和 100 bps 成本。
3. 限制单只股票占 ADV 的比例。
4. 增加借券不可用和借券成本。
5. 分析微盘股过滤前后的因子收益。

## 综合项目

构建“成本敏感的因子回测 Graph”，要求：

- 所有成交时间明确
- 不使用信号生成时不可获得的价格
- 支持多种成本情景
- 支持容量和借券约束
- 输出成本前后表现
- 输出风险和收益归因

## 常见错误

- 用当日收盘数据生成信号并按同一收盘价成交
- 只计算手续费，不计算价差和冲击
- 对所有股票假设无限流动性
- 忽略借券可用性
- 多空组合不控制行业和 Beta 暴露

## 交付物

- 回测引擎
- 成本模型
- 容量分析模块
- 并行情景 Subgraph
- 成本和容量报告

## 晋级标准

- 能明确解释信号到成交的完整时间线
- 能证明回测没有同日成交泄漏
- 至少评估三种成本情景
- 输出容量随资金规模变化的曲线
- 统计有效但成本后无效的因子必须被标记为 `not_tradeable`

---

# Level 7：多因子模型、风险模型与组合优化

## 项目名称

**多因子 Alpha 与风险约束组合系统**

## 学习目标

从单因子研究升级到因子选择、Alpha 合成、风险建模和约束组合优化。

## 量化知识

### 因子关系与冗余

- 因子值相关性
- 因子收益相关性
- 暴露相关性
- Rank Correlation
- 聚类
- 正交化
- 残差化
- 增量 IC
- 增量组合收益
- 条件有效性
- 因子拥挤

### 多因子 Alpha 模型

- 等权合成
- IC 加权
- ICIR 加权
- 线性回归
- Ridge
- Lasso
- Elastic Net
- 非线性交互
- 动态权重
- Regime-dependent Weight
- Shrinkage

### 风险模型

- 系统风险和特异风险
- 协方差矩阵
- 样本协方差的噪声
- Shrinkage Covariance
- 统计因子模型
- 基本面风险模型
- 因子暴露矩阵
- 因子协方差
- 特异方差
- 风险分解

### 组合优化

- 预期 Alpha
- 风险厌恶参数
- 均值—方差优化
- 交易成本惩罚
- 换手率约束
- 个股权重约束
- 行业约束
- Beta 约束
- 风格暴露约束
- 流动性约束
- Tracking Error
- 风险贡献和边际风险贡献
- 优化不稳定性
- 稳健优化基础

## LangGraph 知识

- Graph Composition
- 多个确定性 Subgraph
- 共享状态和私有状态
- 输入输出 Schema 转换
- 并行因子评估
- 结果依赖关系
- 冲突处理

## 子图设计

```text
Candidate Factor Subgraph
  ↓
Redundancy Analysis Subgraph
  ↓
Alpha Model Subgraph
  ↓
Risk Model Subgraph
  ↓
Cost Model Subgraph
  ↓
Portfolio Optimization Subgraph
  ↓
Attribution Subgraph
```

## 最小案例

1. 比较等权、IC 加权和 Ridge 合成。
2. 识别两个高度相关的动量变体。
3. 构建简单统计风险模型。
4. 在行业、Beta 和换手率约束下优化组合。
5. 计算组合风险贡献和收益归因。

## 综合项目

构建“多因子 Alpha 与风险组合 Graph”：

- 输入候选因子库
- 进行冗余和增量价值分析
- 选择或合成因子
- 构建风险模型
- 应用交易成本
- 进行约束优化
- 完成组合回测和归因

## 常见错误

- 用同一数据选择因子又评估组合
- 只根据单因子 IC 选择因子
- 协方差矩阵不稳定
- 优化器产生极端权重
- 忽略因子之间的交互和冗余
- 把优化后的高收益归因于信号而不是约束变化

## 交付物

- 因子冗余报告
- Alpha 合成模块
- 风险模型
- 约束优化器
- 组合归因报告

## 晋级标准

- 能解释因子值相关和因子收益相关的区别
- 能计算增量 IC 和增量组合价值
- 能构建并验证风险模型
- 优化结果满足全部约束
- 能识别优化器产生的不稳定和极端解

---

# Level 8：机器学习因子研究与实验评估

## 项目名称

**机器学习截面 Alpha 研究系统**

## 学习目标

在严格时间验证、成本和风险约束下，将机器学习用于截面收益预测和排序。

## 机器学习知识

### 问题定义

- 截面回归
- 排序问题
- 分类问题
- 连续标签与离散标签
- 原始收益、超额收益和残差收益标签
- 预测周期

### 模型

- 线性回归基线
- Ridge、Lasso 和 Elastic Net
- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost/LightGBM 类模型
- 模型集成
- 非线性和特征交互

### 时间验证

- 时间顺序切分
- Expanding 与 Rolling Training Window
- Purging
- Embargo
- 重叠标签
- Nested Validation
- 最终 Holdout

### 特征研究

- 特征标准化
- 缺失值
- 特征选择
- Permutation Importance
- SHAP 的解释边界
- 特征稳定性
- 特征漂移
- 共线性
- 泄漏特征

### 模型评价

- MSE 和 MAE
- Rank IC
- Top-K Precision
- 分组收益
- 成本后组合表现
- Calibration
- 模型预测衰减
- 模型收益归因
- 简单模型基线

## LangGraph 知识

- Map-Reduce
- 实验 Fan-out/Fan-in
- 模型配置结构化
- 并行训练
- 统一评分
- 实验结果 Reducer
- Graph Evaluation
- Mock Tool 和 Mock Model
- 回归测试

## 工作流程

```text
锁定数据切分和最终 Holdout
  ↓
生成模型实验配置
  ↓
并行训练
  ├─ Linear
  ├─ Ridge
  ├─ Elastic Net
  ├─ Random Forest
  └─ Gradient Boosting
       ↓
统一样本外评分
       ↓
成本和风险约束回测
       ↓
模型稳定性与特征诊断
       ↓
选择或拒绝模型
```

## 最小案例

1. 比较随机切分与时间切分产生的差异。
2. 对重叠标签实施 Purging 和 Embargo。
3. 比较线性模型和树模型的样本外 Rank IC。
4. 对特征置换后观察性能变化。
5. 构造一个泄漏特征并确保门禁能够发现。

## 综合项目

构建“机器学习截面 Alpha Graph”，比较至少四类模型，并确保：

- 相同训练、验证和测试区间
- 相同特征集和成本模型
- 相同风险约束
- 最终 Holdout 只使用一次
- 输出统计和组合两类评价

## 评估体系

### 数值层

- 特征计算正确率
- 标签对齐正确率
- 模型评分正确率
- 回测正确率

### 模型层

- 样本外 Rank IC
- IC 稳定性
- 成本后 Sharpe
- 特征稳定性
- 模型漂移

### Workflow 层

- 路由正确率
- 非法 Holdout 访问率
- 实验重复率
- 失败恢复率
- 预算超限率

## 常见错误

- 随机打乱时间序列
- 在完整数据上做特征选择
- 使用测试集调参
- 把特征重要性解释为因果关系
- 只比较预测误差，不比较组合结果
- 复杂模型没有超过线性基线

## 交付物

- ML 数据集构建模块
- 时间验证器
- 模型实验 Graph
- 模型比较报告
- 泄漏和回归测试集

## 晋级标准

- 所有模型使用完全相同的数据协议
- 能解释 Purging 和 Embargo
- 复杂模型必须与线性基线比较
- 最终 Holdout 不得被自动循环访问
- 能拒绝样本内优秀但样本外衰减的模型

---

# Level 9：多 Agent 因子发现与协同验证

## 项目名称

**多 Agent 因子发现与独立验证系统**

## 学习目标

掌握多个研究 Agent 如何在明确角色、有限权限、上下文隔离和结构化通信协议下协同完成假设生成、数据审查、统计验证、可交易性评估、反方审查和证据裁决。

多 Agent 的目标不是增加角色数量，而是：

- 提高候选假设的差异性
- 并行执行独立研究任务
- 通过盲化评审减少叙事偏误
- 通过 Red-Team 降低确认偏误
- 发现研究遗漏和证据冲突
- 保留完整支持和反对意见

## Agent、Subgraph 和 Tool 的边界

### Agent

适合：

- 提出候选经济假设
- 拆分研究任务
- 选择预定义验证计划
- 判断证据是否完整
- 挑战研究结论
- 综合冲突意见

### Subgraph

适合：

- 点时数据质量检查
- 单因子统计研究
- 稳健性测试
- 多重检验
- 交易成本和容量分析
- 风险模型和组合优化

### Tool

适合：

- 因子计算
- Winsorize
- 中性化
- IC
- 回归
- Bootstrap
- 回测
- 交易成本
- 优化

不得把每个数值函数包装成 Agent。

## 核心 Agent 团队

```text
Research Supervisor
├─ Hypothesis Agent
├─ Data Auditor Agent
├─ Statistical Reviewer Agent
├─ Portfolio & Cost Reviewer Agent
├─ Red-Team Agent
└─ Evidence Synthesizer
```

### 1. Research Supervisor

职责：

- 创建研究协议
- 分配任务
- 控制依赖和预算
- 检查任务重复
- 决定是否执行补充验证
- 将冲突提交裁决
- 将最终结果提交人工审核

禁止：

- 修改数值结果
- 解锁最终 Holdout
- 因多数 Agent 同意而自动批准因子

### 2. Hypothesis Agent

职责：

- 提出经济或行为假设
- 生成 FactorSpec
- 说明预测方向和周期
- 列出可能失效条件
- 说明与已有因子的区别

可以并行部署：

- 行为金融 Hypothesis Agent
- 基本面 Hypothesis Agent
- 量价 Hypothesis Agent

这些 Agent 必须先独立生成，再统一去重。

### 3. Data Auditor Agent

职责：

- 检查时间语义
- 检查股票池和退市数据
- 检查公告日和修订
- 检查标签重叠
- 检查数据覆盖率
- 检查未来函数

禁止修改因子参数以改善结果。

### 4. Statistical Reviewer Agent

职责：

- 检查 IC、分组和回归
- 检查稳健标准误
- 检查样本外结果
- 检查多重检验
- 检查参数敏感性
- 判断结论是否夸大

盲化要求：首次评审时不显示因子名称、经济故事和其他 Agent 的意见。

### 5. Portfolio & Cost Reviewer Agent

职责：

- 检查换手和成本
- 检查借券和容量
- 检查行业、Beta 和风格暴露
- 检查组合集中度
- 检查多因子增量价值
- 区分统计 Alpha 和可交易 Alpha

### 6. Red-Team Agent

职责是尝试推翻因子：

- 搜索隐藏未来函数
- 检查参数选择偏差
- 检查单一时期依赖
- 检查少数股票或行业驱动
- 检查微盘和低流动性依赖
- 检查冗余
- 检查多重检验
- 检查数据供应商特有现象

Red-Team 只能创建挑战任务，不能修改或删除原实验。

### 7. Evidence Synthesizer

职责：

- 合并结构化证据
- 区分事实、统计结果、解释和推测
- 记录支持和反对证据
- 标记未解决冲突
- 形成接受、拒绝或补充测试建议

禁止产生新的数值结论。

## 必须掌握的协同模式

### Router

用于一次性分类：

```text
研究请求
├─ 数据问题
├─ 因子定义
├─ 统计验证
├─ 回测与成本
└─ 组合研究
```

### Supervisor / Subagents

用于动态任务管理：

```text
Supervisor
→ Data Auditor
→ Statistical Reviewer
→ 根据结果调用稳健性 Subgraph
→ Red-Team
→ Evidence Synthesizer
```

### Parallel Fan-out / Fan-in

用于独立实验：

```text
同一候选因子
├─ 多预测周期
├─ 多股票池
├─ 多市场状态
├─ 多成本情景
└─ 多参数邻域
       ↓
Reducer
       ↓
稳定性证据
```

### Handoff

用于研究所有权变化：

```text
Hypothesis
→ Data Audit
→ Statistical Review
→ Red-Team
→ Human Review
```

### Reviewer–Critic

```text
研究结论
→ Reviewer 找证据缺口
→ Critic 尝试推翻
→ 原研究 Agent 回应
→ 独立裁决节点
```

最多允许固定轮数，禁止无限辩论。

### Independent Ensemble

多个 Hypothesis Agent 独立提出候选，之后执行：

- 公式规范化
- 语义去重
- 已有因子相关性检查
- 研究预算分配

相同模型、相同 Prompt 和相同上下文的重复输出不等于真正独立意见。

## 上下文工程与盲化

推荐信息防火墙：

```text
Hypothesis Agent：
- 看研究主题和经济背景
- 不看最终 Holdout

Data Auditor：
- 看数据合同和元数据
- 不看因子表现

Statistical Reviewer：
- 看匿名数值结果
- 不看因子故事和其他 Reviewer 意见

Portfolio Reviewer：
- 看信号和组合工件
- 不允许修改统计结果

Red-Team：
- 看完整证据
- 不能删除或覆盖原实验

Evidence Synthesizer：
- 看全部审查结果
- 不能生成新数值
```

## Agent 通信协议

### TaskSpec

```python
class AgentTask(TypedDict):
    task_id: str
    parent_task_id: str | None
    agent_role: str
    objective: str
    allowed_tools: list[str]
    input_artifact_refs: list[str]
    dataset_version: str
    experiment_version: str
    budget: dict
    blind_fields: list[str]
    deadline_steps: int
```

### AgentResult

```python
class AgentResult(TypedDict):
    task_id: str
    agent_role: str
    status: str
    findings: list[dict]
    claims: list[dict]
    evidence_refs: list[str]
    limitations: list[str]
    requested_followups: list[dict]
    confidence: float
    tool_calls_used: int
    token_cost: int
```

### ResearchClaim

```python
class ResearchClaim(TypedDict):
    claim_id: str
    claim_type: str
    statement: str
    supporting_evidence_refs: list[str]
    contradicting_evidence_refs: list[str]
    statistical_status: str
    economic_status: str
    reviewer_status: str
```

### ConflictRecord

```python
class ConflictRecord(TypedDict):
    conflict_id: str
    agent_a: str
    agent_b: str
    disputed_claim: str
    evidence_a: list[str]
    evidence_b: list[str]
    resolution_method: str
    resolution: str | None
```

## 共享状态和私有状态

### Parent Graph State

只保存：

- 研究目标
- 任务列表
- 因子和实验版本
- 数据版本
- 工件引用
- 研究预算
- 冲突记录
- 最终决策

### Agent 私有状态

保存：

- 角色提示词
- 局部消息历史
- 当前任务上下文
- 尚未提交的草稿结论

不同 Agent 的消息历史不得自动合并到 Parent State。

## 冲突解决规则

不得使用简单多数投票作为最终裁决。

冲突处理顺序：

1. 检查数据、代码和实验版本是否一致。
2. 检查指标定义和样本区间是否一致。
3. 调用确定性节点重新计算。
4. 比较原始工件，而不是 Agent 摘要。
5. 判断冲突属于事实、统计还是经济解释。
6. 事实和数值冲突由确定性程序裁决。
7. 统计解释冲突交由独立 Reviewer。
8. 经济解释冲突可以同时保留。
9. 无法解决的冲突必须披露。
10. 重大冲突未解决时不得批准。

## Agent 权限

| Agent | 允许 | 禁止 |
|---|---|---|
| Hypothesis | 创建候选定义 | 查看最终 Holdout |
| Data Auditor | 运行数据检查 | 修改因子参数 |
| Statistical Reviewer | 读取匿名实验结果 | 重新选择最优参数 |
| Portfolio Reviewer | 运行成本和风险分析 | 修改统计结果 |
| Red-Team | 创建挑战实验 | 删除支持证据 |
| Supervisor | 分配任务和控制预算 | 覆盖工具输出 |
| Synthesizer | 合并证据 | 自行产生新数值 |
| Human Reviewer | 批准或拒绝 | 覆盖历史实验记录 |

## 完整工作流程

```text
研究主题
  ↓
Supervisor 创建研究协议
  ↓
多个 Hypothesis Agent 独立生成候选
  ↓
语义、公式和已有因子去重
  ↓
Data Auditor 数据门禁
  ├─ 失败 → 拒绝或修复数据
  └─ 通过
       ↓
确定性因子研究 Subgraph
       ↓
并行审查
  ├─ Statistical Reviewer
  ├─ Portfolio & Cost Reviewer
  ├─ Robustness Subgraph
  └─ Red-Team
       ↓
Evidence Synthesizer
       ↓
冲突检查
  ├─ 有重大冲突 → 运行有限补充实验
  └─ 无重大冲突
       ↓
Interrupt 等待人工审批
  ├─ 接受监控
  ├─ 拒绝
  ├─ 修改后重跑
  └─ 补充测试
```

## LangGraph 知识

- Supervisor 与 Subagent
- Router
- Handoff
- Subgraph 私有 State
- `Command`
- Parallel Execution
- Reducer
- Checkpoint
- `thread_id`
- Interrupt 和 Resume
- 状态修改
- Agent 任务幂等性
- 重复任务检测
- 权限和 Tool 白名单
- 研究预算和并发限制

## 最小案例

1. Router 分配数据、统计或组合任务。
2. 三个 Hypothesis Agent 独立生成候选并去重。
3. Reviewer 在匿名条件下审查结果。
4. Red-Team 创建挑战实验。
5. 两个 Agent 冲突时调用确定性复算。
6. 子 Agent 失败时返回结构化错误。
7. 研究预算耗尽后安全结束。
8. 人工驳回后通过 Resume 继续执行。
9. 所有结论追踪到 Agent、工具和工件。
10. 与单 Agent 基线比较。

## 综合项目

构建“多 Agent 因子发现与独立验证系统”，必须支持：

- 多 Agent 独立假设生成
- 候选语义和公式去重
- 数据泄漏独立审查
- 统计盲化评审
- 并行稳健性测试
- 成本和容量审查
- Red-Team 挑战
- 冲突记录和裁决
- Agent 权限隔离
- 研究预算控制
- 人工最终审批
- Checkpoint 和恢复

## 评估指标

### 研究质量

- 非重复候选比例
- 数据泄漏发现率
- 虚假正例接受率
- 样本外失败识别率
- 不可交易因子识别率
- 冗余因子识别率

### 协同质量

- 任务路由准确率
- 重复任务率
- 结构化结果合格率
- 无证据结论比例
- 冲突发现率
- 冲突正确解决率
- 不必要 Agent 调用比例

### 系统效率

- 平均模型调用次数
- 平均 Token 成本
- 平均运行时间
- 并行加速比
- 失败恢复率
- 预算超限率

### 多 Agent 增量价值

必须回答：

- 是否发现更多非重复假设？
- 是否提高数据泄漏发现率？
- 是否降低虚假正例接受率？
- 是否改善样本外决策？
- 增加的成本是否合理？

## 常见错误

- 把每个函数包装成 Agent
- Agent 共享完整上下文导致相互影响
- 多数投票替代统计验证
- Supervisor 同时生成、验证和批准
- Reviewer 提前看到因子故事
- Agent 自由讨论直到达成共识
- 多 Agent 没有单 Agent 基线
- 成本明显增加但质量没有改善

## 交付物

- 六角色多 Agent Graph
- Agent 通信协议
- 权限矩阵
- 盲化评审测试
- 冲突解决案例
- 单 Agent 与多 Agent 对照报告

## 晋级标准

- 能解释 Router、Supervisor、Handoff 和并行 Subgraph 的区别
- 能判断任务应是 Agent、Subgraph 还是 Tool
- 实现至少三个不同权限的 Agent
- 实现结构化任务和结果协议
- 实现 Agent 私有 State
- 实现任务去重和研究预算
- 实现 Reviewer 和 Red-Team 独立审查
- 实现至少一种冲突裁决机制
- 多 Agent 必须在至少一个预注册指标上优于单 Agent
- 没有增量价值时能够退回单 Graph

---

# Level 10：独立因子研究毕业项目与研究操作系统

## 项目名称

**可复现、可审计的半自动因子研究员**

## 学习目标

综合使用统计、数据、因子、回测、风险、机器学习和多 Agent 协同，独立完成一个严格、可复现且允许失败的量化研究项目。

本级不要求学习 LangGraph 内核，也不要求搭建大规模平台。

## 毕业研究要求

独立提出一个原创或经过实质改造的因子假设，并完成：

1. 经济、行为或市场摩擦逻辑
2. 可证伪的预测
3. 点时数据说明
4. 字段和股票池定义
5. 因子公式与版本
6. 数据清洗和缺失规则
7. 去极值、标准化和中性化
8. IC 和 ICIR
9. 分组收益和单调性
10. Fama–MacBeth 或等价截面检验
11. 样本外测试
12. 参数敏感性
13. 市场状态和子区间测试
14. Block Bootstrap
15. 多重检验校正
16. 因子衰减
17. 换手率和交易成本
18. 容量和借券分析
19. 风险暴露和集中度
20. 与已有因子的冗余
21. 多因子增量价值
22. 组合构建和约束优化
23. 收益和风险归因
24. Red-Team 挑战
25. 接受、拒绝或继续观察决策

## 最终 Graph

```text
研究主题
  ↓
研究协议和预算
  ↓
多 Agent 候选假设
  ↓
数据门禁
  ↓
因子构造
  ↓
单因子统计研究
  ↓
稳健性与多重检验
  ↓
真实回测和成本
  ↓
冗余与多因子增量分析
  ↓
风险模型和组合优化
  ↓
独立 Reviewer 与 Red-Team
  ↓
证据合并和冲突裁决
  ↓
Interrupt 人工审批
  ↓
最终研究报告
```

## 必须包含的系统能力

- 因子 DSL
- 点时数据门禁
- 确定性数值工具
- 有限研究循环
- 并行实验
- Checkpoint 和恢复
- 因子与实验版本
- Agent 任务和权限协议
- 盲化审查
- Red-Team
- 人工审批
- 执行轨迹和证据引用

## 最终交付物

```text
README.md
research_protocol.md
data_contract.md
factor_definition.md
factor_registry.yaml
experiment_manifest.yaml
Graph 流程图
State Schema
Agent 权限矩阵
数值测试报告
数据泄漏测试报告
单因子报告
稳健性报告
多重检验报告
交易成本与容量报告
风险与归因报告
多 Agent 对照评估
失败实验日志
最终接受或拒绝决策
可复现代码和配置
```

## 毕业标准

### 数值正确性

- 标准数据集上的数值测试通过
- 日期泄漏测试通过率 100%
- 相同配置重复运行结果一致
- 所有指标定义有测试

### 研究纪律

- 预注册研究协议
- 记录全部候选和变体
- 最终 Holdout 未被反复访问
- 保存失败实验
- 多重检验方法明确
- 不选择性隐藏负面证据

### 研究质量

- 经济逻辑与因子暴露一致
- 样本外证据充分
- 成本后结果明确
- 风险和容量限制明确
- 冗余和增量价值明确
- 最终结论允许是拒绝

### LangGraph 与多 Agent

- 所有 Graph 路由和终止条件可测试
- 大型数据只使用 Artifact Reference
- Agent 权限正确隔离
- Reviewer 和 Red-Team 独立
- 冲突有结构化记录
- 多 Agent 增量价值有量化对照

---

# 五、Level 0 + 十级项目演进总览

| 等级 | 量化研究重点 | LangGraph / Agent 重点 | 综合项目 |
|---|---|---|---|
| 0 | Python、数学、金融前置 | 无 | 前置能力测试 |
| 1 | 概率统计、回归、研究工程 | 线性 Graph | 量化统计工具库 |
| 2 | 点时数据、标签和数据质量 | State、Node、Edge、路由 | 点时数据质量系统 |
| 3 | 因子假设、构造和预处理 | Structured Output、Tool Calling | 因子定义与计算 Agent |
| 4 | IC、分组、截面回归 | 固定 Workflow、独立 Reviewer | 单因子研究系统 |
| 5 | 稳健性、多重检验 | 有限循环、预算、Checkpoint | 稳健性验证 Agent |
| 6 | 回测、成本和容量 | 并行 Subgraph、Reducer | 成本约束回测系统 |
| 7 | 多因子、风险模型、优化 | Graph Composition | 多因子组合系统 |
| 8 | 机器学习和时间验证 | Map-Reduce、实验评估 | ML Alpha 研究系统 |
| 9 | 因子发现、独立审查 | 多 Agent、Handoff、Interrupt | 多 Agent 因子研究系统 |
| 10 | 独立完整研究 | 综合编排和人工审批 | 半自动因子研究员 |

---

# 六、学习密度与推荐拆分

Level 0 与十个正式 Level 并非等量章节。建议按以下实际单元学习：

```text
基础阶段
0   前置测试
1A  概率统计和回归
1B  Python 量化研究工程
2A  点时行情和股票池
2B  财务数据和标签对齐

因子研究阶段
3A  因子假设和构造
3B  Tool Calling 和因子 DSL
4A  IC、分组和回归
4B  独立 Reviewer
5A  稳健性和样本外
5B  多重检验和有界循环

投资实现阶段
6A  真实回测时间线
6B  成本、容量和借券
7A  因子冗余和 Alpha 合成
7B  风险模型和组合优化
8A  ML 时间验证
8B  ML 实验评估

协同研究阶段
9A  Supervisor 和 Subagents
9B  盲化 Reviewer 和 Red-Team
9C  冲突裁决、Checkpoint 和审批
10  毕业研究
```

---

# 七、阶段门禁

## Gate A：进入因子研究前

必须能够：

- 正确计算收益和风险指标
- 解释 OLS 和稳健标准误
- 构造点时正确的前瞻收益
- 识别未来函数和幸存者偏差
- 编写数值测试

## Gate B：进入稳健性研究前

必须能够：

- 完成单因子 IC、分组和截面回归
- 正确拒绝一个无效因子
- 记录因子和实验版本
- 区分研究、验证和最终 Holdout

## Gate C：进入多因子和机器学习前

必须能够：

- 完成多重检验
- 完成成本和容量回测
- 识别因子冗余
- 证明没有日期泄漏
- 使用普通 Python 和单 Graph 建立可靠基线

## Gate D：进入多 Agent 前

必须证明：

- 单 Agent 或单 Graph 已有稳定测试
- 确实存在可并行或需独立审查的任务
- Agent 有不同权限和上下文
- 可以量化多 Agent 的增量价值
- 多 Agent 失败时能够退回单 Graph

## Gate E：毕业前

必须：

- 完成独立研究
- 保留全部失败实验
- 锁定最终 Holdout
- 完成 Red-Team 和人工审批
- 给出接受或拒绝的明确结论

---

# 八、评估体系

## 8.1 数值正确性

- 因子计算正确率
- 前瞻收益对齐正确率
- IC 和回归正确率
- 回测和成本正确率
- 风险和优化约束正确率

数值正确性只能由标准答案、模拟数据或确定性程序验证，不能主要依赖 LLM-as-Judge。

## 8.2 数据质量

- 未来函数检测率
- 幸存者偏差检测率
- 点时 Join 正确率
- 标签泄漏检测率
- 数据版本完整率

## 8.3 研究质量

- 样本外通过率
- 虚假正例接受率
- 参数敏感性
- 子区间稳定性
- 成本后有效率
- 冗余因子识别率
- 最终结论与证据一致率

## 8.4 Graph 质量

- 路由准确率
- 必要节点执行率
- 非法跳过率
- 循环安全终止率
- 失败恢复率
- 状态字段正确率
- 工件引用完整率

## 8.5 Agent 质量

- 结构化参数准确率
- 工具选择准确率
- 无证据结论比例
- Reviewer 结论准确率
- Red-Team 漏检率
- 冲突发现和解决率
- 不必要调用比例

## 8.6 效率

- 平均执行时间
- 平均 LLM 调用次数
- Token 成本
- 计算任务数
- 并行加速比
- 预算超限率

---

# 九、必须准备的测试数据集

至少准备以下类别：

## 数值测试

- 手工可验证的小型价格数据
- 模拟线性回归数据
- 模拟已知 IC 的因子数据
- 已知最优解的组合优化数据

## 数据泄漏测试

- 错误使用财报期末日
- 当前指数成分回填历史
- 使用未来行业分类
- 特征和标签窗口重叠
- 同日信号和成交
- 最终 Holdout 被重复访问

## 因子研究测试

- 稳定有效模拟因子
- 纯随机因子
- 样本内有效、样本外失效因子
- 与已知因子完全冗余的因子
- 由微盘股驱动的因子
- 成本后失效的高换手因子

## Agent 测试

- 非法字段请求
- 非法参数窗口
- 诱导跳过数据检查
- 诱导访问最终 Holdout
- Reviewer 被乐观叙事干扰
- Agent 之间数值冲突
- Supervisor 重复分配任务
- Red-Team 漏掉预设漏洞

---

# 十、最重要的避坑原则

## 量化研究

- 不要把相关关系自动解释为因果关系
- 不要使用今天的股票池研究历史
- 不要使用信息发布前的数据
- 不要先看结果再决定预测方向
- 不要只报告最优参数
- 不要忽略多重检验
- 不要反复查看最终 Holdout
- 不要忽略失败因子
- 不要只看统计显著，不看经济显著
- 不要忽略交易成本、容量和借券
- 不要用单一市场阶段证明稳定性
- 不要把历史收益描述为未来保证

## LangGraph

- 不要把所有函数都做成 Node
- 不要把 DataFrame 和模型文件放进 State
- 不要创建无终止条件的循环
- 不要让 LLM 修改确定性数值结果
- 不要用 Checkpoint 代替正式实验数据库
- 不要在没有普通 Python 基线时直接使用复杂 Graph
- 不要为了展示框架而增加无价值步骤

## 多 Agent

- 不要把每个工具包装成 Agent
- 不要让所有 Agent 看到相同完整上下文
- 不要用多数投票代替统计证据
- 不要让提出假设的 Agent 同时批准结果
- 不要让 Reviewer 提前看到故事和其他意见
- 不要让 Agent 无限辩论
- 不要在没有增量价值时保留多 Agent
- 不要只保存共识而删除异议

---

# 十一、完成后的水平定位

## 完成 Level 1—3

能够：

- 完成基础量化数据处理
- 构造点时正确的研究数据集
- 定义和计算受约束因子
- 使用 LangGraph 组织简单量化 Workflow

定位：**量化研究入门 / 初级研究工程能力。**

## 完成 Level 1—5

能够：

- 独立完成单因子研究
- 使用截面回归和稳健标准误
- 执行样本外和多重检验
- 识别大部分基础虚假发现
- 构建有界研究 Agent

定位：**较扎实的初级量化研究员或研究工程师。**

## 完成 Level 1—7

能够：

- 将因子转化为真实成本约束组合
- 构建多因子 Alpha 模型
- 构建风险模型和组合优化
- 分析增量价值、风险和容量

定位：**成熟的 Quant Research Engineer 核心能力范围。**

## 完成 Level 1—9

能够：

- 使用机器学习开展严格的截面研究
- 构建多 Agent 独立研究和审查流程
- 设计盲化评审、Red-Team 和冲突裁决
- 使用 LangGraph 构建可恢复、可审批的因子研究系统

定位：**顶级系统化量化机构研究岗位的较强候选人能力画像。**

## 完成 Level 10

在全部项目真正独立完成、数值正确、未照抄且经过严格复盘的前提下，能够：

- 独立提出和检验专业因子假设
- 完成数据、统计、回测、风险和组合全链路
- 组织单 Agent 和多 Agent 进行受控研究
- 建立可复现、可审计的研究工作流
- 对因子做出接受、拒绝或继续观察的专业判断

这仍不等于自动成为 Two Sigma 等顶级机构的资深专家。真正的专家水平还需要：

- 多年持续研究
- 大量失败实验
- 真实市场和交易成本反馈
- 对未知数据的长期样本外表现
- 高水平团队的反复评审
- 对新问题提出原创方法的能力

更准确的目标是：

> **达到顶级量化研究岗位所需的核心知识结构和研究方法，具备竞争力强的项目、代码和研究作品。**

---

# 十二、最终能力清单

完成整条路线后，应能够独立回答并实现：

1. 如何从经济逻辑提出可证伪因子假设？
2. 如何保证财务和分析师数据在当时真实可得？
3. 如何构造点时正确的股票池和标签？
4. 如何选择去极值、标准化和中性化方法？
5. IC、分组收益和截面回归各自回答什么问题？
6. 如何使用稳健标准误处理时间依赖？
7. 如何避免参数挖掘和多重检验导致的虚假发现？
8. 如何设计真正隔离的样本外和最终 Holdout？
9. 如何判断因子在不同市场环境下是否稳定？
10. 如何将统计信号转换为成本后可交易组合？
11. 如何估计容量、借券和市场冲击？
12. 如何判断新因子是否与已有因子冗余？
13. 如何构建多因子 Alpha 模型？
14. 如何构建和验证风险模型？
15. 如何在风险、成本和换手率约束下优化组合？
16. 如何为机器学习设置正确的时间验证？
17. 如何发现特征泄漏和模型漂移？
18. 哪些步骤应是 Tool、Node、Subgraph 或 Agent？
19. 如何限制 Agent 的工具、上下文和研究预算？
20. 如何使用盲化 Reviewer 和 Red-Team 降低确认偏误？
21. 如何解决 Agent 之间的事实、统计和解释冲突？
22. 如何使用 Checkpoint、Interrupt 和 Resume 支持长研究任务？
23. 如何证明多 Agent 比单 Agent 有真实增量价值？
24. 如何记录每个结论的数据、代码、实验和证据来源？
25. 如何在证据不足时专业地拒绝一个因子？

---

# 结语

本路线的核心不是让 Agent 自动发现“神奇 Alpha”，而是建立一个严格的科学研究过程：

```text
可证伪假设
→ 点时正确的数据
→ 确定性计算
→ 严格统计验证
→ 样本外与多重检验
→ 成本、风险与容量
→ 独立审查和反方挑战
→ 人工最终判断
```

LangGraph 的价值，在于将这一过程变成显式、受约束、可恢复、可测试、可审计的研究系统。
