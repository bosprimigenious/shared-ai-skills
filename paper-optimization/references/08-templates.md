# 可复制的任务卡与 SOP 模板

## 新题启动提示词

> 使用 `$paper-optimization`。论文在【路径】，代码在【仓库】，题目规范在【路径/链接】，可用算力和额度为【约束】。先核对优化范围与原论文/代码差异，输出不超过三项有机制依据的假设，选择最便宜可验证的一项直接实现。冻结 baseline 与候选共同协议，先跑最小闭环，再做成对比较；保留真实源码快照、失败、checkpoint重载和费用记录。缺失规范显式标记，不能伪造收益或时长。用户只要求方案时先交方案，不自行消费。

## 任务契约

```yaml
task_id: null
paper_title: null
task_type: optimization
source_documents: []
code_revision: null
objective: null
editable_interface: null
frozen_components: []
metric: {name: null, direction: null, implementation_hash: null}
baseline: {definition: null, evidence: null}
score_anchors: {required: null, baseline: null, upper_bound: null, rationale: null}
resource_budget: {currency: null, total: null, approved_scope: null}
model_and_data: {revisions: [], licenses: [], split_manifest: null}
agent_requirements: {required: null, combinations: [], effective_hours_each: null}
submission_contract: {source: null, version: null, required_artifacts: []}
unknowns: []
status: NOT_READY
```

null 是未确定，不是 0、不需要或已通过。

## 单次实验卡

```text
Run ID / 协议版本：
观察与假设：
机制改变：
候选源码哈希 / baseline源码哈希：
共同模型、数据、seed、训练与评测预算：
额外校准／分解成本：
预期观察 / 否定条件：
实际启动命令 / PID / 日志：
退出码 / 失败分类：
全部seed结果 / 配对差：
checkpoint重载证据：
决定：继续 / 修改假设 / 不采用 / 基础设施修复
```

## 研究阅读卡

```text
来源URL、版本、作者代码commit、许可证：
解决什么具体失败模式：
与原方法不同的公式或步骤：
额外参数、数据、预处理、训练和推理开销：
本题接口是否容许：
对照与消融应如何设：
哪些主张仅来自论文，哪些已在本题实测：
```

## 成本台账

`时间 | provider/实例 | 单价及单位 | 数量 | 预计/实际时长 | 训练/空闲/存储/API | 累计 | 余额来源 | 下一轮止损`

预算估算与实际账单分列；没有余额访问权限时写“未知”，不保证足够。退租/关机前检查运行和队列，再备份。

双轨租卡任务另填：小时价、包日价、pilot 小时、正式小时、重租概率及依据、重租影响、API、存储、目标 GPU 库存、预约/保留条件、镜像 digest、持久快照位置、恢复演练状态、最终补测窗口。使用 `autoresearch-dual-track/scripts/plan_capacity.py` 同时计算小时、包日和混合方案。

## 进展汇报

> 已实际完成【动作与证据】；结果为【主指标、全部seed、与baseline差值】。当前【进程与阶段】；【失败/未过门槛】仍未解决。接下来运行【具体实验】回答【问题】，预计【时间/成本，注明估算】。整体【READY或NOT READY】。

短状态只写用户此刻需要知道的变化，不重复所有测试。项目在跑不能只说“都正常”，需要最近 step 或原始事件支撑。

## 续做交接提示词

> 直接检查和修改代码／执行必要实验，不要只输出计划。仓库【绝对路径】；先读【当前状态文件】，核对【PID、远端日志、最新summary】再行动，避免重复启动。已授权【范围和额度】，未授权【额外动作】。当前真实结果【值与证据路径】，硬阻塞【列表】，失败产物【位置】。第一阶段完成标准【实际训练/评分闭环】；第二阶段【成对验证/独立轨迹】；第三阶段【冻结方法、干净重跑、交付】。每一步报告实际输出，没跑就写没跑。凭据通过【机制】获得，不把值写到回复或仓库。

## 最终摘要

1. 原论文与当前任务的差异。
2. 优化假设、实现接口及计算成本。
3. 冻结实验协议、baseline和全部结果。
4. 失败尝试、排除理由与限制。
5. 干净重跑、轨迹和平台验收状态。
6. 可运行命令、资源要求、证据定位和剩余事项。

## 额外可沉淀的知识

除方法和登录命令，还应保存：规范变更台账、数据泄漏与许可清单、源代码—配置—结果血缘、负结果库、性能剖析、断点恢复与灾难恢复、费用预算、模型/harness兼容矩阵、隔离威胁模型、独立复核记录、可复用提示词、阶段验收与停止规则。

这些资料按项目需要添加，不要求每个小实验都建完整文档体系。
