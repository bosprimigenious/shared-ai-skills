# 开发 Continuum 时

不要在 skill 里维护第二份里程碑。动手前读仓库：

1. `~/Projects/ai-tools/continuum/AGENTS.md`
2. `~/Projects/ai-tools/continuum/docs/development.md`
3. `~/Projects/ai-tools/continuum/docs/architecture.md`

在**该仓库根**启动，保留 `git status` 里已有未提交内容。工具链跟 `uv.lock`。

P0/P1 已在仓库落地。原生下一刀是手册里的 **P2（授权真源 + MCP 宿主）**；无授权保持 BLOCKED。不要在 skill 里重开 P0，也不要为 GUI 新写 HTTP 后端。GUI 是 CLI JSON 壳，**GUI NOT READY**。里程碑只以 `docs/development.md` 为准。

门禁：

```sh
cd ~/Projects/ai-tools/continuum
uv run python scripts/check.py
```

出口仍以手册为准：fixture 绿不等于 live 绿；P2 要用户授权真实源；P3 要非作者复装。未通过就报 `native adapter NOT READY`。

Claude Code / Codex 适配器、GUI/桌面是否开工，只看仓库 `docs/development.md`。这里不跟踪里程碑。
