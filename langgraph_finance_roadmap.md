# 从 0 到 LangGraph 专家：金融项目实战路线

> 目标：以金融研究、量化分析、风险控制和生产级工程为主线，从 Python 与 LLM 基础逐步进阶到企业级 LangGraph 架构设计。

---

## 总体学习原则

每一级都完成以下五类任务：

1. 理解核心概念
2. 完成最小代码案例
3. 完成独立练习
4. 完成综合金融项目
5. 通过晋级考核

建议学习比例：

- 30%：官方文档与概念学习
- 50%：项目开发
- 20%：调试、测试、复盘与重构

每一级的项目建议保存在独立 Git 仓库或同一 Monorepo 中：

```text
README.md
pyproject.toml
.env.example
src/
tests/
data/
docs/
architecture.md
```

整条路线统一围绕一个主项目持续升级：

```text
V1：金融问答机器人
V2：增加金融计算工具
V3：增加问题分类与路由
V4：增加循环研究与质量检查
V5：增加研究档案与持续跟踪
V6：增加量化策略回测与人工审批
V7：升级为多智能体金融研究系统
V8：增加测试与自动评估
V9：部署为多用户金融研究服务
V10：升级为企业级金融智能分析平台
```

---

# Level 1：Python、LLM 与金融数据基础

## 项目名称

**金融数据查询助手**

## 学习目标

掌握学习 LangGraph 所需的 Python、API、金融数据处理和大模型基础。

## 核心知识

### Python

- 函数、类、模块和包
- `dict`、`list`、集合
- 类型提示
- `TypedDict`
- `dataclass`
- 异常处理
- JSON 序列化
- 环境变量
- 虚拟环境
- `async` / `await`
- 日志记录

### LLM

- System、User、Assistant Message
- Token 与上下文窗口
- Temperature
- Prompt Template
- Structured Output
- Tool Calling
- Embedding
- RAG
- Agent 与 Workflow 的区别

### 金融数据

- CSV、JSON 和 Pandas
- 收益率
- 累计收益率
- 移动平均线
- 波动率
- 最大回撤
- 基础财务指标

## 最小案例

1. 读取股票历史 CSV 数据
2. 计算每日收益率
3. 计算 20 日移动平均线
4. 调用模型总结财报文本
5. 保存命令行对话历史

## 综合项目

构建一个命令行金融信息助手：

```text
用户输入
  ↓
识别查询类型
  ↓
读取本地金融数据
  ↓
执行计算
  ↓
模型生成解释
  ↓
返回结果
```

支持的问题：

```text
计算某股票最近 20 个交易日的平均价格。
比较两只股票的历史波动率。
总结这份公司财报中的主要风险。
解释市盈率和市净率的区别。
```

## 晋级标准

能够独立完成：

- 调用任意大模型 API
- 处理结构化 JSON 输出
- 使用 Pandas 完成基础金融计算
- 编写异步函数
- 处理 API 超时和异常
- 解释 Tool Calling 的基本过程

---

# Level 2：LangChain 与金融工具调用

## 项目名称

**金融工具调用 Agent**

## 学习目标

理解 Agent 如何根据用户任务选择并调用不同的金融工具。

## 核心知识

- Chat Model
- Messages
- Prompt Template
- Runnable
- Tools
- Tool Calling
- Structured Output
- ReAct Agent
- Agent Loop
- 工具参数验证
- 工具错误处理

## 工具列表

- 股票历史价格查询
- 收益率计算
- 波动率计算
- 最大回撤计算
- 复利计算器
- 贷款还款计算器
- 汇率换算
- 财报文本检索
- 财务指标提取

## Agent Loop

```text
用户提出金融问题
  ↓
模型判断是否需要工具
  ├─ 不需要 → 直接解释
  └─ 需要 → 选择工具
               ↓
          执行金融计算
               ↓
          返回工具结果
               ↓
          模型生成答案
```

## 综合项目

构建一个“个人金融计算助理”，支持：

```text
如果本金为 10 万元，年化收益率为 5%，10 年后是多少？
比较两只股票过去一年的收益和波动。
计算一笔贷款的每月还款额。
从财报中提取公司的主要收入来源。
```

## 晋级标准

能够解释：

- Tool Calling 和普通函数调用的区别
- Agent 为什么可能无限循环
- 什么任务适合确定性 Workflow
- 什么任务适合 Agent
- 为什么不能让 Agent 无限制调用工具
- 如何验证模型生成的工具参数

---

# Level 3：LangGraph 核心基础

## 项目名称

**金融问题分类与路由系统**

## 学习目标

掌握 LangGraph 最重要的三个对象：

- State
- Node
- Edge

## 核心知识

- `StateGraph`
- `TypedDict`
- State Schema
- Node
- Normal Edge
- Conditional Edge
- `START`
- `END`
- `compile()`
- `invoke()`
- `stream()`

## State 示例

```python
from typing import TypedDict


class FinanceState(TypedDict):
    user_query: str
    intent: str
    symbol: str | None
    retrieved_data: dict
    calculation_result: dict
    final_answer: str
```

## 工作流程

```text
用户问题
  ↓
金融意图分类
  ├─ 股票分析 → 股票分析节点
  ├─ 财报分析 → 财报节点
  ├─ 贷款计算 → 贷款节点
  ├─ 宏观问题 → 宏观解释节点
  └─ 金融教育 → 概念教学节点
                   ↓
                  END
```

## 最小案例

1. 线性工作流：输入 → 计算 → 输出
2. 条件路由：根据问题类型选择节点
3. 错误路由：无法识别时进入兜底节点
4. 流式输出：逐步展示执行结果

## 综合项目

构建一个“金融客户咨询路由系统”。

系统必须处理：

- 股票代码查询
- 贷款计算
- 财务指标解释
- 公司财报分析
- 宏观金融问题
- 无法识别的问题

## 晋级标准

不查教程独立实现：

- 至少 4 个节点
- 至少 1 条条件路由
- 完整 State Schema
- 兜底节点
- Graph 编译与执行
- 流式输出

---

# Level 4：状态、循环与金融研究 Agent

## 项目名称

**上市公司基本面研究助手**

## 学习目标

从简单路由图进阶到具有循环、检查和终止条件的有状态研究流程。

## 核心知识

- State 更新
- Reducer
- Message State
- `add_messages`
- Conditional Routing
- Loop
- Recursion Limit
- Tool Node
- Command
- 节点重试
- 错误回退
- Token 与调用预算

## 工作流程

```text
接收研究问题
  ↓
制定研究计划
  ↓
检索金融数据
  ↓
计算关键指标
  ↓
检查证据是否充分
  ├─ 否 → 继续检索或计算
  └─ 是 → 生成研究报告
             ↓
         风险与质量检查
             ↓
            END
```

## 示例任务

```text
分析一家公司的收入增长趋势。
比较两家同行公司的盈利能力。
检查某公司现金流是否存在明显风险。
分析某资产的历史收益和最大回撤。
```

## 必须输出

- 分析结论
- 数据依据
- 使用的计算方法
- 数据时间范围
- 风险因素
- 数据缺失说明
- 不确定性说明
- 非投资建议声明

## 综合项目

构建一个“上市公司基本面研究助手”。

系统需要包含：

- 研究计划节点
- 数据检索节点
- 财务计算节点
- 证据完整性检查节点
- 报告生成节点
- 风险检查节点
- 最大循环次数
- 工具失败重试
- 无结果回退路径

## 晋级标准

能够处理：

- Agent 无限循环
- State 被错误覆盖
- Reducer 配置错误
- 工具调用失败
- 模型输出无法解析
- 数据不足时提前终止
- 达到预算时安全结束

---

# Level 5：持久化与金融研究档案

## 项目名称

**金融研究档案与持续跟踪助手**

## 学习目标

掌握 LangGraph 的持久化、线程恢复和长期记忆机制，让金融研究可以跨会话持续进行。

## 核心知识

- Checkpointer
- `thread_id`
- State History
- Store
- Namespace
- 短期状态
- 长期研究档案
- 跨会话检索
- 记忆更新
- 记忆冲突
- 数据版本管理
- 多用户隔离

## 工作流程

```text
用户提交研究任务
  ↓
识别公司、行业和研究主题
  ↓
读取当前研究线程
  ↓
检索该公司的历史研究档案
  ↓
判断是新研究还是继续研究
  ├─ 新研究 → 创建研究档案
  └─ 继续研究 → 恢复历史状态
                    ↓
              获取或分析新数据
                    ↓
              对比历史研究结论
                    ↓
              更新公司研究档案
                    ↓
                  输出结果
```

## State 示例

```python
from typing import TypedDict


class ResearchState(TypedDict):
    user_query: str
    company_id: str
    research_topic: str
    current_findings: list[str]
    unresolved_questions: list[str]
    identified_risks: list[str]
    data_sources: list[dict]
    previous_summary: str | None
    final_report: str
```

## Checkpoint 保存内容

- 当前执行节点
- 已完成的分析步骤
- 当前工具调用结果
- 中间结论
- 未完成任务
- 节点错误信息
- 当前研究报告草稿

Checkpoint 主要解决：

```text
研究执行到一半
  ↓
程序中断
  ↓
使用相同 thread_id
  ↓
恢复任务
  ↓
继续后续分析
```

## Store 保存内容

- 公司基本档案
- 长期关注指标
- 历史风险
- 待验证问题
- 历史研究报告
- 数据来源记录
- 研究结论变化
- 用户偏好的报告格式

推荐 Namespace：

```python
namespace = (
    "financial_research",
    user_id,
    company_id,
)
```

也可以进一步分类：

```text
financial_research/{user_id}/{company_id}/profile
financial_research/{user_id}/{company_id}/risks
financial_research/{user_id}/{company_id}/questions
financial_research/{user_id}/{company_id}/reports
```

## 记忆冲突示例

历史记录：

```text
公司收入主要来自硬件业务。
```

最新财报：

```text
软件服务已经成为最大收入来源。
```

正确的更新方式：

```text
历史状态：
硬件业务为主要收入来源。

最新状态：
软件服务成为最大收入来源。

变化时间：
2026 年第二季度。

结论：
公司的收入结构发生明显变化。
```

不应简单覆盖旧记录，而应保留变化过程和数据时间。

## 综合项目

构建一个“上市公司研究档案助手”，支持：

- 创建公司研究档案
- 恢复中断任务
- 保存历史分析报告
- 保存风险清单
- 保存待验证问题
- 比较当前与历史结论
- 标记过期数据
- 修正或删除错误记忆
- 区分事实、观点和模型推测
- 多用户数据隔离

## 晋级标准

能够清楚回答：

1. 哪些内容放 State
2. 哪些内容由 Checkpoint 保存
3. 哪些内容进入 Store
4. 如何恢复未完成任务
5. 如何处理过期研究结论
6. 如何解决前后冲突的记录
7. 如何删除错误长期记忆
8. 如何隔离不同用户数据
9. 如何限制长期档案无限增长
10. 如何记录数据来源和版本

---

# Level 6：人工介入与量化策略审批

## 项目名称

**量化策略回测审批系统**

## 学习目标

掌握 Interrupt、Resume、Human-in-the-loop 和 Durable Execution，构建可以暂停、审批、修改和恢复的量化研究流程。

> 本项目只进行历史回测和模拟运行，不连接真实交易账户。

## 核心知识

- Interrupt
- Resume
- Human-in-the-loop
- Durable Execution
- State 修改
- 审批分支
- 幂等性
- 副作用隔离
- 策略版本管理
- 数据版本管理
- 操作审计
- 崩溃恢复

## 工作流程

```text
提交策略需求
  ↓
生成策略定义
  ↓
验证策略参数
  ↓
加载历史数据
  ↓
运行回测
  ↓
计算绩效指标
  ↓
执行风险检查
  ↓
执行回测质量检查
  ↓
生成策略报告
  ↓
暂停等待人工审批
  ├─ 批准 → 进入模拟运行
  ├─ 修改 → 调整参数并重新回测
  ├─ 补充测试 → 返回测试节点
  └─ 拒绝 → 归档并结束
```

## State 示例

```python
from typing import TypedDict


class StrategyState(TypedDict):
    strategy_name: str
    strategy_description: str
    universe: list[str]
    parameters: dict
    backtest_period: dict
    backtest_results: dict
    risk_findings: list[str]
    validation_findings: list[str]
    approval_status: str
    reviewer_comments: str | None
    strategy_version: int
    final_report: str
```

## 策略示例

```json
{
  "strategy_name": "双均线趋势策略",
  "universe": ["SPY"],
  "parameters": {
    "short_window": 20,
    "long_window": 60
  },
  "entry_rule": "短期均线上穿长期均线",
  "exit_rule": "短期均线下穿长期均线",
  "transaction_cost": 0.001,
  "position_limit": 1.0
}
```

## 回测指标

- 累计收益率
- 年化收益率
- 年化波动率
- Sharpe Ratio
- Sortino Ratio
- 最大回撤
- 最大回撤持续时间
- 胜率
- 盈亏比
- 换手率
- 交易次数
- 交易成本
- 基准收益
- 超额收益

## 风险检查

```text
是否存在未来数据泄漏？
是否使用了当时不可获得的数据？
是否忽略交易成本？
是否存在幸存者偏差？
样本时间是否过短？
参数是否过度拟合？
最大回撤是否超过限制？
交易次数是否过少？
收益是否依赖少数交易？
是否只在单一市场环境中有效？
```

## 回测质量检查

```text
是否包含训练期和验证期？
是否进行了样本外测试？
是否与基准比较？
是否测试参数敏感性？
是否覆盖不同市场阶段？
是否记录数据版本？
是否能重复得到相同结果？
```

## 人工审批选项

### 批准

```text
审批结果：批准
下一阶段：进入模拟运行
```

### 修改参数

```text
审批结果：修改后重新提交

修改内容：
- 短期均线从 20 调整为 15
- 长期均线从 60 调整为 90
- 增加最大仓位限制
```

### 补充测试

```text
审批结果：需要补充测试

要求：
- 增加金融危机阶段
- 增加高利率阶段
- 测试双倍交易成本
```

### 拒绝

```text
审批结果：拒绝

原因：
- 样本外表现明显下降
- 参数敏感性过高
- 最大回撤超过限制
```

## 幂等性设计

同一回测任务应使用唯一标识：

```python
backtest_job_id = (
    strategy_id,
    strategy_version,
    dataset_version,
)
```

执行前检查任务是否已经完成，避免：

- 重复运行大型回测
- 重复保存结果
- 重复创建模拟策略
- 重复发送审批通知

## 副作用隔离

审批之前只允许：

- 生成策略代码
- 读取历史数据
- 执行回测
- 生成研究报告
- 保存草稿结果

审批之后才允许：

- 创建模拟交易任务
- 写入正式策略库
- 发布研究报告
- 发送正式审批结果
- 更新策略状态

## 综合项目

构建一个“量化策略研究与审批平台”，支持：

- 自然语言策略需求
- 结构化策略定义
- 历史回测
- 绩效指标计算
- 风险检查
- 数据质量检查
- 人工暂停审批
- 修改参数后恢复
- 策略版本管理
- 操作审计
- 崩溃后恢复
- 模拟运行状态创建

## 晋级标准

系统必须保证：

1. 未批准时不能进入模拟运行
2. 不同策略版本结果不能混淆
3. 重试不会重复产生副作用
4. 程序重启后可以恢复审批状态
5. 审核人员可以修改参数并重新执行
6. 每次审批都有完整记录
7. 数据版本可以追踪
8. 报告必须包含限制和风险
9. 不把历史收益描述为未来收益保证
10. 不连接真实交易账户

---

# Level 7：高级 Graph 与多智能体金融研究

## 项目名称

**多智能体公司研究平台**

## 学习目标

掌握 Subgraph、并行执行、Supervisor 和多 Agent 协作模式。

## 核心知识

- Subgraph
- Parallel Execution
- Fan-out / Fan-in
- Map-Reduce
- Supervisor
- Handoff
- Router
- Agent as Tool
- Graph Composition
- 共享状态
- 私有状态
- 并发限制

## Agent 分工

```text
Supervisor
├─ 数据研究员
├─ 财报分析员
├─ 行业分析员
├─ 风险分析员
├─ 估值分析员
├─ 证据审查员
└─ 报告撰写员
```

## 工作流程

```text
研究任务
  ↓
Supervisor 拆分任务
  ↓
多个分析 Agent 并行执行
  ↓
证据审查
  ↓
合并研究结果
  ↓
风险审查
  ↓
生成最终报告
```

## 最终报告内容

- 公司概况
- 收入与利润趋势
- 资产负债情况
- 现金流分析
- 行业比较
- 历史估值指标
- 主要风险
- 数据来源
- 数据日期
- 不确定性说明

## 综合项目

构建一个“多智能体公司研究平台”。

要求：

- Supervisor 动态分配任务
- 至少 4 个专业 Agent
- 至少 2 个并行节点
- 证据核验
- 报告合并
- 风险审查
- 最大迭代次数
- 总成本限制
- 重复任务检测

## 晋级标准

能够解释：

- 为什么不能为每个步骤都创建 Agent
- Supervisor 何时成为瓶颈
- 多 Agent 比单 Agent 增加了哪些成本
- 如何防止 Agent 重复工作
- 如何管理共享状态和私有状态
- 如何控制并行任务数量
- 如何处理不同 Agent 的冲突结论

---

# Level 8：测试、可观测性与金融评估

## 项目名称

**金融 Agent 自动评测平台**

## 学习目标

从“看起来能运行”提升到“能够证明系统有效”。

## 核心知识

- Unit Test
- Node Test
- Graph Integration Test
- Mock LLM
- Mock Tool
- Trace
- Dataset
- Offline Evaluation
- Online Evaluation
- Human Evaluation
- LLM-as-Judge
- Regression Test
- 成本与延迟监控

## 测试数据集

准备至少 50 个问题：

- 金融概念解释
- 收益率计算
- 贷款计算
- 财务指标提取
- 财报风险识别
- 股票对比
- 数据不足问题
- 错误股票代码
- 工具调用失败
- 诱导性投资问题
- 过期数据问题
- 引用不支持结论的问题

## 评估指标

```text
计算正确率
数据提取准确率
路由准确率
工具选择准确率
引用完整率
事实一致性
幻觉率
风险提示完整率
平均执行步骤
平均响应时间
平均 Token 成本
人工介入率
失败恢复率
任务完成率
```

## 综合项目

为 Level 7 的多智能体金融研究系统建立自动评估平台。

要求：

- 至少 50 条测试数据
- 标准答案或评分 Rubric
- 自动运行测试
- 对比不同模型
- 对比不同 Prompt
- 对比不同 Graph 设计
- 记录成本和延迟
- 自动生成评估报告
- 支持回归测试

## 评估报告示例

```text
财务指标计算正确率：96%
问题路由准确率：91%
引用完整率：87%
幻觉率：4%
平均响应时间：8.2 秒
单次任务平均成本：0.12 元
主要失败类型：财报表格字段识别错误
```

## 晋级标准

不再使用：

```text
我测试了几个问题，感觉效果不错。
```

而是提供：

- 明确数据集
- 明确评分标准
- 修改前后指标
- 成本变化
- 延迟变化
- 失败类型分析
- 回归测试结果

---

# Level 9：生产级金融研究服务

## 项目名称

**多用户金融研究 SaaS**

## 学习目标

将 LangGraph 项目部署为可维护、可恢复、可扩展的多用户服务。

## 核心知识

### 服务层

- FastAPI
- REST API
- SSE
- WebSocket
- Background Job
- Queue
- Worker
- Rate Limit
- Authentication
- Authorization

### 数据层

- PostgreSQL
- Redis
- Checkpoint Database
- Store Database
- 向量数据库
- 数据迁移
- TTL
- 备份和恢复
- 多租户隔离

### 可靠性

- Timeout
- Retry
- Circuit Breaker
- Idempotency
- Dead Letter Queue
- Cancellation
- Concurrency Control
- Resource Limit
- Graceful Shutdown

### 安全性

- Prompt Injection
- Tool Permission
- Secrets Management
- PII 保护
- 输出过滤
- 工具参数验证
- Tenant Isolation
- 审计日志

## 系统架构

```text
Web 前端
   ↓
API Gateway
   ↓
身份验证与权限控制
   ↓
LangGraph 服务
   ↓
任务队列与 Worker
   ↓
金融数据服务
   ↓
PostgreSQL / Redis / Vector Database
   ↓
Tracing / Evaluation / Monitoring
```

## 核心功能

- 用户登录
- 自选研究列表
- 多会话金融研究
- 流式报告生成
- 长任务后台执行
- 任务暂停和取消
- 历史报告查询
- 数据来源记录
- 成本限制
- 多租户隔离
- 权限审计
- 崩溃恢复

## 综合项目

构建一个“多用户金融研究 SaaS”。

要求：

- Docker 部署
- CI/CD
- 多用户认证
- 用户数据隔离
- 流式响应
- 后台任务
- 任务取消
- Checkpoint 持久化
- Store 持久化
- 监控和告警
- 负载测试
- 审计日志

## 晋级标准

能够回答：

- 同一请求重复发送怎么办
- Worker 执行一半宕机怎么办
- 模型服务超时怎么办
- 用户关闭页面后任务是否继续
- 同时有 1,000 个任务怎么办
- 如何限制单用户资源消耗
- 如何回滚有问题的 Prompt
- 如何追踪某次错误调用
- 如何避免用户数据交叉
- 如何安全取消长任务

---

# Level 10：LangGraph 专家与企业级金融架构

## 项目名称

**企业金融研究与风险决策平台**

## 学习目标

从 LangGraph 使用者进阶为能够设计、评估和治理复杂金融 Agent 系统的架构师。

## 深入框架原理

研究：

- Graph 编译过程
- Pregel 风格执行模型
- Super-step
- Channel
- Reducer
- Checkpoint 生命周期
- 并发状态更新
- Streaming Event
- Subgraph 状态传播
- 序列化
- Task Scheduling
- Retry 与恢复语义

## 架构判断能力

能够在以下方案中做出选择：

```text
普通 Python Workflow
vs
LangChain Agent
vs
LangGraph
vs
自定义状态机
vs
消息队列工作流系统
```

专家能力不仅是“会使用 LangGraph”，还包括知道：

- 什么时候应该使用 LangGraph
- 什么时候普通 Python 更合适
- 什么时候应该使用确定性工作流
- 什么时候适合多 Agent
- 什么时候应减少 LLM 决策
- 什么时候必须人工审批

## 数据接入模块

- 股票历史数据
- 公司财报
- 企业内部研究文档
- 行业报告
- 宏观经济数据
- 新闻和公告
- 用户上传文件

## 企业级研究工作流

```text
提出研究问题
  ↓
任务分类
  ↓
生成研究计划
  ↓
并行数据收集
  ↓
指标计算
  ↓
事实和证据检查
  ↓
风险分析
  ↓
人工审核
  ↓
生成正式研究报告
```

## Agent 团队

- 研究规划 Agent
- 数据分析 Agent
- 财报分析 Agent
- 风险识别 Agent
- 行业比较 Agent
- 证据核验 Agent
- 合规检查 Agent
- 报告写作 Agent
- Supervisor Agent

## 平台能力

- 多租户
- 权限管理
- 人工审批
- 长短期记忆
- 任务恢复
- 成本预算
- 模型路由
- 数据版本管理
- 在线评估
- 审计日志
- Prompt 版本管理
- 执行轨迹可视化
- 策略与报告版本管理
- 安全工具权限

## 最终毕业项目

构建一个“企业金融研究与风险决策平台”。

必须提交：

```text
系统架构图
Graph 流程图
State Schema
节点设计文档
数据库设计
金融数据字典
权限与安全设计
风险控制设计
评估数据集
评估报告
成本报告
压力测试报告
故障恢复方案
部署文档
技术决策记录 ADR
```

## 开源与研究要求

至少完成两项：

- 阅读 LangGraph 核心源码
- 修复一个 Issue
- 提交 Pull Request
- 编写可复用金融节点库
- 创建 Checkpointer 或 Store 集成
- 发布完整金融案例
- 编写中文系列教程
- 对多 Agent 架构进行基准测试
- 构建自己的 Agent Runtime 原型

## 专家级考核

能够解释：

1. 哪些金融流程必须使用确定性节点
2. 哪些任务可以交给 LLM 判断
3. 为什么交易和付款不能完全由 Agent 自主执行
4. 如何避免模型引用过期金融数据
5. 如何处理不同数据源之间的冲突
6. 如何验证财务计算结果
7. 如何追踪报告中每个结论的依据
8. 如何隔离不同客户的数据和记忆
9. 如何评估金融 Agent 的幻觉风险
10. 什么情况下不应该使用 LangGraph
11. 如何定位状态、并发和持久化问题
12. 如何将开发原型升级为生产系统

---

# 10 级项目总览

| 等级 | 技术定位 | 金融项目 |
|---|---|---|
| 1 | Python 与 LLM 入门 | 金融数据查询助手 |
| 2 | Tool Calling 入门 | 金融工具调用 Agent |
| 3 | LangGraph 核心基础 | 金融问题分类与路由系统 |
| 4 | 状态、循环与研究流程 | 上市公司基本面研究助手 |
| 5 | 持久化与长期研究记忆 | 金融研究档案与持续跟踪助手 |
| 6 | 人工介入与可靠执行 | 量化策略回测审批系统 |
| 7 | 多智能体与高级 Graph | 多智能体公司研究平台 |
| 8 | 测试、追踪与评估 | 金融 Agent 自动评测平台 |
| 9 | 生产部署与系统工程 | 多用户金融研究 SaaS |
| 10 | 专家与企业架构 | 企业金融研究与风险决策平台 |

---

# 每一级的建议案例数量

| 内容 | 每级建议数量 |
|---|---:|
| 最小代码案例 | 3—5 个 |
| 独立练习 | 2—3 个 |
| 综合金融项目 | 1 个 |
| 错误排查案例 | 2 个 |
| 晋级测试 | 1 套 |

完成全部路线后，预计积累：

- 30—50 个金融代码案例
- 20—30 个独立练习
- 10 个阶段项目
- 20 个调试案例
- 10 套晋级测试
- 1 个企业级毕业项目

---

# 推荐学习顺序

```text
Level 1：Python + LLM + 金融数据
          ↓
Level 2：LangChain + Tool Calling
          ↓
Level 3：State / Node / Edge
          ↓
Level 4：路由 / 循环 / Research Agent
          ↓
Level 5：Checkpoint / Store / 研究档案
          ↓
Level 6：Interrupt / Resume / 策略审批
          ↓
Level 7：Subgraph / Parallel / Multi-Agent
          ↓
Level 8：Tracing / Testing / Evaluation
          ↓
Level 9：Deployment / Reliability / Security
          ↓
Level 10：源码 / 架构 / 开源贡献
```

---

# 最重要的避坑原则

- 不要一开始就学习多 Agent
- 不要把每个函数都设计成 Node
- 不要把所有业务判断交给 LLM
- 不要用自然语言代替明确的状态字段
- 不要创建没有终止条件的循环
- 不要把 Checkpoint 当作长期业务数据库
- 不要把所有聊天内容都写入长期记忆
- 不要覆盖旧金融结论而不保留版本
- 不要忽略金融数据的时间和来源
- 不要在回测中使用未来数据
- 不要忽略交易成本和滑点
- 不要在工具函数中执行不可控副作用
- 不要未经人工审批进入高风险流程
- 不要只测试最终答案，还要测试节点和路由
- 不要没有评估数据就不断修改 Prompt
- 不要为了使用 LangGraph 而使用 LangGraph

---

# 金融项目安全边界

学习项目推荐聚焦：

- 金融教育
- 历史数据分析
- 财务指标计算
- 财报分析
- 公司研究
- 风险识别
- 信息检索
- 报告生成
- 历史回测
- 模拟交易
- 人工审批流程

暂不让系统自主执行：

- 真实证券交易
- 自动付款
- 自动放贷
- 自动调整客户资产
- 无人工审批的高风险金融决策
- 使用未经验证的数据生成确定性投资结论
- 将历史收益描述为未来收益保证

---

# 最终能力目标

完成 10 个等级后，应具备以下能力：

1. 独立设计 LangGraph State、Node 和 Edge
2. 构建带路由、循环和终止条件的金融 Agent
3. 使用 Checkpoint 恢复长时间任务
4. 使用 Store 管理结构化研究档案
5. 构建人工审批和可恢复工作流
6. 设计多智能体金融研究系统
7. 建立金融 Agent 自动评估体系
8. 部署多用户生产级 LangGraph 服务
9. 处理数据版本、权限、审计和风险控制
10. 判断何时应该或不应该使用 LangGraph
11. 阅读源码并定位框架级问题
12. 设计企业级金融智能分析平台
