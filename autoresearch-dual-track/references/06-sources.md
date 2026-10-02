# 外部来源与已核实边界

以下是设计依据，不锁定未来版本。每次正式运行重新读取目标版本：

- Docker Compose GPU support：`https://docs.docker.com/compose/how-tos/gpu-support/`。确认 `capabilities: [gpu]` 必填，`count` 与 `device_ids` 互斥，宿主需具备 GPU 与正确 Docker runtime。
- Docker Compose startup order：`https://docs.docker.com/compose/how-tos/startup-order/`。确认容器启动不等于服务 ready；需要 healthcheck 与 `service_healthy`。
- NVIDIA Container Toolkit installation：`https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html`。确认 Docker 需配置 NVIDIA runtime；具体驱动/runtime 兼容性以目标主机为准。
- Harbor task structure：`https://github.com/harbor-framework/harbor/blob/main/docs/content/docs/tasks/index.mdx`。
- Harbor task creator skill：`https://github.com/harbor-framework/skills/blob/main/skills/harbor-task-creator/SKILL.md`。2026-10-02 检查到的当前说明包括任务结构、reward 路径、Oracle 流程，以及 DockerEnvironment 不支持 GPU、GPU task 需使用支持的 backend。命令和 backend 列表可能变化，执行前用安装版本 `--help` 复核。

不要引用搜索摘要来证明本机已运行；外部文档只证明接口能力，现场仍需保存版本、命令和实际输出。
