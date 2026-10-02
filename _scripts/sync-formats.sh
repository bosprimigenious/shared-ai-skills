#!/usr/bin/env bash
# sync-formats.sh - 从 SKILL.md 派生 AGENTS.md 和 CLAUDE.md
# SKILL.md 是唯一事实来源（YAML frontmatter 格式）；另两份是引用块格式的自动产物。
# 用法: ./sync-formats.sh [skill-name...]   不传参数则处理全部 skill
set -euo pipefail

SHARED_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 从 SKILL.md 生成引用块格式：把 YAML frontmatter 的 name/description
# 转成 "# Title" + "> description"，正文原样保留（去掉重复的一级标题）。
derive() {
  local skill_dir="$1"
  local out="$2"
  local src="$skill_dir/SKILL.md"

  python3 - "$src" "$out" <<'PY'
import re, sys, pathlib

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
text = src.read_text(encoding="utf-8")

m = re.match(r"\A---\n(.*?)\n---\n?", text, re.DOTALL)
if not m:
    sys.exit(f"{src}: 缺少 YAML frontmatter")
fm, body = m.group(1), text[m.end():]

def field(key):
    # 单行标量（可含冒号/引号）、>/>-/>> 折叠、|/|-/|+ 字面；缺失返回空。
    mm = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.MULTILINE)
    if not mm:
        return ""
    head = mm.group(1).strip()
    if head and head[0] not in "|>":
        return head.strip("'\"")
    rest = fm[mm.end():]
    # $ 停在指示符行末、换行之前；吃掉这个换行，避免 | / > 块多出一段空行
    if rest.startswith("\n"):
        rest = rest[1:]
    lines = []
    for ln in rest.splitlines():
        if not ln.strip():
            lines.append("")
            continue
        if not ln.startswith((" ", "\t")):
            break
        lines.append(ln.strip())
    if head.startswith(">"):
        # 折叠：空行分段，段内空格连接
        out, buf = [], []
        for ln in lines:
            if ln:
                buf.append(ln)
            elif buf:
                out.append(" ".join(buf))
                buf = []
        if buf:
            out.append(" ".join(buf))
        return "\n\n".join(out)
    return "\n".join(lines)

name = field("name")
desc = field("description")
if not name:
    sys.exit(f"{src}: frontmatter 缺少 name")

body = body.lstrip("\n")
# 正文若以一级标题开头，用它当标题并从正文移除，避免重复
hm = re.match(r"# (.+?)\n+", body)
if hm:
    title, body = hm.group(1).strip(), body[hm.end():]
else:
    title = name.replace("-", " ").title()

parts = [f"# {title}", ""]
if desc:
    parts += ["\n".join(("> " + ln) if ln else ">" for ln in desc.split("\n")), ""]
parts.append(body.rstrip() + "\n")
out.write_text("\n".join(parts), encoding="utf-8")
PY
}

targets=()
if [ $# -eq 0 ]; then
  for d in "$SHARED_DIR"/*/; do
    n="$(basename "$d")"
    [[ "$n" == _* ]] && continue
    targets+=("$n")
  done
  # 裸跑也更新 _projects/*/，避免改了专用 skill 却静默陈旧
  if [ -d "$SHARED_DIR/_projects" ]; then
    for d in "$SHARED_DIR/_projects"/*/; do
      [ -d "$d" ] || continue
      targets+=("_projects/$(basename "$d")")
    done
  fi
else
  targets=("$@")
fi

echo "🔄 从 SKILL.md 派生 AGENTS.md / CLAUDE.md"
echo "========================================"
for n in "${targets[@]}"; do
  d="$SHARED_DIR/$n"
  if [ ! -f "$d/SKILL.md" ]; then
    echo "  ⏭️  $n (无 SKILL.md)"
    continue
  fi
  derive "$d" "$d/AGENTS.md"
  cp "$d/AGENTS.md" "$d/CLAUDE.md"
  echo "  ✅ $n"
done
echo ""
echo "完成。SKILL.md 是唯一事实来源，改完它重跑本脚本即可。"
