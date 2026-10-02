#!/usr/bin/env bash
# install.sh - 在当前项目中安装共享 skills（项目级，各 harness 都能读）
# 用法: cd /your/project && ~/shared-ai-skills/_scripts/install.sh [skill-name...]
# 不传参数则安装所有 skills
set -euo pipefail

SHARED_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$(pwd)"

# 项目级 skills 目录。各 harness 都读 <skill>/SKILL.md。
# skill-name 可以是 _projects/<name>；链接名取 basename，避免嵌套一层后扫不到。
PROJECT_TARGETS=(
  ".qoder/skills|Qoder"
  ".claude/skills|Claude Code"
  ".codex/skills|Codex"
  ".cursor/skills|Cursor"
  ".grok/skills|Grok"
  ".agents/skills|Agents"
)

echo "📦 安装共享 Skills 到项目"
echo "=========================="
echo "项目目录: $PROJECT_DIR"
echo ""

install_skill() {
  local skill_name="$1"
  local skill_dir="$SHARED_DIR/$skill_name"

  if [ ! -d "$skill_dir" ]; then
    echo "  ❌ skill '$skill_name' 不存在"
    return 1
  fi
  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "  ⏭️  $skill_name (缺少 SKILL.md)"
    return 0
  fi

  local tools=()
  local link_name; link_name="$(basename "$skill_name")"
  for entry in "${PROJECT_TARGETS[@]}"; do
    local subdir="${entry%%|*}" tool="${entry##*|}"
    local link="$PROJECT_DIR/$subdir/$link_name"

    # 目标是真实目录（非链接）时跳过，避免删掉项目里独有的同名 skill
    if [ -d "$link" ] && [ ! -L "$link" ]; then
      echo "  🛑 $skill_name @ $subdir 已存在真实目录，跳过"
      continue
    fi

    mkdir -p "$PROJECT_DIR/$subdir"
    rm -rf "$link"
    ln -s "$skill_dir" "$link"
    tools+=("$tool")
  done

  if [ ${#tools[@]} -gt 0 ]; then
    local joined; joined="$(printf '%s / ' "${tools[@]}")"
    echo "  ✅ $skill_name (${joined% / })"
  fi
}

if [ $# -eq 0 ]; then
  for skill_dir in "$SHARED_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    [[ "$skill_name" == _* ]] && continue
    install_skill "$skill_name"
  done
else
  for skill_name in "$@"; do
    install_skill "$skill_name"
  done
fi

echo ""
echo "✅ 安装完成!"
echo ""
echo "项目目录结构:"
echo "  .qoder/skills/   -> Qoder 读取"
echo "  .claude/skills/  -> Claude Code 读取"
echo "  .codex/skills/   -> Codex 读取"
echo "  .cursor/skills/  -> Cursor 读取"
echo "  .grok/skills/    -> Grok 读取"
echo "  .agents/skills/  -> Grok / DeepSeek 读取"
echo ""
echo "提示: 这些是指向 $SHARED_DIR 的符号链接，"
echo "      如果项目要提交给别人，记得把它们加进 .gitignore。"
