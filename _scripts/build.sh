#!/usr/bin/env bash
# build.sh - 将共享 skills 符号链接到各 AI 工具的全局目录
# 用法: ./build.sh [--dry-run] [--force]
#   --dry-run  只打印将要做的操作
#   --force    允许覆盖目标位置已存在的「真实目录」（默认拒绝，避免误删本地独有 skill）
set -euo pipefail

SHARED_DIR="$(cd "$(dirname "$0")/.." && pwd)"

DRY_RUN=0
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --force)   FORCE=1 ;;
    *) echo "未知参数: $arg" >&2; exit 1 ;;
  esac
done

# 各工具的全局 skills 目录。每个都读 <skill>/SKILL.md。
# 第三字段 always：即使工具 home 不存在也建目录（约定路径，不是独立 App）。
# 注意: Cursor 用 ~/.cursor/skills（用户 skill）；~/.cursor/skills-cursor 是 Cursor
# 自带的内置集，有它自己的 .sync-manifest.json，不要往里写。
TARGETS=(
  "$HOME/.qoder/skills|Qoder"
  "$HOME/.claude/skills|Claude Code"
  "$HOME/.codex/skills|Codex"
  "$HOME/.cursor/skills|Cursor"
  "$HOME/.grok/skills|Grok"
  "$HOME/.agents/skills|Agents (Grok/DeepSeek)|always"
  "$HOME/.dsh/skills|DeepSeek Harness"
  "$HOME/.deepseek/skills|DeepSeek TUI"
)

echo "🔧 共享 Skills 同步工具"
echo "========================"
echo "源目录: $SHARED_DIR"
[ "$DRY_RUN" = 1 ] && echo "模式:   dry-run（不实际改动）"
echo ""

skipped_total=0

sync_target() {
  local target_dir="$1" tool_name="$2" mode="${3:-}"

  echo "📁 $tool_name -> $target_dir"

  # 工具自己的配置目录不存在 = 没装这个工具，跳过。
  # 不给未安装的工具凭空造目录；装上之后重跑本脚本会自动纳入。
  # mode=always：约定目录（如 ~/.agents），即使 home 不存在也 mkdir。
  local tool_home; tool_home="$(dirname "$target_dir")"
  if [ "$mode" != "always" ] && [ ! -d "$tool_home" ]; then
    echo "  ⏭️  跳过：未检测到 ${tool_home} （该工具未安装）"
    echo ""
    return 0
  fi

  if [ ! -d "$target_dir" ]; then
    if [ "$DRY_RUN" = 1 ]; then
      echo "  [dry-run] 将创建目录"
    else
      mkdir -p "$target_dir"
    fi
  fi

  local count=0
  for skill_dir in "$SHARED_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_name; skill_name="$(basename "$skill_dir")"
    [[ "$skill_name" == _* ]] && continue

    if [ ! -f "$skill_dir/SKILL.md" ]; then
      echo "  ⏭️  $skill_name (缺少 SKILL.md)"
      continue
    fi

    local link="$target_dir/$skill_name"

    # 已经是指向同一位置的链接: 幂等跳过（容忍结尾斜杠差异）
    if [ -L "$link" ]; then
      local cur; cur="$(readlink "$link")"
      if [ "${cur%/}" = "${skill_dir%/}" ]; then
        echo "  ✅ $skill_name (已链接)"
        count=$((count + 1))
        continue
      fi
    fi

    # 目标是真实目录（非链接）: 默认拒绝，避免删掉本地独有内容
    if [ -d "$link" ] && [ ! -L "$link" ]; then
      if [ "$FORCE" = 1 ]; then
        echo "  ⚠️  $skill_name 目标是真实目录，--force 覆盖"
        [ "$DRY_RUN" = 0 ] && rm -rf "$link"
      else
        echo "  🛑 $skill_name 目标已存在真实目录，跳过（确认可删后用 --force）"
        skipped_total=$((skipped_total + 1))
        continue
      fi
    fi

    if [ "$DRY_RUN" = 1 ]; then
      echo "  [dry-run] 链接 $skill_name"
    else
      rm -rf "$link"
      ln -s "${skill_dir%/}" "$link"
    fi
    echo "  ✅ $skill_name"
    count=$((count + 1))
  done
  echo "  共 $count 个 skills"
  echo ""
}

for entry in "${TARGETS[@]}"; do
  target_dir=""; tool_name=""; mode=""
  IFS='|' read -r target_dir tool_name mode <<< "$entry"
  sync_target "$target_dir" "$tool_name" "${mode:-}"
done

echo "✅ 同步完成!"
[ "$DRY_RUN" = 1 ] && echo "(以上为 dry-run 模式，未实际执行)"
if [ "$skipped_total" -gt 0 ]; then
  echo ""
  echo "⚠️  有 $skipped_total 处因目标是真实目录被跳过。"
  echo "   先确认那些目录的内容已并入 ${SHARED_DIR} ，再用 --force 重跑。"
fi
