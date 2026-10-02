# GPU 选择、登录、运行、备份与费用

## 1. 开机之前准备什么

先让源码、依赖、数据来源和最小启动命令可执行，再租卡。估算模型权重、可训练参数、梯度／优化器、激活、checkpoint 和缓存磁盘；用实测短跑修正估算。参数高效训练仍要经过底座前后向，不能按适配器大小估全部显存。

推荐默认是能满足峰值内存并有调试余量、软件成熟且可扩容的单卡；更大卡在大模型／长序列／多实验吞吐上可能更适合。不要因为别人的报销表用了最好卡就推定本题需要同卡。以实际 tokens/s、整轮用时和总成本判断性价比。

查看的是**空闲数**而非总数；截图显示 0/9 就不是还有 9 张。磁盘不可扩容可能比显存更早成为阻塞。当前价格、优惠资格、CUDA 镜像和库存都要临时确认，skill 不固定价格。

费用至少包含：开机空闲、装环境、失败试跑、正式训练、存储、数据传输以及 API。预算拆成启动／探索／确认／轨迹／返修余量，记录消耗，临近上限停止新一轮而不是期待之后报销。

### 按小时还是按天

默认先按小时租，完成环境、真实训练器短跑、计时和失败恢复演练；只有在工作负载已经稳定、能连续占用较长时间时才切到包日。不要在代码、模型、数据或正式入口仍未闭环时先买整天。

用当前平台价格计算盈亏点，而不是凭感觉：

`break_even_hours = daily_price / hourly_price`

估计本次可计费占用：

`billable_hours = 环境准备 + pilot + 正式运行 + 评分/重载 + 备份 + 合理返修余量`

- 当 `billable_hours` 明显低于盈亏点，或中途存在等待用户/API/下载/改代码的不确定性，先选按小时；但若关机后同规格 GPU 很可能租不到，还要加入 `重租概率 × 重建/延期/无法补测损失`，不能只比较表面单价。
- 当工作流已通过短跑，预计连续占用超过盈亏点，包日更省；但仍要设置自动停机/人工检查点，不能把包日理解为必须跑满。
- 若包日跨自然日、关机仍计费、磁盘另计费或不可退款，把这些条款计入总成本。两条 10h agent 轨迹不等于一张卡连续 20h：并行度、GPU evaluator 占用和 controller 等待要按真实资源时间展开。
- API 与 GPU 分开记账。API 余额不足会导致轨迹中断，但不会解释统计协议、结果身份或 Harbor 部署缺陷；诊断时不要把所有 NOT READY 都归因于“钱没充够”。

切换包日前的硬条件：源码与依赖已冻结；模型/数据已就绪；一次端到端短跑成功；单轮时长有实测；断点恢复与日志落盘已验证；下一批任务无需等待外部决定。缺一项则继续小时制或暂停消费。

需要两条长期 Agent 轨迹、Docker 隔离和跨实例恢复时，转用 `autoresearch-dual-track` 的三方案成本模型。Docker 镜像与外部快照能降低换机成本，但不能保证平台有库存；预约或包日购买的是容量确定性，不应伪装成 GPU 利用率。

## 2. SSH 首次登录

以下是占位命令，先填自己的主机、端口和受信账号。首次连接核对控制台提供的主机指纹；不要用关闭主机校验作为常规排错。

```bash
command -v ssh
command -v scp
ssh -p PORT USER@HOST
```

密码通过终端隐藏输入或受信凭据工具提供，不写在命令参数、仓库、Markdown 或截图里。若需要自动化，使用专用 SSH key，先检查已有授权并备份，再追加本任务公钥；保留原有授权，不覆盖整个文件。密钥只存受信机器的私有目录，设置适当文件权限。

```bash
ssh -i /absolute/private/controller_key \
  -o IdentitiesOnly=yes -o BatchMode=yes \
  -o ConnectTimeout=15 -o ServerAliveInterval=20 \
  -o ServerAliveCountMax=3 -p PORT USER@HOST
```

不要把控制账号的 key 挂载到 solver 中。实例 root 仅作为安装／隔离控制器时，模型执行应降到专用 UID；模型获得 root 后，再用普通文件权限隐藏参考解没有意义。

## 3. 常见连接差异

- 交互 shell 的 PATH 不等于 SSH 非交互 PATH。发现 `python3: command not found` 时先查真实解释器路径，随后固定绝对路径，不断猜 `python` 名称没有帮助。
- ControlMaster 可减少重复认证，但 socket 路径有长度限制；使用短、归当前用户、0700 的目录。socket 不存在就先确认 master 已失效，不自动把它当账号密码错误。
- 密码正确也可能因交互等待过久断开。保留真实错误，重试次数和连接超时有上限；多次鉴权拒绝应检查控制台实例状态和连接信息，不尝试猜密码。
- 端口／容器重建可能变化；不要把旧登录命令当永久配置。此手册不保存任何项目账号凭据。

## 4. 首次远端盘点

```bash
id
uname -a
pwd
df -h
command -v nvidia-smi
nvidia-smi
command -v python3
command -v tmux
command -v rsync
```

随后使用已确认的 Python：

```bash
/absolute/python -c 'import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO_CUDA")'
/absolute/python -c 'import torch; x=torch.randn(256,256,device="cuda",requires_grad=True); (x@x).square().mean().backward(); torch.cuda.synchronize(); print(bool(torch.isfinite(x.grad).all()))'
```

这只证明基础 CUDA 前后向，后面还要跑真实训练器和重载。驱动显示的 CUDA 上限不是已安装 PyTorch 的 CUDA runtime；新卡需要实际支持其架构的构建。版本跟项目锁文件和官方兼容说明走，不盲目升级整套依赖。

## 5. 部署规范

代码、数据、模型各自版本固定。传输前排除 `.env`、API key、SSH 私钥、用户配置、其他项目数据。覆盖远端代码前先保存可回滚快照；rsync 有 dry-run，先看清列表。

```bash
rsync -avni -e 'ssh -p PORT -i /absolute/private/controller_key' \
  /absolute/reviewed-source/ USER@HOST:/absolute/new-release/
```

把实际执行版放新 release 目录更容易追溯。首次配置完成后记录：锁文件、pip/conda 实际版本、驱动、硬件、模型 revision、数据哈希和完整启动 argv。缓存模型与数据可省钱，但双方使用同一内容且不得混入隐藏数据。

## 6. 真实运行与状态判断

选择已有可靠管理方式：tmux、任务调度器、nohup 加持久 wrapper 或平台作业。wrapper 写 PID、启动时间、源码哈希、exit code 和最终摘要。PID 可重用，后续检查还要核对命令和启动时间。

观察顺序：控制进程 → 本轮工具调用 → 远端训练 PID/UID → train step 是否增长 → GPU/CPU 资源 → checkpoint → 独立重载 summary。同步等待 GPU 的时候 RPC 没新增不一定卡死。

```bash
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv
ps -eo pid,uid,etime,time,args
tail -n 5 /absolute/run/train.jsonl
```

间隔再检查 step，不必每秒重复大量日志。GPU 0% 可能是在 CPU 初始化、读数据或 agent 思考；判断是否合理要结合当前阶段。长时间没有合法工作且没有下一步，不让实例无限空耗。

## 7. 让控制器也可靠

本地 Mac 跑 API controller 时，睡眠、断网、退出应用都会影响轨迹；远端 GPU 进程可能仍在跑。必要时用系统支持的防空闲睡眠工具跟随特定 controller PID，例如本机的 `caffeinate -i -w PID`。这不是有效时长证明。

更长作业可把受信 controller 部署到稳定主机，但不能把 API key 暴露给不可信训练进程。监控应重读状态文件并验证 PID，不能因为一次断网立即重启整轮造成重复训练和消费。

## 8. 备份、关机、释放

先收集源码快照、配置、方法、训练/评分/observer/原始轨迹和失败日志；用传输后的哈希核对。大模型公共缓存未必需要复制，但必须能按固定版本重新获得。

确认没有活跃任务、没有自动队列即将启动，再按平台的关闭方式停止计费。关机、删除实例、释放磁盘是不同动作；了解数据保留期后再操作。报销资料保留实际规格、时间、审批和费用，不把估算训练成本当整个账单。

历史案例的 6.98 元/小时仅用于解释旧记录；用当前控制台价格和余额规划新运行。
