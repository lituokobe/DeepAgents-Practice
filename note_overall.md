# DeepAgents
## 1. Preface
In the class, the tutor makes `./3月28日直播代码/src` the source root of the project in PyCharm. This is a convenient IDE-specific setting.
As I usually develop/deploy project s across multiple machines/platforms, I will ignore this setup.

In the dependencies, `langgraph-cli[inmem]` is a package for quick testing on web. To use it, simply have `langgraph.json` as the configuration file in current directory and run 
```bash
langgraph dev
```
Your agent in the configuration file will be built and run on a webpage with clear illustrations of the structure.

## 2. Intro to DeepAgents
In the production environment, to handle complicated tasks, agents must have the capability to operate files (add, delete, edit, search, etc.)  
For example, 
- temp data will be created during tasks and it could stuff the context. Agents needs to save the temp data to a file and it needs the capability to operate files.
- some code needs to be executed during the task, it needs the capability to save the code to a file.
To build agents with complicated workflows, user LangGraph. To build agents with for complicated tasks, use DeepAgents.

`create_deep_agent` in DeepAgents is a more advanced version of `create_agent` in LangChain that integrates more feature.

DeepAgents provides:
- **Planning capability**: with `write_todos` tool, it maintains a structured task list
- **Virtual file system**: the virtual file system is maintained via a backend
- **Task delegation/child agents**: contemporary child agents can be created and delegated to, they have independent context and can run concurrently
- Context management

But in the source code, the returned object of this function is still a `create_agent`.

DeepAgents by default provides a set of tools for file manipulation (`ls`, `write_file`, `read_file`, etc.). It is realized by a pluggable **Backend** to execute.

## 3. Backend
> Backend is the underlying system or service that actually powers the agent’s intelligence, storage, tools, or execution.

It is a key of DeepAgents' `create_deep_agent`.

| Concept           | Backend                      | Tool                                          |
| ----------------- | ---------------------------- |-----------------------------------------------|
| Purpose           | Powers the system internally | Gives abilities to the agent                  |
| Used by           | Framework/developer          | Agent/LLM                                     |
| Visibility to LLM | Usually invisible            | Directly visible                              |
| Examples          | OpenAI API, Redis, Docker    | `web_search()`, `calculator()`, `sql_query()` |
| Level             | Infrastructure layer         | Agent action layer                            |

### 3.1 StateBackend
The default backend for DeepAgents. It stores the file data to LangChain/LangGraph's state. 
The data will be persisted and called during a thread (conversation), but will disappear when the thread ends.  
**`checkpointer` MUST be provided** (unless using LangSmith (`langgraph dev`) to deploy).  
Best for drafting of Agents or storing middel result.

### 3.2 FilesystemBackend
It allows Agents to read/write files in a assigned `root_dir` on the local machine.  
Security alert: 
- always set `virtual_mode=True` to use path sandbox, preventing Agent using `..` or `~` to visit outside the `root_dir`.
- do not put sensitive files in `root_dir`.

Please visit `./agent/my_agent2.py` for reference.

### 3.3 LocalShellBackend
Add the tool of `execute` on top of `FilesystemBackend`. It allows Agents to execute shell commands on the host machine.
**Alert**: This is a dangerous backend, please only use it with trusted agent code and reliable inputs.

Please visit `./agent/my_agent3.py` for reference.

### 3.4 StoreBackend (The backend storage from LangGraph)
Use LangGraph's `BaseStore` abstract to save files and to persist data across threads.  
This is for the long-term memory of the agent.  
**MUST pass an argument `store = InMemoryStore()/RedisStore()/PostgreStore()` to `create_deep_agent`.**

### 3.5 CompositeBackend
The router at backend. Direct the operation to different backends based on the file appendix.  
Example: mix store - temp file use `StateBackend`, long-term memory use `StoreBackend`, specific directory maps to local disk.

### 3.6 Customized Backend
Inherit the class of `BackendProtocal` and its ports, you can expose to any storage (e.g AWS S3, database) to the agent.

Please visit `./agent/my_agent4.py` for reference.

## 4. Comparison
- Backend → the agent’s operating environment, like a sandbox or workspace, it is tied to DeepAgents.
- Checkpointer → workflow execution recovery, it is usually ties to LangGraph.
- Store → long-term persistent memory, it is an optional integration.

### **Comparison: Checkpointer, Store, and Backend in Agent Development**

| Feature               | **LangGraph Checkpointer**                                                                                                               | **LangChain Store (BaseStore)**                                                                                                  | **DeepAgents Backend**                                                                                                         |
|:----------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------|
| **Design Goal**       | **Workflow State Recovery.** Provides snapshots to enable persistence, pause/resume, time-travel (rewind), and Human-in-the-loop (HITL). | **Global Long-term Memory.** A universal storage layer for custom data that needs to persist across different threads and users. | **Environment Abstraction.** Provides a "Virtual Filesystem" for the agent to interact with a directory tree like a real user. |
| **Data Model**        | **Serialized State.** Snapshots of the entire `State` object, including message history and internal variables.                          | **Namespaced Key-Value.** Structured data organized by keys and namespaces.                                                      | **File/Directory Tree.** Path-based content management (File paths and contents).                                              |
| **Key Operations**    | Internal `checkpoint` save/load (automatic during graph execution).                                                                      | `get`, `set`, `delete`, `list`                                                                                                   | `ls_info`, `read`, `write`, `edit`                                                                                             |
| **Persistence Scope** | **Thread-Level.** Primarily used to allow a specific conversation thread to continue after a break.                                      | **Global/Cross-Session.** Shared data accessible by any agent or thread (e.g., global user preferences).                         | **Environment-Level.** Can be `StateBackend` (Thread), `Filesystem` (Process), or `StoreBackend` (Session/Cloud).              |
| **Typical Use Case**  | Chatbots remembering current conversation context; multi-step workflows requiring human approval.                                        | Storing user profiles, shared knowledge bases, or long-term behavioral preferences.                                              | Agent workspace for coding; loading skills and documents; managing a `/memories/` folder.                                      |
| **Analogy**           | A **"Quick Save"** in a video game to restart from the exact same moment.                                                                | A **Personal Notebook** or Database where facts are recorded for future reference.                                               | A **Hard Drive** or a local folder where the agent "works" on files.                                                           |

### **Decision Logic: Which one to use?**
* **Checkpointer:** Use when you need **Fault Tolerance** or **Human Intervention** within a specific task execution.
* **Store:** Use when you need **Cross-Thread Knowledge** (e.g., "The user told me they live in London in a previous chat").
* **Backend:** Use when you need an **Operating Workspace** for the agent to create, edit, or manage files and tools.

Many teams add a small memory consolidation step at the end of a session — 
an LLM call that extracts key facts from the Redis checkpoint and writes them to Postgres 
before the session closes. This is sometimes called memory distillation.


| Layer                | Recommended Technology | Role                                       |
|:---------------------|:-----------------------|:-------------------------------------------|
| Short-term           | Redis                  | Live checkpoint, session state             |
| Long-term structured | PostgreSQL             | Distilled facts, user profile, preferences |
| Long-term semantic   | Milvus (optional)      | Fuzzy recall, RAG, large episodic memory   |

## 5. Harness Engineering
$$Agent = Model + Harness$$
Harness Engineering in DeepAgents:
1. Planning
    - Critical difference from traditional agents: plan first, then delegate subagents/call tools. Traditional agents call tools directly one by one.
    - Provide a tool of `write_todos` and let the agents to maintain structured task list.
    - Realized with the middleware `TodoListMiddleware`.
    - Let the agent track multiple tasks and their status, suitable for complicated multip-step tasks.
2. File System
    - `ls_info` and `read`/`write`/`edit` for file system as mentioned above.
3. Task Delegation/Subagents
    - Primary agents use tool of `task` and middleware `SubAgentMiddleware` to delegate specialized task to subagents.
    - Developers can predefine different system prompts and child agents for task specialization.
    - Advantages: context isolation, concurrency, and efficient token usage.
4. Context Management
5. Code Execution and Sandbox
6. Human-in-the-loop
7. Skills
