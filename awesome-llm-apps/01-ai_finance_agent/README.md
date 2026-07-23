## AI 金融分析 Agent

这个应用是一个金融分析 Agent，使用 DeepSeek 模型服务，并结合实时股票数据和网页搜索能力，提供结构化的金融分析结果。

### 功能

- 支持 DeepSeek 官方 API
- 通过 YFinance 获取实时股票数据
- 通过 DuckDuckGo 进行网页搜索
- 金融和数值数据会优先用表格展示
- 提供 AgentOS 交互式界面

### 快速开始

1. 克隆仓库
```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/01-ai_finance_agent
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置模型服务

在 `01-ai_finance_agent/.env` 或仓库根目录 `awesome-llm-apps/.env` 中填入你的 DeepSeek API key、服务地址和模型名：
```bash
DEEPSEEK_API_KEY=你的DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_ID=deepseek-chat
```

如果需要使用其他 DeepSeek 模型，可以把 `DEEPSEEK_MODEL_ID` 设置为服务支持的模型名，例如 `deepseek-chat`、`deepseek-reasoner`、`deepseek-v4-flash` 或 `deepseek-v4-pro`。

4. 运行 AgentOS API
```bash
python finance_agent.py
```

启动成功后，本地服务会运行在：

```text
http://localhost:7777
```

直接访问这个地址会看到 AgentOS API 信息。要使用图形化聊天界面，请打开 Agno 官方控制台并连接本地服务：

```text
https://os.agno.com/
```

如果 `https://os.agno.com/` 因网络、DNS 或地区访问限制打不开，可以先用本地方式确认 Agent 正常：

```text
http://localhost:7777/docs
```

也可以直接运行本项目提供的终端聊天入口，不依赖 Agno 官方网页：

```bash
python local_chat.py
```

### 访问方式说明

`http://localhost:7777` 是本地 AgentOS API 服务，不是聊天网页。直接打开它通常只会看到类似下面的 JSON，表示服务已经启动：

```json
{"name":"AgentOS API","id":"...","version":"1.0.0"}
```

图形化聊天界面由 Agno 官方控制台提供：

```text
https://os.agno.com/
```

这里不是让 Agno 的服务器直接访问你的本地端口，而是你浏览器中打开的 Agno 控制台页面连接本机的 `http://localhost:7777`。本地 Python 进程负责运行 Agent 和工具调用，浏览器里的官方控制台负责展示聊天、会话和运行管理界面。

如果官方控制台无法访问，通常不是本地 AgentOS API 的问题。可按下面顺序排查：

1. 打开 `http://localhost:7777/docs`，能看到 Swagger 页面说明本地服务正常。
2. 确认浏览器可以正常访问 `http://localhost:7777`。
3. 使用 `python local_chat.py` 在终端里直接与 Agent 对话。
4. 等外网环境可访问 `https://os.agno.com/` 后，再在官方控制台里添加 `http://localhost:7777`。

本项目不额外自写 Streamlit 页面，原因是它已经使用 Agno 的 `AgentOS` 运行方式。官方控制台正好匹配这套 API，可以复用 AgentOS 的会话、运行记录和后续管理能力；自写页面会绕开这些能力，并引入额外的前端和 Python 环境依赖。

5. 连接 AgentOS

如果需要通过浏览器中的 AgentOS Control Plane 管理、监控和使用这个 Agent，需要把当前运行的 AgentOS 实例连接到控制台。

参考官方文档：

- [Connecting Your OS](https://docs.agno.com/agent-os/connecting-your-os)
