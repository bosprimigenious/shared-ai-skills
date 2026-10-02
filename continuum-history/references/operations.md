# Continuum 操作细节

SKILL.md 是入口。这里只补命令、格式边界和迁移，避免把开发手册再抄一份。

## 本机约定

| 变量 | 含义 |
| --- | --- |
| `CONTINUUM_ROOT` | 默认 `~/Projects/ai-tools/continuum` |
| `CONTINUUM_INDEX` | 探测脚本用的派生 sqlite 路径（可空） |
| `CONTINUUM_DB` | CLI 在未传 `--db` 时使用的派生 sqlite |
| `CURSOR_SOURCE` | 用户点名的一份 `state.vscdb` |

命令一律 `uv run --directory "$CONTINUUM_ROOT" continuum --db "$INDEX" ...`。仓库用 `uv.lock`，不要另起 pip。

## 已实现 / 未实现

已实现（合成证据）：规范化快照 v1 导入；字面搜索与分页；`--format json|text` 与 `CONTINUUM_DB`；四只读 MCP 工具（无 import）；Cursor `state.vscdb` / `cursorDiskKV` 只读适配器（合成夹具）；CLI JSON GUI 会话（pytest）。

未验收：真实 Cursor 宿主；Cursor agent-transcripts JSONL；工作区 sidebar DB；Claude Code / Codex 适配器；自动发现；GUI 浏览器 e2e；签名桌面包；Windows 启动/查询；PyPI `continuum-history`；语义搜索；附件/工具块全文。

P0 合成失败边界已收紧。不要在 skill 里发明另一种解析器。MCP 与 CLI 查询同一 `HistoryStore`；导入只走 CLI。

报状态时拆开写，不要用「能搜全部对话」概括。

## Cursor 这一份格式（仅此适配器）

显式文件：`state.vscdb`。表：`cursorDiskKV`。

- 会话：`composerData:{id}`，`fullConversationHeadersOnly`，可选 `gitWorktree.worktreePath`
- 消息：`bubbleId:{composerId}:{bubbleId}`，`type` 1=user / 2=assistant，可选 `text` / `createdAt`
- 只读：`mode=ro` + `query_only`；不要 checkpoint WAL
- 需要 `--source-id`
- 工具/thinking/codeBlocks → coverage `unsupported_block`，不进 `text`

缺口：JSONL transcripts、`composer.composerHeaders`、checkpoint、protobuf、live 宿主。

## 失败导入

结构损坏、缺被引用 bubble、源在读取中变化：应失败或 `complete=false`，且**不得覆盖**已有派生索引里的成功快照。未知形态不得标 complete；超范围时间戳不得抛裸异常。在仓库修，不要在 skill 里发明另一种解析器。

## 迁移清单

```sh
# 1. 停客户端后快照旧索引（含 -wal/-shm 如果存在）
tar -cf "$BACKUP/index.snapshot.tar" -C "$(dirname "$OLD_INDEX")" "$(basename "$OLD_INDEX")"

# 2. 新路径导入，不要覆盖 OLD_INDEX
uv run --directory "$ROOT" continuum --db "$NEW_INDEX" import ...

# 3. 核对
uv run --directory "$ROOT" continuum --db "$NEW_INDEX" sources
uv run --directory "$ROOT" continuum --db "$NEW_INDEX" search '约定标记'

# 4. 通过后再改 MCP/CLI 的 --db
```

`source_id` 相同的新导入是原子替换该来源，不是历史并集。新快照没有的旧事件会从派生索引消失。
