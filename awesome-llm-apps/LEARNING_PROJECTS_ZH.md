# 项目中文学习手册

本手册覆盖金融优先学习路线中的 21 个项目。仓库暂未为这些项目提供完整的项目级中文简介，以下内容根据各项目的 README、源码结构和依赖文件整理生成。难度按本仓库内的相对复杂度评定。

> 金融、投资和保险项目仅用于技术学习与原型验证，不构成投资、保险或法律建议。涉及外部 API、网页操作和消息投递时，应使用测试账户、最小权限和人工确认。

## 一、金融 Agent 主线

### 1. xAI 金融分析 Agent

- **路径**：[`starter_ai_agents/xai_finance_agent/`](starter_ai_agents/xai_finance_agent/)
- **中文简介**：使用 Grok、Yahoo Finance 和 DuckDuckGo 查询股票行情、公司信息与相关新闻，并通过 AgentOS Playground 展示结构化金融分析结果。
- **核心技术**：Agno、AgentOS、YFinance、DuckDuckGo、工具调用。
- **学习重点**：最小 Agent 结构、模型与工具绑定、实时数据和自然语言结论的边界。
- **难度/前置条件**：入门；Python 基础、xAI API Key。
- **建议产出**：增加数据时间戳、来源和风险声明的单股票分析页。

### 2. AI 投资分析 Agent

- **路径**：[`advanced_ai_agents/single_agent_apps/ai_investment_agent/`](advanced_ai_agents/single_agent_apps/ai_investment_agent/)
- **中文简介**：基于 Yahoo Finance 获取公司资料、行情、新闻和分析师建议，生成两只或多只股票的比较报告。
- **核心技术**：Agno、AgentOS、OpenAI、YFinance。
- **学习重点**：金融工具封装、比较型 Prompt、表格输出和报告结构。
- **难度/前置条件**：入门；Python、LLM API Key。
- **建议产出**：三家公司基本面比较工具，并为缺失字段提供明确标记。

### 3. AI 个人财务规划师

- **路径**：[`advanced_ai_agents/single_agent_apps/ai_personal_finance_agent/`](advanced_ai_agents/single_agent_apps/ai_personal_finance_agent/)
- **中文简介**：收集用户的收入、支出、目标与财务状况，由研究和规划 Agent 生成个性化预算、储蓄及投资建议。
- **核心技术**：Agno、Streamlit、OpenAI、SerpAPI、双 Agent 流程。
- **学习重点**：表单输入、会话状态、Researcher 到 Planner 的上下文传递。
- **难度/前置条件**：初中级；Python、Streamlit、OpenAI 与 SerpAPI Key。
- **建议产出**：可解释的月度预算方案，计算逻辑使用普通 Python 实现。

### 4. AI 金融 Agent 团队

- **路径**：[`advanced_ai_agents/multi_agent_apps/agent_teams/ai_finance_agent_team/`](advanced_ai_agents/multi_agent_apps/agent_teams/ai_finance_agent_team/)
- **中文简介**：由网页研究 Agent、金融数据 Agent 和协调 Team 共同完成公司研究与金融分析，并用 SQLite 保存交互记录。
- **核心技术**：Agno Team、YFinance、DuckDuckGo、SQLite、AgentOS。
- **学习重点**：多 Agent 分工、任务委派、工具隔离和结果汇总。
- **难度/前置条件**：中级；理解单 Agent 和工具调用。
- **建议产出**：加入独立风险审查 Agent，检查来源、时效和结论冲突。

### 5. 人寿保险保额顾问

- **路径**：[`starter_ai_agents/ai_life_insurance_advisor_agent/`](starter_ai_agents/ai_life_insurance_advisor_agent/)
- **中文简介**：根据收入、负债、家庭责任和已有保障估算定期寿险需求，并检索用户所在地区的相关产品信息。
- **核心技术**：Agno、Streamlit、Firecrawl、E2B Code Interpreter、OpenAI。
- **学习重点**：确定性财务计算、沙箱执行、实时网页研究和安全声明。
- **难度/前置条件**：中级；需要 OpenAI、Firecrawl、E2B Key。
- **建议产出**：为保额计算、百分比解析和异常输入补充单元测试。

### 6. Google ADK 多 Agent 财务教练

- **路径**：[`advanced_ai_agents/multi_agent_apps/ai_financial_coach_agent/`](advanced_ai_agents/multi_agent_apps/ai_financial_coach_agent/)
- **中文简介**：分析手工输入或 CSV 交易数据，通过预算、储蓄和债务三个 Agent 依次生成个人财务改善方案及可视化图表。
- **核心技术**：Google ADK、SequentialAgent、Pydantic、Pandas、Streamlit、Plotly。
- **学习重点**：结构化输出、顺序工作流、CSV 校验、债务雪球与雪崩法。
- **难度/前置条件**：中高级；Python 数据处理、Gemini API Key。
- **建议产出**：带预算、应急金和债务时间线的结构化财务报告。

### 7. AI VC 尽职调查团队

- **路径**：[`advanced_ai_agents/multi_agent_apps/agent_teams/ai_vc_due_diligence_agent_team/`](advanced_ai_agents/multi_agent_apps/agent_teams/ai_vc_due_diligence_agent_team/)
- **中文简介**：对初创公司依次执行公司研究、市场分析、财务建模、风险评估和投资备忘录生成，并输出 HTML 报告与信息图。
- **核心技术**：Google ADK、Gemini、SequentialAgent、Google Search、代码执行、Matplotlib。
- **学习重点**：长流水线编排、共享状态、情景预测、风险矩阵和专业报告生成。
- **难度/前置条件**：高级；多 Agent 基础、Gemini API Key。
- **建议产出**：为一家公开公司生成可追溯的投资备忘录，并逐条核验事实来源。

### 8. 财报电话会分析 Agent

- **路径**：[`advanced_ai_agents/single_agent_apps/earnings_call_analyst_agent/`](advanced_ai_agents/single_agent_apps/earnings_call_analyst_agent/)
- **中文简介**：将 YouTube 财报电话会转换为与视频时间轴同步的分析工作区，结合字幕、SEC 文件和市场新闻识别关键财务信号。
- **核心技术**：Google ADK、FastAPI、Pydantic、YouTube Transcript、yt-dlp、SEC 数据、pytest。
- **学习重点**：多源数据管道、引用与时间戳对齐、长文本分析、失败回退和契约测试。
- **难度/前置条件**：高级；FastAPI、异步任务、Gemini 或 Vertex AI 配置。
- **建议产出**：带精确引文、播放时间和研究来源的财报事件卡片。

## 二、RAG 学习主线

### 9. DeepSeek 本地 RAG 推理 Agent

- **路径**：[`rag_tutorials/deepseek_local_rag_agent/`](rag_tutorials/deepseek_local_rag_agent/)
- **中文简介**：通过 Ollama 本地运行 DeepSeek，使用 Snowflake Embedding 和 Qdrant 检索 PDF 或网页内容，并可在检索不足时补充网络搜索。
- **核心技术**：Ollama、Agno、Qdrant、LangChain Qdrant、Streamlit。
- **学习重点**：文档切分、向量化、相似度检索、上下文注入和来源展示。
- **难度/前置条件**：中级；Ollama、本地模型和 Qdrant 环境。
- **建议产出**：本地年报问答系统，记录命中文档块和相似度。

### 10. RAG 故障诊断诊所

- **路径**：[`rag_tutorials/rag_failure_diagnostics_clinic/`](rag_tutorials/rag_failure_diagnostics_clinic/)
- **中文简介**：输入真实 RAG 故障描述，由模型将问题归类到 12 种常见失效模式，并输出最小结构修复建议和 JSON 诊断报告。
- **核心技术**：OpenAI-compatible API、故障模式库、CLI、JSON 报告。
- **学习重点**：召回失败、切分错误、上下文污染、错误引用和系统化调试。
- **难度/前置条件**：初中级；Python 和任意兼容的聊天模型 API。
- **建议产出**：为自己的年报 RAG 建立故障案例库和回归测试集。

### 11. PydanticAI 类型化 Agentic RAG

- **路径**：[`rag_tutorials/agentic_typed_rag_pydanticai/`](rag_tutorials/agentic_typed_rag_pydanticai/)
- **中文简介**：从 PDF 或文档网站检索内容，将回答验证为带原文引句、块编号、置信度和是否可回答标志的类型化对象；证据不足时在调用模型前拒答。
- **核心技术**：PydanticAI、Streamlit、结构化输出、本地哈希或 OpenAI Embedding、pytest。
- **学习重点**：类型约束、引用契约、检索门槛、拒答机制和离线测试。
- **难度/前置条件**：中级；Pydantic、基础 RAG。
- **建议产出**：定义 `FinancialAnswer` 模型并评测引用正确率与拒答准确率。

### 12. 混合检索 RAG

- **路径**：[`rag_tutorials/hybrid_search_rag/`](rag_tutorials/hybrid_search_rag/)
- **中文简介**：组合向量语义检索、关键词检索和重排序，提高长文档问答的召回质量，并支持多种向量数据库后端。
- **核心技术**：LangChain、向量数据库、OpenAI Embedding、Cohere Rerank、Anthropic。
- **学习重点**：Hybrid Search、候选合并、reranking、召回率与精确率权衡。
- **难度/前置条件**：高级；RAG 基础及多个外部服务配置。
- **建议产出**：在同一财报数据集上比较纯向量检索和混合检索。

### 13. 带可验证引用的知识图谱 RAG

- **路径**：[`rag_tutorials/knowledge_graph_rag_citations/`](rag_tutorials/knowledge_graph_rag_citations/)
- **中文简介**：从文档抽取实体和关系写入 Neo4j，通过多跳图遍历回答跨文档问题，并为推理链中的每个结论保留来源。
- **核心技术**：Neo4j、Ollama、知识图谱、Streamlit、引用追踪。
- **学习重点**：实体关系建模、多跳查询、图检索与向量检索的差异、数据溯源。
- **难度/前置条件**：高级；Docker、Neo4j、RAG 基础。
- **建议产出**：构建“公司—子公司—供应商—风险事件”关系图谱。

## 三、MCP 学习主线

### 14. 浏览器 MCP Agent

- **路径**：[`mcp_ai_agents/browser_mcp_agent/`](mcp_ai_agents/browser_mcp_agent/)
- **中文简介**：通过 MCP-Agent 连接 Playwright MCP Server，让用户用自然语言完成网页导航、点击、表单操作、截图和信息提取。
- **核心技术**：MCP、MCP-Agent、Playwright、Streamlit、OpenAI-compatible 模型。
- **学习重点**：MCP Client/Server/Tool 分工、stdio 连接、多步工具调用和浏览器安全边界。
- **难度/前置条件**：中级；Python、Node.js、浏览器自动化基础。
- **建议产出**：只读访问公司投资者关系页面并提取财报链接的 Agent。

### 15. Multi-MCP Agent Router

- **路径**：[`mcp_ai_agents/multi_mcp_agent_router/`](mcp_ai_agents/multi_mcp_agent_router/)
- **中文简介**：根据用户意图将任务路由给代码审查、安全、研究或 BIM 专职 Agent，每个 Agent 只连接与职责相关的 MCP Server。
- **核心技术**：Anthropic SDK、MCP Python SDK、Streamlit、工具路由、多 Agent。
- **学习重点**：意图分类、工具格式转换、最小权限、自动与手动路由。
- **难度/前置条件**：中高级；MCP 基础、Anthropic-compatible API。
- **建议产出**：改造成“公司研究、财报检索、风险审查”三个金融专职 Agent。

### 16. Multi-MCP 智能助手

- **路径**：[`mcp_ai_agents/multi_mcp_agent/`](mcp_ai_agents/multi_mcp_agent/)
- **中文简介**：把 GitHub、Perplexity、Calendar 和 Gmail 等多个 MCP Server 接入一个 Agno 助手，实现跨服务研究、日程和沟通自动化。
- **核心技术**：Agno、MCP、异步执行、会话记忆、Node.js MCP Server。
- **学习重点**：多 Server 生命周期、工具链组合、跨服务上下文和凭据管理。
- **难度/前置条件**：高级；多个第三方服务 Key 和 OAuth 配置。
- **建议产出**：将研究结果生成待审阅摘要，而不是直接发送邮件或创建日程。

### 17. GitHub MCP Agent

- **路径**：[`mcp_ai_agents/github_mcp_agent/`](mcp_ai_agents/github_mcp_agent/)
- **中文简介**：连接官方 GitHub MCP Server，以自然语言查询仓库、Issue、Pull Request、活动和代码统计信息。
- **核心技术**：Agno、MCP、Docker、GitHub MCP Server、Streamlit。
- **学习重点**：官方 MCP Server 部署、令牌权限、工具发现和实时仓库分析。
- **难度/前置条件**：中级；Docker、GitHub PAT、LLM API Key。
- **建议产出**：只读仓库健康报告，并限制 Token 权限和可调用工具集合。

## 四、高级应用与工程化

### 18. 生成式 UI 财务教练

- **路径**：[`generative_ui_agents/ai-financial-coach-agent/`](generative_ui_agents/ai-financial-coach-agent/)
- **中文简介**：多 Agent 分析预算、储蓄和债务计划，并把工具调用结果实时渲染为独立报告页中的交互式 UI 卡片。
- **核心技术**：Next.js、React、CopilotKit、AG-UI、Google ADK、FastAPI。
- **学习重点**：Agent 状态与前端同步、工具渲染组件、流式状态和前后端分离。
- **难度/前置条件**：高级；TypeScript/React、Python、Google API Key。
- **建议产出**：可编辑财务档案和可追溯到结构化 Agent 输出的报告界面。

### 19. Release Radar 常驻 Agent

- **路径**：[`always_on_agents/release_radar_agent/`](always_on_agents/release_radar_agent/)
- **中文简介**：定时读取 Python 或 npm 依赖清单，检查 GitHub Release，只报告破坏性变更、安全修复、弃用和大版本升级，并支持邮件或 Webhook 投递。
- **核心技术**：Google ADK、FastAPI、GitHub API、调度、Webhook、pytest。
- **学习重点**：Always-on Agent、确定性样例模式、信号排序、幂等投递和 dry-run 保护。
- **难度/前置条件**：中高级；FastAPI、定时任务、Gemini API Key。
- **建议产出**：改造成每日公司公告监控器，加入去重、人工审核和发送保护。

### 20. 保险理赔实时 Agent 团队

- **路径**：[`voice_ai_agents/insurance_claim_live_agent_team/`](voice_ai_agents/insurance_claim_live_agent_team/)
- **中文简介**：通过实时语音或文本采集首次损失通知，在对话过程中持续抽取理赔字段、证据和安全信号，并生成理赔员可接手的结构化材料包。
- **核心技术**：Gemini Live、Google ADK、FastAPI、WebSocket、Pydantic、确定性保险规则。
- **学习重点**：实时语音、增量状态、规则与模型协作、人工升级和审计轨迹。
- **难度/前置条件**：高级；异步 Python、WebSocket、Gemini Live API。
- **建议产出**：先完成纯文本和模拟数据版本，再接入实时语音；不得自动承诺赔付。

### 21. AI MCP App Builder

- **路径**：[`generative_ui_agents/ai-mcp-app-builder/`](generative_ui_agents/ai-mcp-app-builder/)
- **中文简介**：用户通过对话描述 MCP 应用，Agent 在 E2B 沙箱中生成并运行完整应用，再把它作为可交互界面嵌入聊天工作区。
- **核心技术**：MCP Apps、Next.js、Mastra、CopilotKit、AG-UI、E2B、Turbo Monorepo。
- **学习重点**：运行时代码生成、沙箱隔离、动态 MCP UI、双向工具访问和供应链安全。
- **难度/前置条件**：专家级；Node.js 20、pnpm、React、MCP、OpenAI 与 E2B 配置。
- **建议产出**：受限模板驱动的金融 MCP 仪表盘生成器，禁止任意网络和文件系统权限。

## 推荐学习顺序

1. 完成 2、3、4，掌握单 Agent、交互界面和多 Agent。
2. 完成 9、10、11，掌握基础 RAG、故障诊断和类型化回答。
3. 完成 14、15，并自行实现只读金融数据 MCP Server。
4. 完成 6、8 或 19 中的一个，学习复杂状态、服务化和测试。
5. 根据方向选修 12、13、18、20、21，不要求全部完成。

最终综合项目建议整合行情工具、财报 RAG、网页 MCP、风险 Agent、结构化引用、FastAPI 服务和人工审核，不包含自动交易功能。
