# Sandbox
## 1. Defining Sandbox
Agents need to generate code, operate files, and run Shell commands.  
As **we can not predict what agent will execute exactly**, we need to isolate its environment from the host machine,
to prevent it from visiting sensitive files or network.  
The sandbox provides this isolation by setting up boundaries between agent environment and host machine.

In DeepAgents, sandbox is a special backend. Different from other backends (`State`, `Filesystem`, `Store`), sandbox backend 
provide a tool of `execute` to the agents to perform Shell commands in the isolated environment.

## 2. Sandbox Toolset
- **File System Operation Tools**
    - `ls` - List directory contents
    - `read_file` - Read file
    - `write_file` - Write file
    - `edit_file` - Edit file
    - `glob` - File pattern matching
    - `grep` - Text search

- **Execution Tools**
    - `execute` - Run Shell command
        - Can run any commands
        - Return stdout/stderr
        - Return exit code

- **Security Boundaries**
    - Cannot access host files
    - Cannot read host environment variables
    - Cannot interfere with host processes

### Sandbox Service Providers
- Daytona is a sandbox service provider. Visit `sandbox-daytona.py` to understand how to use it.
- OpenSandBox is the open source sandbox service by Alibaba.

## 3. OpenSandBox

### 🎯 Overview
OpenSandbox is an open-source, general-purpose sandbox platform designed to provide secure, isolated execution environments for AI agents, code interpreters, and autonomous systems. Officially released in March 2026 under the Apache 2.0 license.

### ✨ Key Features
- **4-Layer Architecture**: SDKs → OpenAPI Specs → FastAPI Runtime → Containerized Sandbox Instances
- **Multi-Environment Support**: Code interpreter, shell commands, filesystem operations, browser automation (Chrome/Playwright), and GUI/Desktop (VNC-enabled)
- **Stateful Execution**: Maintains session state across multiple code/command executions within a sandbox lifecycle
- **Network & Ingress/Egress Controls**: Configurable per-sandbox egress policies and unified ingress routing
- **Production-Ready Tooling**: Batch sandbox creation, connection pooling, and checkpointing for reinforcement learning training
- **Extensible Design**: Container-based environments allow custom tooling, dependency injection, and third-party integrations

### 💻 Supported Programming Languages
**Client SDKs (Integration Layer)**
- Python (`pip install opensandbox`)
- JavaScript / TypeScript (`npm install @alibaba-group/opensandbox`)
- Java / Kotlin (Maven/Gradle)
- C# / .NET (NuGet)
- Go (Go modules)

**Execution Languages (Inside Sandbox)**
- Python, JavaScript/Node.js, Bash/Shell
- *Fully Extensible*: Any language or runtime can be supported via custom Docker images or package installation within the sandbox container

### 🚀 Deployment Options
- **Local / Development**: Docker-based single-node deployment for testing, prototyping, and lightweight workloads
- **Production / Cloud-Native**: Kubernetes-native deployment with:
  - Horizontal auto-scaling & sandbox pooling
  - Integration with Kubernetes `agent-sandbox` SIG standards
  - Support for secure, high-isolation runtimes: `gVisor`, `Kata Containers`, `Firecracker microVMs`
- **Flexible Orchestration**: Deployable as standalone services or integrated into existing AI agent pipelines, CI/CD workflows, and multi-tenant platforms

### 🔒 Security & Isolation
- Hardware/OS-level isolation via secure container runtimes
- Strict filesystem, process, and network namespace separation
- Automated sandbox lifecycle management with timeout enforcement and resource cleanup
- OpenAPI-driven contract enforcement for consistent, auditable execution
- Apache 2.0 licensed for open commercial, academic, and enterprise use

### Deployment
Visit the project of sandbox for the local deployment of OpenSandbox.
Start an API server that dynamically creates/manages sandbox containers.
```shell
opensandbox-server
```

OR, use Docker deployment to manually start one notebook container.:
```shell
docker pull sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.2

docker run -d \
--name opensandbox \
-p 8080:8080 \
sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.2 \
jupyter lab \
--ip=0.0.0.0 \
--port=8080 \
--allow-root \
--no-browser
```
### In our project
We customized a OpenSandbox backend based on the class of `BaseSandbox` from the source code. Please find the class of `OpenSandboxBackend` from `OpenSandboxBackend_by_Tuo.py`.
In this class, the most important function is `execute`, it will execute all the commands in the sandbox.
There are two fundamentally different ways to access files inside a sandbox. Understanding when to use each approach is very important.

#### 1. Agent Filesystem Tools

Examples:

- `read_file`
- `write_file`
- `edit_file`
- `ls`
- `glob`
- `grep`
- `execute`

These are tools directly invoked by the LLM during task execution.

They operate through the sandbox’s internal `execute()` environment, allowing the agent to so the basic file manipulation.

---

#### 2. File Transfer APIs

Examples:

- `uploadFiles()`
- `downloadFiles()`

These are APIs explicitly called by your application code. They provide local file transfer capabilities (rather than shell commands) for moving files between:
- The host environment
- The sandbox environment

**Typical use cases for these APIs include:**

- **Initializing the sandbox**  
  Upload source code, configuration files, or datasets into the sandbox before the agent starts running.
- **Retrieving generated artifacts**  
  Download generated code, build outputs, reports, or other artifacts after the agent completes its work.
- **Preloading dependencies and resources**  
  Prepare dependency files or resource assets required during the agent’s execution.

---

#### 3. Usage

**Uploading Files**

Use `upload_files()` to write files into the sandbox before the agent starts running. Requirements:
- File paths must be absolute paths
- File contents must be provided as byte streams (`bytes`)

**Downloading Files**

Use `download_files()` after the agent completes execution to:
- Read files from the sandbox
- Or download them to another location

## 4. Take a try
Make sure in `langgraph.json`, the agent is set as follow: `"agent": "./sandbox/sandbox_agent.py:agent"`, then
```shell
langgraph dev
```