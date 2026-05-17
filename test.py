from datetime import timedelta
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync

# config = ConnectionConfigSync(
#     domain="http://127.0.0.1:8080",
#     request_timeout=timedelta(seconds=120),
# )
#
# print("Creating sandbox...")
#
# sandbox = SandboxSync.create(
#     "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.2",
#     connection_config=config,
# )
#
# print("Sandbox created!")
# print(sandbox.id)
#
# result = sandbox.commands.run("python3 --version")
#
# print(result)
#
# result = sandbox.commands.run("pwd")
#
# print(result)
#
# print(dir(SandboxSync))

sandbox.delete()