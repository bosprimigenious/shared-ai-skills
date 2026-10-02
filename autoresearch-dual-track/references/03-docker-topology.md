# 双轨 Docker 拓扑

## 分层

```text
受信控制层（宿主机或独立控制服务）
├── API/provider 凭据、调度、成本与原始事件
├── agent-codex -> 独立无密钥 sandbox / 独立卷
├── agent-second -> 独立无密钥 sandbox / 独立卷
└── trusted-evaluator -> 隐藏资产、GPU 队列、receipt/reward

持久层
├── 内容寻址的镜像与代码快照
├── 只读公共模型/数据缓存
├── 两条互不可见的轨迹与方法产物
└── 正式 B/R、checkpoint、哈希和成本台账
```

两条 agent lane 使用同一任务镜像 digest，不维护两个漂移镜像。模型/provider 差异放在受信 controller 配置中；solver 文件系统只得到公共任务内容和本轨迹可写目录。

## GPU 调度

- 单卡：两个 lane 可保持容器状态，但 trainer/evaluator 通过可信锁串行获取 GPU。
- 双卡：使用明确 `device_ids`，记录宿主 `nvidia-smi` 和容器可见设备；逻辑 `cuda:0` 不等于宿主物理编号。
- 不用并行抢卡制造“有效时长”；资源竞争会污染性能和成本比较。
- `assets/compose.yaml` 仅是开发模板。运行前先执行 `docker compose config`，再用容器内 `nvidia-smi` 和真实最小前后向确认。

## 权限

Agent 不持有宿主 Docker socket、SSH 私钥、API key、peer 卷、Reference 或 tests。隐藏评分器不构建进 agent 镜像层。若 controller 能执行任意 root shell，必须限制模型能调用的参数与路径，否则容器名义隔离无效。

## Harbor 分界

Harbor 的 task environment 与开发 Compose 是两件事。根据当前目标版本核对：task 配置、主服务命名、工作目录、测试上传、solution/oracle、reward 文件和 backend GPU 支持。2026-10-02 查阅的官方 Harbor task-creator 文档提示其 DockerEnvironment 不支持 GPU 请求；因此 GPU Harbor 运行必须使用当期支持的 backend 或平台适配，不能拿租赁机上的普通 Compose 成功代替。
