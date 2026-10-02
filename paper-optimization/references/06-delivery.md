# 提交、仓库、ZIP 与干净复现

## 1. 三种状态分开

`代码存在`、`实验链路通过`、`题目可提交` 是不同状态。最终 READY 要求当前任务所有适用门槛通过；没有训练任务就不强加训练门槛，没有 Harbor 平台就不强加 Harbor 格式。

对论文优化常见需要：来源/许可、baseline、固定预算、参数与数据边界、完整结果、正收益要求、复现、最终包。对 agent benchmark 还需要模型身份、独立性、隔离与轨迹。

## 2. 包内有什么

以平台规范为准，从已审阅清单导出，通常包括任务说明、代码、锁文件、配置、模型/数据获取或离线资产清单、训练/评分入口、候选方法、原始证据索引和复现说明。

如果采用 历史案例的三目录模板：

```text
workspace/
  harbor_task/       # solver任务、允许的公共资产、评分接口
  reference/         # 专家参考解，不能挂载给solver
expert_evidence/     # 两模型原始轨迹、方法、人工说明、校验
optimization_evidence/ # baseline/reference训练与比较
```

这不是所有平台的默认格式；有些平台需要隐藏测试、外部资产和不同路径。最终文件名以当前示例及 validator 为准。

## 3. Harbor / Docker 检查

核对实际安装的 Harbor parser 版本/schema，而不只看 `schema_version` 字符串。`[task]`、agent user、资源、网络、verifier 字段都应被目标版本解析且实际生效。

Docker `COPY` 源相对 **build context**，不是相对 Dockerfile。教学 `docker build -f environment/Dockerfile TASK_ROOT` 与平台从 `environment/` 构建不同；用错可能越界或缺文件。需要实际 parser → build → run → verifier → reward 验证，而不是 grep 几行配置。

没有 Docker 权限时如实记录本地未完成，使用平台支持的验收渠道；不要在 Mac 上把静态检查报成 Linux build 成功。

Docker Compose 在普通 NVIDIA 主机上获得 GPU，不证明目标 Harbor 的 Docker backend 支持 GPU。按目标 Harbor 版本分别验证 backend 能力。Oracle 只证明 solution 与 verifier 的正向闭环；还要运行 Starter/负例防止平凡满分或 reward hack，并保留真实 Agent Trial。命令先以安装版本 `--help` 为准，不从旧教程复制。

## 4. Git 与实际提交包

```bash
git status --short
git ls-files
git diff --check
git check-ignore -v path/to/required_script.py
```

检查锁文件、复现入口、评分器依赖都在提交清单。白名单式 `.gitignore` 容易漏掉新脚本；`git archive HEAD` 不会包括未提交修改，不能把它当最新工作树的自动备份。也不要直接 `zip -r project .` 把凭据和全部缓存打进去。

保留用户已有改动，不因要提交就全量 add、格式化或 reset。是否 commit/push 依用户授权和仓库要求；中心 skill 的维护规则不扩展为项目自动提交权限。

## 5. 密钥、隐私与许可

导出前对显式清单扫描 `.env`、私钥、令牌、授权配置、原始认证头和带密钥日志；自动扫描有盲区，还要人工审阅可疑路径。不要通过在报告中打印命中原文来再次泄漏。

私人平台教程保存本地来源索引即可，不默认进入 GitHub 或对外 skill。第三方代码与模型/数据许可要跟随规定，包含归属、来源和必要 notice。一个“私有仓库”也不代表可以上传任何受限数据。

## 6. 干净重放

在新目录解压，检查顶层布局与文件哈希；使用规定环境从包内入口完成至少一条真实训练/评测路径，最终方法另做完整重跑。复现入口不得依赖作者机器未打包绝对路径、未声明环境变量或旧缓存。

验收要回答：拿到 ZIP 的人能否独立获得依赖/资产、执行方法、生成真实 checkpoint、重新评分、得到相同口径结论？格式校验通过不是性能或隔离验收。

输出简明账本：已验证、失败、未运行、平台侧待办。负结果和中途修复仍在记录中；只打包最好分数而省掉失败轨迹，会损害可核查性。

## 7. 交接时必须有

项目绝对路径、当前版本及 dirty 状态、正在运行 PID/任务ID、日志位置、最后真实结果、未过门槛、下一条具体命令、预计费用和停止条件、凭据所在机制（不含值）、哪些动作已经授权、哪些资源绝不能混到 solver 里。

长期运行状态单独存在可更新文件，案例文档是带时间戳的快照。旧 `compliance-status.json` 可能落后现场，续做时先查实际日志，发现差异就注明。
