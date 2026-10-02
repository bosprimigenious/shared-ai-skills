# Continuum History

> Search, read, and migrate local coding-agent conversation history through Continuum: explicit source import, literal search, pagination, and derived-index migration. Use when the user asks to find past chats, import Cursor/Claude/Codex history, migrate a Continuum index, or continue Continuum adapter development. Do not auto-discover private logs or write vendor databases.

用本机 Continuum 索引检索、阅读、显式导入和迁移对话历史。兼容 Grok / Codex / Claude Code / Cursor：读这份 `SKILL.md` 并执行，不要另写一套扫描家目录的脚本。

仓库默认路径：`~/Projects/ai-tools/continuum`。开发手册真源是仓库内 `docs/development.md`，不要把本 skill 当第二份产品计划，也不要在这里维护 P0–P6。

## MCP 与 Skill（不要做成两套产品）

| 层 | 职责 | 不是 |
| --- | --- | --- |
| Skill（本文件） | 何时用、授权口吻、禁止扫盘、CLI 导入/迁移、开发时去读哪份手册 | 不是搜索引擎，不解析 `state.vscdb` |
| MCP | 进程启动时已选定 `--db` 后的四只读工具 | 不能 import、不能发现源、不能当权限系统 |
| CLI | 显式 import + 与 MCP 同一套查询 | 不是 HTTP 后端 |

检索语义必须一致：字面子串、`preview` 可截断、`history_read`/`read` 才是全文、跟 `next_cursor` 直到 `null`、`stale_cursor` 要重启分页。Skill 用 CLI 示范，MCP 已连接就只调工具，不要再跑一遍 CLI，也不要为 GUI 新写检索。

有害重合（要避免）：把开发刀写死在 skill 里（曾误写「当前刀是 P0」）；宣称无 GUI 或 GUI READY；在 MCP 里加 import。GUI 壳存在但 **GUI NOT READY**（无浏览器 e2e）。不要新开 Continuum HTTP API。

## Core Rule

不自动发现私人历史；不写厂商会话库；没有用户点名的路径和授权，不读真实 Cursor / Claude / Codex / Grok 日志。 Continuum **原生适配器在 live 宿主验收前一律报 `native adapter NOT READY`**，地基测试通过不能替代。

导入一份 `state.vscdb` 会读取该文件里**全部**受支持会话，不能把「允许看一条」扩成「导入整个库」。

## 先分模式

| 用户要的 | 做什么 |
| --- | --- |
| 搜/读已经导入的对话 | 只查派生索引，不碰源。已连 MCP 就用四工具；否则用 CLI |
| 导入或迁移 | 用户给出源文件和新索引路径；先快照再 **CLI** `import`。MCP 没有 import |
| 继续开发 Continuum | 在仓库根改代码，读 `AGENTS.md` 和 `docs/development.md`。P0/P1 已落地；原生下一刀是 **P2**（无授权则 BLOCKED） |
| 升级 GUI | 只改 `gui/` + CLI JSON 桥；不写 HTTP 后端，不在 skill 里画产品路线图 |

三种不要混。搜对话时不要开始写适配器；开发时不要去扫 `~/Library/Application Support/Cursor`。

先跑探测（不读取会话正文）：

```sh
bash ~/shared-ai-skills/continuum-history/scripts/continuum_probe.sh
```

缺仓库、缺 `uv`、或索引不存在时据实报告，不要假装能搜全机历史。

## 检索已导入索引

默认索引由用户指定。没有 `--db` / `CONTINUUM_DB` 就问，不要猜家目录里的 sqlite。
脚本解析 stdout 时加 `--format json`（终端默认可读文本；无子命令时第一个位置参数视为 `search`）。

```sh
ROOT="${CONTINUUM_ROOT:-$HOME/Projects/ai-tools/continuum}"
# INDEX 必须是用户选定的派生库，不是 Cursor 的 state.vscdb
uv run --directory "$ROOT" continuum --db "$INDEX" --format json sources
uv run --directory "$ROOT" continuum --db "$INDEX" --format json search '用户给的关键词'
uv run --directory "$ROOT" continuum --db "$INDEX" --format json list --limit 20
uv run --directory "$ROOT" continuum --db "$INDEX" --format json read "$SESSION_ID" --limit 20
```

规则：

- 字面子串搜索，不是语义搜索。中文短查询有效。
- `preview` 可能截断；完整正文只在 `read`。跟 `next_cursor` 直到 `null`。
- `stale_cursor` / `invalid_cursor` 是要重启分页，不是空结果。
- 不要把整段对话贴进公共 issue、commit 或 skill 仓库。
- MCP：`uv run --directory "$ROOT" continuum --db "$INDEX" serve`。工具只有 `history_sources` / `history_list` / `history_search` / `history_read`。连上等于该客户端能读**整个**选定索引。没有 import 工具。已连 MCP 时不要再复制一套 CLI 检索。

没有导入过的来源：告诉用户需要显式 `import`，而不是去翻 `.cursor` / `.claude` / `.codex`。

## 显式导入（不是自动迁移厂商库）

用户必须给出：源文件路径、`--source-id`（原生适配器）、以及**派生** `--db` 路径。导入前问清范围。

合成快照（已实现）：

```sh
uv run --directory "$ROOT" continuum --db "$INDEX" --format json import \
  "$ROOT/examples/synthetic.snapshot.json"
```

Cursor IDE `state.vscdb`（合成夹具已接线；真实宿主 **未验收**）：

```sh
uv run --directory "$ROOT" continuum --db "$INDEX" --format json import \
  --adapter cursor-state-vscdb --source-id cursor-demo \
  "$CURSOR_SOURCE"
```

导入后立刻核对：源文件字节未改；`sources` 里的 `adapter` / `coverage`；用约定关键词 `search`；`read` 跟 cursor 直到结束；再导入一次得到 `"changed": false`。

授权口吻（读真实库之前必须得到明确同意，沉默不等于同意）：

> 是否允许读取你指定的这一份会话库，导入到新的 Continuum 派生索引？只会使用你给出的路径；不会扫描家目录其它日志；不会改厂商数据库。导入会覆盖该 `source_id` 在派生索引里的全部旧行。

## 迁移派生索引（schema / 换路径）

这是 Continuum **派生库**的迁移，不是把对话写回 Cursor。

当前：规范化快照仍是 schema v1；派生 SQLite `user_version=2`。打开 v1 索引会 `unsupported_schema`。没有自动 `ALTER`。

顺序（反了会把失败的新库暴露给客户端）：

1. 停掉读写该索引的 CLI/MCP。
2. 给旧索引做一致性快照（`tar` 不要 `-h`）。活跃 WAL 期间不要只拷主库。
3. 建**新路径**，不要覆盖唯一副本。
4. 用匹配的代码版本把保留的快照/源重新 `import` 进新路径。
5. 核对 counts / coverage / 搜索 / 末页。
6. 再把客户端 `--db` 指过去。

失败：停新客户端，用旧代码打开旧索引。源文件始终不改、不删。

详细命令和 Cursor 格式边界见 [references/operations.md](references/operations.md)。开发阶段与 P0–P6 只在仓库手册里维护，见 [references/develop.md](references/develop.md)。

## Hard Stops

- 不扫描 `~/Library/Application Support/Cursor`、`~/.cursor`、`~/.claude`、`~/.codex`、`~/.grok/sessions`，除非用户给出具体文件且明确授权。
- 不把真实 `state.vscdb`、`.jsonl`、会话正文提交进任何 git 仓库。
- 不对厂商库 `INSERT`/`UPDATE`/`VACUUM`/`checkpoint`。读取用 `mode=ro`。
- 不宣称支持 Claude Code / Codex 原生格式、Cursor JSONL、自动发现、语义搜索。
- 不宣称 GUI READY（Vite 壳 + pytest 已有，浏览器 e2e 未过）；不写 Continuum HTTP 后端。
- 不把工具块/thinking JSON 塞进 `text` 再声称全文支持。
- 不把 foundation gate 绿说成 native adapter 或产品 READY。
- 开发 Continuum 时不在 `$HOME` 改项目代码；一次会话一个主仓库。

## Quality Checks

- 探测脚本已跑，缺依赖已说明。`continuum --help` 不需要 `--db`。
- 合成路径：`bash ~/shared-ai-skills/continuum-history/scripts/continuum_skill_check.sh`
- 检索用的是派生索引，不是源库。
- 导入有用户点名的路径和 `source_id`；真实库有明确授权。
- 源文件导入前后指纹未变；重复导入 `changed=false`。
- 长会话跟完 `next_cursor`。
- 迁移先新路径后切客户端。
- 状态用 `native adapter NOT READY` / 部分完成，不写「已经能搜全部历史」。
