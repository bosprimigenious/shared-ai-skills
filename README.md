# Shared AI Skills

跨 Coding Agent 复用的技能中枢。每个顶层目录是一项独立 skill，以 `SKILL.md` 为唯一指令源；`AGENTS.md` 与 `CLAUDE.md` 由同步脚本生成，不手工维护。

本仓库只发布可公开、可移植的通用能力。项目专用规则、个人策略、工作目录、凭据和私有协作平台内容不进入公开版本。

## 快速开始

```sh
git clone https://github.com/bosprimigenious/shared-ai-skills.git
cd shared-ai-skills

# 先预览将创建的全局软链
./_scripts/build.sh --dry-run

# 确认后同步到本机已安装的 Agent
./_scripts/build.sh
```

也可以只把指定 skill 安装到当前项目：

```sh
cd /path/to/project
/path/to/shared-ai-skills/_scripts/install.sh engineering-principles git-commit
```

安装脚本默认使用软链，避免多个 Agent 各自维护过期副本。目标位置已有真实目录时会停止覆盖；只有确认内容已合并后才使用 `--force`。

## AutoResearch 工作流

- `paper-optimization`：从论文与代码建立可复现的优化任务、实验协议和证据边界。
- `autoresearch-dual-track`：规划 GPU 小时/包日、双轨 Docker、恢复、血缘、Harness 验收与平台登记回读。
- `engineering-principles`：在 READY、验收、迁移和交接中执行 fail-closed 的证据纪律。
- `public-release-privacy`：公开发布前扫描路径、凭据、私有链接、归档与文档元数据。

其中平台表格流程只保留通用状态机与验证规则：先从当期权威源读取 schema 和记录主键，再精确写入并回读；领取、材料上传和组长初筛是三种不同状态。仓库不保存真实平台链接、账号、题号映射、记录 ID 或表格正文。

## Skill 目录

| 类别 | Skills |
|---|---|
| 研究与工程 | `paper-optimization`, `paper-polish`, `autoresearch-dual-track`, `engineering-principles`, `git-commit` |
| 资料与历史 | `agent-figure-gallery`, `continuum-history`, `classroom-note-reconstruction` |
| 图像与文档 | `image-text-restore`, `layered-poster-collage`, `zh-handwritten-notes`, `zh-typst-resume` |
| 运维与发布 | `mihomo-auto-routing`, `public-release-privacy` |
| 生活场景 | `trip-itinerary-guide` |

使用前阅读目标目录的 `SKILL.md`。Skill 只提供决策规则和工作流，不会自动扩大外部写入、付费服务、GPU 租赁或公开发布的授权。

## 开发与验证

新增或修改 skill 时：

```sh
./_scripts/sync-formats.sh
./_scripts/build.sh --dry-run
./_scripts/privacy-scan.sh
git diff --check
```

若 skill 带测试，再运行该目录自己的测试入口。提交前只暂存本次文件；不要使用 `git add -A` 把 `_projects/`、个人策略、`work/`、附件或缓存带入公开仓库。

## 隐私边界

公开版本默认 fail-closed：归档损坏、加密或不可读，路径含个人目录，文件含凭据、私有协作链接、内部端点或作者元数据时，发布应停止。扫描通过也不替代人工审查；Git 作者邮箱、历史提交、旧 release 和 fork 需要单独检查。

## License

各 skill 沿用其目录中的许可证或来源声明；没有单独许可证的内容不得推定为可再分发。
