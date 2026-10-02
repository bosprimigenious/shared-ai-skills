# 运行与恢复手册

## 阶段 A：零消费/小卡

1. 冻结题面、接口、阈值、随机性协议与提交格式。
2. 构建 agent 镜像和 evaluator 镜像，固定 digest。
3. 运行 CPU/小卡单步、checkpoint 保存/加载、失败原子写与 secret scan。
4. 建立两个 lane，验证 peer、隐藏资产和凭据不可见。
5. 用 `preflight.py` 检查任务合同；失败不进入正式消费。

## 阶段 B：目标 GPU 小时 pilot

1. 记录主机、GPU、驱动、runtime、镜像 digest 和数据/模型哈希。
2. 完成一对真实 B/R：训练、评分、checkpoint、独立重载、receipt。
3. 实测各阶段时长和峰值资源，运行 `plan_capacity.py`。
4. 在关闭实例前上传快照并核对远端/本地哈希。

## 阶段 C：正式窗口

1. 协议与镜像冻结后启动两条独立轨迹。
2. 单 GPU 串行评估；每轮绑定代码快照、真实 run ID 和评分。
3. 达到停止条件后冻结各自 best，不用另一条轨迹结果回填历史。
4. 按预声明协议完成正式 B/R 和确认运行。
5. 在目标 Harbor 版本/backend 上运行实际 parser/build/trial/verifier/reward 链；未执行就保留未验证。

## 关机前门禁

- 无活跃 trainer/evaluator/自动队列；
- 轨迹、方法、checkpoint、receipt、成本台账和失败日志已同步；
- 上传端和持久端哈希一致；
- 恢复说明含下一命令与凭据机制但不含凭据值；
- 平台关机状态得到确认，不只以 SSH 断开推断。

## 恢复演练

至少一次在新容器或新实例：拉取同 digest 镜像、恢复快照、核对哈希、继续一个中断后的测试轮、独立重载已有 checkpoint。只验证“文件能下载”不等于可以补测。
