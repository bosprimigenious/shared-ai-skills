# AutoResearch 双轨 GPU 执行

> Plan, deploy, resume, and audit two independent AutoResearch agent trajectories with rented GPU capacity, Docker isolation, trusted evaluation, cost controls, and Harbor-aware acceptance. Use when an AutoResearch task requires two long-running model tracks, GPU hourly-versus-daily decisions, recoverable cloud execution, or final container/harness evidence; not for ordinary single-run model training.

## 目标与边界

把两条独立 Agent 轨迹从“能启动”推进为可恢复、可计费、可追溯和可验收的运行。科学问题、Baseline/Reference 与统计判断仍由 `paper-optimization` 负责；本 skill 负责容量、容器、双轨隔离、可信评分、快照和最终运行证据。

Docker Compose 能在配置正确的 NVIDIA 主机上分配 GPU，但不等于目标 Harbor backend 支持 GPU。开发执行层与最终 Harness 层分别验收；目标 backend、版本和 GPU 支持必须以当前官方文档或平台证据为准。

## 按当前阶段读取

| 阶段 | 读取 | 必须产出 |
|---|---|---|
| 选题与正式消费前 | [选题预检](references/02-task-selection.md) | 可否证 pilot、阈值、随机性与停止条件 |
| 小时/包日选择 | [成本与容量](references/01-cost-capacity.md) | 三方案成本、容量风险与推荐 |
| 部署两条轨迹 | [双轨拓扑](references/03-docker-topology.md) | 冻结镜像、隔离卷、可信评分路径 |
| 启动、暂停、换机 | [运行与恢复](references/04-runbook.md) | run manifest、快照、恢复验收 |
| 打包或报 READY | [验收门禁](references/05-acceptance.md) | 聚合结论与未验证边界 |
| 核对外部依据 | [来源边界](references/06-sources.md) | 版本化来源，不凭记忆写平台能力 |

## 默认资源策略

1. 本地 CPU/MPS 或便宜小 GPU 先清除构建、接口、数据、恢复和单步训练问题。
2. 目标 GPU 按小时跑一次完整 Baseline/Reference pilot，实测训练、评分、重载和快照时间。
3. 只有 pilot 通过、协议冻结且正式工作预计连续推进时，才比较继续小时制、包日或“小时 pilot + 包日正式窗口”。
4. 把再次租不到、重建、延期和无法补测的期望损失计入小时制；包日未使用时长是容量保险成本，不伪装成计算利用率。
5. API、GPU、存储分别记账。加钱不能修复阈值缺失、trial 身份混合或 Harness 部署缺口。

用 `scripts/plan_capacity.py` 生成透明估算；价格、报销上限和库存必须由当前任务填写，skill 不固定平台价格。

## 双轨不可变约束

- 两条轨迹从同一公共任务哈希和冻结起点开始，但使用独立可写目录、上下文、日志、方法快照与 run ID。
- Agent 不可读取 peer、Reference、隐藏测试、可信评分器或控制器凭据。
- 单 GPU 默认串行评分；双 GPU 才能显式绑定设备并行。不同轨迹的重叠时间分别记录，但不能把资源墙钟错误相加。
- 每个正式结果只绑定一个真实 trial：源码、配置、seed、receipt、artifact、checkpoint 与时间窗必须一致。用 `scripts/verify_lineage.py` 拒绝拼接结果。
- 租赁实例不是唯一存储。镜像 digest、代码、轨迹、checkpoint、receipt 和成本台账在关机前同步到持久位置，并至少做一次重建恢复。
- 密钥仅在受信控制层注入，不写进 Compose、镜像、轨迹、仓库或提交包。

## Harness 边界

先固定目标 Harbor 版本和 backend，再使用该版本真实命令。Harbor 任务至少核对 task 配置、instruction、environment、tests/test.sh、reward 路径和可选 solution；Oracle、Starter、负例与最终 Agent Trial 各回答不同问题，不能互相替代。

本 skill 的 Compose 模板是租赁 GPU 主机上的开发/轨迹执行参考，不声明与 Harbor 原生 Docker backend 等价。若目标 Harbor backend 不支持 GPU，使用当前支持的云 backend 或平台适配；没有真实运行就写“静态检查通过，动态未验证”。

## 停止条件

以下任一出现就暂停新消费：正式阈值或随机性协议未冻结；pilot 无法区分候选与噪声；结果身份链不完整；恢复演练失败；目标 backend 未确定；预算达到止损线；没有下一条能减少硬阻塞的实验。

## 本机维护

唯一源位于 `~/shared-ai-skills/autoresearch-dual-track`。修改后运行中枢 `sync-formats.sh`、验证脚本和 `build.sh --dry-run`，再同步软链。不得把私人平台凭据或未经授权的规范全文写入 skill。
