In the class, the tutor makes `./3月28日直播代码/src` the source root of the project in PyCharm. This is a convenient IDE-specific setting.
As I usually develop/deploy project s across multiple machines/platforms, I will ignore this setup.

In the dependencies, `langgraph-cli[inmem]` is a package for quick testing on web. To use it, simply have `langgraph.json` as the configuration file in current directory and run 
```bash
langgraph dev
```
Your agent in the configuration file will be built and run on a webpage with clear illustrations of the structure.

## Intro to DeepAgents
To build agents with complicated workflows, user LangGraph. To build agents with for complicated tasks, use DeepAgents.

`create_deep_agent` in DeepAgents is a more advanced version of `create_agent` in LangChain that integrates more feature.

DeepAgents provides:
- **Planning capability**: with `write_todos` tool, it maintains a structured task list
- **Virtual file system**: the virtual file system is maintained via a backend
- **Task delegation/child agents**: contemporary child agents can be created and delegated to, they have independent context and can run concurrently
- Context management

But in the source code, the returned object of this function is still a `create_agent`.

DeepAgents by default provides a set of tools for file manipulation (`ls`, `write_file`, `read_file`, etc.). It is realized by a pluggable **Backend** to execute.

## Backend
> Backend is the underlying system or service that actually powers the agent’s intelligence, storage, tools, or execution.

It is a key of DeepAgents' `create_deep_agent`.

| Concept           | Backend                      | Tool                                          |
| ----------------- | ---------------------------- |-----------------------------------------------|
| Purpose           | Powers the system internally | Gives abilities to the agent                  |
| Used by           | Framework/developer          | Agent/LLM                                     |
| Visibility to LLM | Usually invisible            | Directly visible                              |
| Examples          | OpenAI API, Redis, Docker    | `web_search()`, `calculator()`, `sql_query()` |
| Level             | Infrastructure layer         | Agent action layer                            |

#### StateBackend
The default backend for DeepAgents. It stores the file data to LangChain/LangGraph's state. 
The data will be persisted and called during a thread (conversation), but will disappear when the thread ends.  
`checkpointer` must be provided, unless using LangSmith (`langgraph dev`) to deploy.  
Best for drafting of Agents or storing middel result.

#### FilesystemBackend
It allows Agents to read/write files in a assigned `root_dir` on the local machine.  
Security alert: 
- always set `virtual_mode=True` to use path sandbox, preventing Agent using `..` or `~` to visit outside the `root_dir`.
- do not put sensitive files in `root_dir`.
