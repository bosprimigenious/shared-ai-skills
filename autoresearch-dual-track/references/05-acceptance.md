# 聚合验收门禁

## 资源与恢复

- 成本台账完整，小时/包日选择有当前价格依据；
- 正式窗口包含合理补测余量；
- 租赁磁盘不是唯一副本；
- 换容器/换机恢复演练通过。

## 双轨

- 两条轨迹的模型/provider、起止事件、有效时长与原始记录真实；
- 公共起点哈希一致，可写卷、上下文和产物独立；
- 不可读取 peer、Reference、隐藏 tests 和凭据；
- 最终 best 有实际方法快照，不只是高分数字。

## 实验与血缘

- B/R 使用冻结协议，全部适用 seed/replicate 都保留；
- 每个 result 的 run ID、源码、配置、receipt、artifact、checkpoint 和时间窗一致；
- 负结果与补充敏感性没有被删除或冒充正式结果；
- 独立重载和质量门通过。

## Docker 与 Harness

- 开发 Compose 静态配置、目标主机 GPU 可见性和真实最小运行分别验证；
- Harbor task 通过目标版本解析；
- Oracle 证明任务可解，Starter/负例防止平凡满分和 reward hack；
- tests 在所有路径写合法 reward；
- 真实 Agent Trial 和目标 GPU backend 状态明确。

任何适用硬门失败即 NOT READY。静态检查不能升级成动态运行，Compose GPU 成功不能升级成 Harbor GPU 成功。
