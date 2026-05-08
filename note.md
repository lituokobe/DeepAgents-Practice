In the class, the tutor makes `./3月28日直播代码/src` the source root of the project in PyCharm. This is a convenient IDE-specific setting.
As I usually develop/deploy project s across multiple machines/platforms, I will ignore this setup.

In the dependencies, `langgraph-cli[inmem]` is a package for quick testing on web. To use it, simply have `langgraph.json` as the configuration file in current directory and run 
```bash
langgraph dev
```
Your agent in the configuration file will be built and run on a webpage with clear illustrations of the structure.

To build agents with complicated workflows, user LangGraph. To build agents with for complicated tasks, use DeepAgents.

`create_deep_agent` in DeepAgents is a more advanced version of `create_agent` in LangChain that integrates more feature.
But in the source code, the returned object of this function is still a `create_agent`.

DeepAgents by default provides a set of tools for file manipulation (`ls`, `write_file`, `read_file`, etc.). It is realized by a pluggable **Backend** to execute.
