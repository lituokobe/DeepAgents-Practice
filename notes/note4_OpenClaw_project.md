# OpenClaw Project
This project will cover following topics:
- Skills
- MCP
- sandbox
- user preference/long term memory
- connection to Java web project
- FastAPI (Async)
- ASGI Agent (Linux server)
- vue (UI) with SSE

## 1. Context Engineering

Context Engineering is the process of designing and controlling the information that an agent can access during runtime.

In Deep Agents, agents can access multiple types of context and dynamically manage them during execution. The framework includes automatic context management mechanisms, allowing agents to maintain long-running tasks without exceeding the model’s context window limitations.

The table below summarizes the main context types and their intended use cases:

| Context Type                   | Controlled Content                                                         | Scope                                                                       |
|--------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Input Context                  | System prompts, memory documents, skill files, tool descriptions           | Statically loaded at the beginning of every execution                       |
| Runtime Context                | User metadata, API keys, database connections                              | Scoped to a single invocation (`invoke`) and can be passed to sub-agents    |
| Context Compression            | Automatically summarizes large conversations and long-term context         | Triggered automatically to prevent context overflow                         |
| Context Isolation (Sub-agents) | Split large files into independent sub-agent tasks and return only results | Each sub-agent maintains its own isolated context                           |
| Long-term Memory               | Persistent storage for cross-session state and files                       | Can persist across threads, users, organizations, or long-running workflows |

### Backend and Memory
In the below example code:
```python
create_deep_agent(
    model=qwen_llm,
    skills=[sandbox_skills_path],
    tools=[web_search],
    memory=["/AGENTS.md"],
    backend=backend,
    subagents=subagents
)
```
- Backend usually stores system prompts and user-preference.
- `memory` setting will need the file path in the backend system. These files will be automatically loaded into the context as part of the system prompt, no need to have extra steps.

### Progressive disclosure
In the below example `SKILL.md`:
```markdown
---
name: linux-system-info
description: 当用户提问关于当前计算机的系统信息，例如操作系统详情、Python环境、磁盘空间、网络配置等时，使用此技能。本技能利用一个Python脚本获取结构化信息。
---

# Linux 系统信息查询技能

## 概述
本技能用于获取并报告当前系统的详细信息。为了提供准确、结构化的信息，请运行同目录下的 `get_system_info.py` 脚本。

## 重要提示
- **必须在项目根目录下运行脚本**：脚本使用相对路径，必须在项目根目录下执行

## 操作步骤
1. **检查当前工作目录**：
......
)
```
- When agents start, they only read the YAML part the `SKILL.md`s in all the skill paths. The YAML part is a description of the skill, less than 1024 bytes.
- When LLM decides to call the skill, it will read the whole `SKILL.md` file.
- Different form `memory` which always stays in context. Skills are loaded on demand.

### Runtime context
- Configuration data (e.g. user ID, API keys, database connections) won't automatically be loaded into the context.
It is only loaded when the tool or middleware reads it.
- Usually no context isolation, all the sub-agents share the same runtime context from the primary agent.

### Context Compression
DeepAgents has prebuilt mechanism of offloading and summarization to maintain the context size.
- `ToolCallLimitMiddleware`: Summarize (keeping the first 10 lines) the results of tool calls if too long (default threshold `BIG_TOOL_RESULT_LIMIT`: 20,000 tokens, not supported to change as of May 2026), save the full result in a file. Read the file in the future if needed.
- When the whole chat history (user inputs, model output, tool call records) occupies more than 85% (not supported to change as of May 2026) of the context window, DeepAgents will prioritize to trim the parameters (with full content) of `write_files` or `edit_file` tool calls, as they are already persisted in the file system.
- After the above 2 strategies, if the context still reaches to 85% of the context window (or 170,000 tokens), save the recent 6 messages or the last 10% of the tokens as fresh context and summarize the rest. This is a passive default setting. If you don't like the default way, you can also configure: 
  - `SummarizationToolMiddleware` (with an LLM, and summary prompt) from DeepAgents with the tool of `compact_conversation`.
  - `SummarizationMiddleware` (with an LLM, and summary prompt) from LangChain.

### Cross-session memory
Persistent storage for cross-coversation/threads/users. DeepAgents use file read/write to realize this feature. You can configure the backend to control the actual storage location.

## 2. Project Description
Acquisition Assistant:
- Analyze historical acquisition data and storage data
- Crawl supplier's price quotation
- Generate full analysis report and acquisition proposal
- Generate acquisition plan and list with human intervention, revise accordingly

### Preparation
The ERP system is running with JAVA, and the project folder is `./38_Java_ERP`, open it with IDEA.
Preparation:
- Install JDK and IDEA.
- Create a database named `motorparts_db` in mySQL.
- Open the project with IDEA and configure the database in `./src/main/resources/application.yml` - `datasource`
- Run `./src/main/java/com.motroparts/MotorpartsAplication.Java` to start the service.
  - Visit http://localhost:8080/swagger-ui/index.html for the internal ERP system.
- Run `./src/main/java/com.motroparts/init/SparkPlugDataInitializer.Java` to initialize the database.
- Launch the simulated external supplier web (static) with Nginx for crawling:
  - copy the files to Homebrew Nginx web root: 
  ```shell 
  cp -R /Users/lituokobe/Desktop/Mashibing_LLM_course/38_Java_ERP/ecommerce-demo/* $(brew --prefix)/var/www/ 
  ```
  - port 8080 is taken by the Java ERP system, this Brew Nginx web server is running on port 8081. Run below:
  ```shell 
  brew services start nginx
  ```
  - Visit http://localhost:8081/index.html for the simulated external supplier web.

### Multi-agent
1. Primary agent is the coordinator that 
  - understands the request
  - delegates tasks to sub-agents
  - manages memory
  - manages / creates skills, allocates new skills to sub-agents
  - NOT performs ERP system tasks
2. Analysis assistant is a sub-agent that
  - collects data
  - analyzes data
  - generates charts
  - exports report
3. Procurement assistant is a sub-agent that
  - understands the order
  - calls MCP tools
  - validates result
  - confirm the order

### Example of dataflow
```mark down
1. User Input: "Help me conduct a supplier price comparison analysis for motorcycle spark plugs"

2. ContextInjectionMiddleware
   → Extract from runtime.context: user_id="lx", username="lx"
   → Inject into SystemMessage: "Current user user_id: lx, preference file: /memories/lx/preferences.md"

3. MemoryMiddleware
   → Load global rules from sandbox /AGENTS.md → Inject into system prompt

4. Agent Routing
   → Read /memories/lx/preferences.md (StoreBackend)
   → Determine: "price comparison analysis" → Route to procurement-analyst

5. task(procurement-analyst) Delegation Format:
   [Task Objective] [User Preferences] [Analysis Requirements] [Output Requirements]

6. Sub-Agent (procurement-analyst) Execution:
   a. ls /skills/procurement/ → Scan available skills
   b. supplier_query("spark plugs") → MCP → Java backend → ERP data
   c. part_by_supplier(supplier_id) → Query parts by supplier
   d. Skill: Read supplier-price-urls/data/url_mapping.yaml
      → Match URLs → web-content-fetcher → Crawl external quotes
   e. Python analysis script → /data/analysis_result.json
   f. generate_visualization("bar", chart_config={...}) → Chart URL
   g. write_file("/analysis/report_20260509.md") → Final report

7. Sub-Agent → compact_conversation → Return structured results to Agent
```
### Storage (CompositeBackend)
| Path                 | Backend                      | Persistence                               | Content                                             |
|----------------------|------------------------------|-------------------------------------------|-----------------------------------------------------|
| /AGENTS.md           | OpenSandbox (default route)  | Sandbox lifecycle                         | Global behavior guidelines (Phase 1.4 upload)       |
| /skills/             | OpenSandbox (default route)  | Sandbox lifecycle + StoreBackend recovery | Skill files (pre-configured + persistence hybrid)   |
| /memories/{user_id}/ | StoreBackend → InMemoryStore | Cross-session                             | User preference files                               |
| /persisted-skills/   | StoreBackend → InMemoryStore | Cross-session                             | Persisted skills                                    |
| Other paths          | OpenSandbox (default route)  | Sandbox lifecycle                         | Temporary files, code execution, analysis artifacts |

### Middlewares
| Middleware                    | Function                                                 |
|-------------------------------|----------------------------------------------------------|
| `ContextInjectionMiddleware`  | Inject `user_id`/`username` into system prompt           |
| `SkillsSyncMiddleware`        | Sync local `src/skills/` → sandbox                       |
| `UserSkillsRestoreMiddleware` | Restore skills from StoreBackend persistence → sandbox   |
| `SummarizationToolMiddleware` | Provide `compact_conversation` tool + auto-summarization |
| `ModelCallLimitMiddleware`    | Max 50 model calls                                       |
| `ToolCallLimitMiddleware`     | Max 200 tool calls                                       |


Custom Middleware in the Project

1.  **Read/Write Separation:** ContextInjection (Reading Memory) ↔ MemoryUpdate (Writing Memory). When injecting, explicitly inform the Agent: "System auto-maintains, no manual update required."
2.  **Three-Layer Skills Synchronization:** SkillsSync (Local → Sandbox) + UserSkillsRestore (Store → Sandbox) + SkillsMiddleware (Sandbox → Agent Discovery). Each handles a specific segment.
3.  **Differentiated Management for Main/Sub-Agents:** The Main Agent has panoramic middleware, the Analyst retains summaries, and the Order agent only requires restrictions—reduce configuration as needed.
4.  **Silent Failure > Crash:** ContextInjection two-level degradation, SkillsSync exception capture, MemoryUpdate full try/except, no middleware failure should drag down the Agent.
LLM can take the errors from tools, but cannot take the errors from the middleware. Tools are under the LLM. But middleware is part of the system design.

### Port mapping
- 8080: Java ERP system ()
- 8081: Nginx web server (external supplier web)
- alicloud_host:8080: OpenSandbox (deployed on AliCloud ECS)

### Start the project
Run `./OpenClaw_project/src/mcp_server/server_main.py` to start the MCP server.  
Run `./OpenClaw_project/start_web.py` to start the service including frontend and backend.








## 3. Special Features
OpenSandbox is a private sandbox deployed with Docker. One user user should have one dedicated sandbox, with all the isolated resources.

### 3.1 Privately deployed sandbox
### 3.3 Customized Progressively Disclosed Tool Description
In the MCP of data visualization, there are 27 tools.  
To make good use of context, I created another tool `generate_visualization()` to assemble their top level description first, after LLM decides which tool to use, load the detailed descriptions of parameter definition.  
In practice, expose this one tool instead of 27 tools.
### 3.3 Complete Frontend and Backend Based on SSE Event Streams

Architecture Overview: Division of Labor Among Three Files

```text
1 api_view/api/
2 ├── chat.py          ★ Core: SSE Streaming Chat + Interrupt Detection + Interrupt Recovery + Display Message Persistence
3 ├── history.py       ◂ History Session List / Message Viewing / Session Deletion
4 └── agent_loader.py  (Upper Layer) ◃ Agent Singleton / MongoDB Connection / Display Message Storage and Retrieval
```

| Frontend (Browser)              | Backend (FastAPI)                                   | LangGraph Agent |
|:--------------------------------|:----------------------------------------------------|:----------------|
| **POST** `/api/chat/stream`     |                                                     |                 |
| `{message, thread_id, user_id}` |                                                     |                 |
| ----------------------->        | `⊕ stream_chat_response()`                          |                 |
|                                 | `├─ agent_loader.get_agent_for_user(user_id)`       |                 |
|                                 | `├─ agent_loader.create_config(thread_id, user_id)` |                 |
|                                 | `├─ Construct input:`                               |                 |
|                                 | `│  Initial: {"messages": [{"role":"user",...}]}`   |                 |
|                                 | `│  Resume: Command(resume=resume_data)`            |                 |
|                                 | `│`                                                 |                 |
|                                 | `⊕ agent_graph.astream(`                            |                 |
|                                 | `   input, config,`                                 |                 |
|                                 | `   stream_mode=["messages","values"],`             |                 |
|                                 | `   subgraphs=True, version="v2"`                   |                 |
|                                 | `)`                                                 |                 |
|                                 | `↓↓↓ Start Streaming Push ↓↓↓`                      |                 |
| `← SSE: token`                  | `⊕ messages stream: (token, metadata)`              |                 |
| `← SSE: tool_start`             | `← token has tool_call_chunks → Tool Start`         |                 |
| `← SSE: tool_args`              | `← Tool argument delta`                             |                 |
| `← SSE: tool_result`            | `← type=="tool" → Tool Result`                      |                 |
| `← SSE: tool_end`               | `← Tool call ended`                                 |                 |
| `← SSE: interrupt`              | `⊕ values stream: chunk["interrupts"]`              |                 |
| `← SSE: done`                   | `⊕ Stream ended normally`                           |                 |