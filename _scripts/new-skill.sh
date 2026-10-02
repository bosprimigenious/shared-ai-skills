#!/usr/bin/env bash
# new-skill.sh - 从 _templates/skill-template 创建一个新 skill
# 用法: ./new-skill.sh <skill-name> [description]
# 只生成 SKILL.md（唯一事实来源），AGENTS.md / CLAUDE.md 由 sync-formats.sh 派生。
set -euo pipefail

SHARED_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$SHARED_DIR/_templates/skill-template"

if [ $# -lt 1 ]; then
  echo "用法: $0 <skill-name> [description]"
  echo "示例: $0 code-review 'Review code for quality and best practices'"
  exit 1
fi

SKILL_NAME="$1"
DESCRIPTION="${2:-TODO: Add description for $SKILL_NAME}"
SKILL_DIR="$SHARED_DIR/$SKILL_NAME"

if ! echo "$SKILL_NAME" | grep -qE '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'; then
  echo "错误: skill 名称只能包含小写字母、数字和连字符" >&2
  exit 1
fi
if [ -d "$SKILL_DIR" ]; then
  echo "错误: skill '$SKILL_NAME' 已存在于 ${SKILL_DIR}" >&2
  exit 1
fi
if [ ! -f "$TEMPLATE/SKILL.md" ]; then
  echo "错误: 模板缺失 ${TEMPLATE}/SKILL.md" >&2
  exit 1
fi

# 标题: my-skill -> My Skill
SKILL_TITLE="$(echo "$SKILL_NAME" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"

cp -R "$TEMPLATE" "$SKILL_DIR"

# 占位符替换（用 python 避免 sed 的转义/分隔符问题）
python3 - "$SKILL_DIR/SKILL.md" "$SKILL_NAME" "$DESCRIPTION" "$SKILL_TITLE" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
name, desc, title = sys.argv[2], sys.argv[3], sys.argv[4]
t = p.read_text(encoding="utf-8")
t = (t.replace("__SKILL_NAME__", name)
      .replace("__DESCRIPTION__", desc)
      .replace("__SKILL_TITLE__", title))
p.write_text(t, encoding="utf-8")
PY

# 派生另外两种格式
"$SHARED_DIR/_scripts/sync-formats.sh" "$SKILL_NAME" >/dev/null

echo "✅ 已创建 skill: ${SKILL_DIR}"
echo ""
echo "  SKILL.md    <- 编辑这个（唯一事实来源）"
echo "  AGENTS.md   <- 自动派生，勿手改"
echo "  CLAUDE.md   <- 自动派生，勿手改"
echo ""
echo "下一步:"
echo "  1. 编辑 ${SKILL_DIR}/SKILL.md"
echo "  2. 运行 _scripts/sync-formats.sh ${SKILL_NAME}   # 重新派生"
echo "  3. 运行 _scripts/build.sh                        # 链接到四个工具"
