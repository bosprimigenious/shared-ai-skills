#!/usr/bin/env python3
"""Fail-closed checks for the classroom-note framework mind map."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field

MAX_DEPTH = 3  # root + two levels
MIN_NODES = 6
MAX_NODES = 16
MAX_CHILDREN = 4
MAX_CHARS = 12
MAX_EN_WORDS = 6
FORBIDDEN_CHARS = set("()[]{}#;\"")
DETAIL_PATTERNS = (
    re.compile(r"[。；]"),
    re.compile(r"(是指|即是|例如|比如|【)"),
)

ROOT_SHAPES = (
    re.compile(r"^\(\((.+)\)\)$"),
    re.compile(r"^\[(.+)\]$"),
    re.compile(r"^\((.+)\)$"),
    re.compile(r"^\{\{(.+)\}\}$"),
)


@dataclass
class Node:
    label: str
    depth: int
    children: list["Node"] = field(default_factory=list)


def strip_shape(label: str) -> str:
    text = label.strip()
    if re.match(r"(?i)^root\b", text):
        text = text[4:].strip()
    for pat in ROOT_SHAPES:
        m = pat.match(text)
        if m:
            return m.group(1).strip()
    return text


def parse_mindmap(src: str) -> Node | None:
    m = re.search(r"```mermaid\s*\nmindmap\n(.*?)```", src, re.DOTALL | re.IGNORECASE)
    if not m:
        return None
    lines = []
    for raw in m.group(1).splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))
    if not lines:
        return None
    min_indent = min(i for i, _ in lines)
    stack: list[Node] = []
    root: Node | None = None
    for indent, label in lines:
        depth = (indent - min_indent) // 2
        node = Node(strip_shape(label), depth)
        while stack and stack[-1].depth >= depth:
            stack.pop()
        if not stack:
            root = node
        else:
            stack[-1].children.append(node)
        stack.append(node)
    return root


def parse_list_block(src: str) -> Node | None:
    """Parse the first nested markdown list after a 知识框架图 heading."""
    heading = re.search(r"^#{2,4}\s+.*知识框架图.*$", src, re.MULTILINE)
    region = src[heading.end() :] if heading else src
    nxt = re.search(r"^#{2,4}\s+", region, re.MULTILINE)
    if heading and nxt:
        region = region[: nxt.start()]
    region = re.sub(r"```.*?```", "", region, count=1, flags=re.DOTALL)
    stop = re.search(r"^跨枝关系", region, re.MULTILINE)
    if stop:
        region = region[: stop.start()]
    lines = []
    for raw in region.splitlines():
        m = re.match(r"^(\s*)[-*+]\s+(.+)$", raw)
        if not m:
            continue
        indent = len(m.group(1).replace("\t", "    "))
        lines.append((indent, m.group(2).strip()))
    if not lines:
        return None
    min_indent = min(i for i, _ in lines)
    # Synthetic root so the list's top items are level-1 modules.
    root = Node("ROOT", 0)
    stack = [root]
    for indent, label in lines:
        depth = 1 + (indent - min_indent) // 2
        node = Node(strip_shape(label), depth)
        while stack and stack[-1].depth >= depth:
            stack.pop()
        stack[-1].children.append(node)
        stack.append(node)
    return root


def walk(node: Node) -> list[Node]:
    out = [node]
    for child in node.children:
        out.extend(walk(child))
    return out


def max_depth(node: Node) -> int:
    if not node.children:
        return node.depth
    return max(max_depth(c) for c in node.children)


def labels(node: Node, skip_synthetic: bool = False) -> list[str]:
    nodes = walk(node)
    if skip_synthetic and nodes and nodes[0].label == "ROOT":
        nodes = nodes[1:]
    return [n.label for n in nodes]


def node_too_long(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if re.search(r"[\u4e00-\u9fff]", text):
        return len(compact) > MAX_CHARS
    words = re.findall(r"[A-Za-z0-9\-']+", text)
    return len(words) > MAX_EN_WORDS or len(compact) > 40


def check_tree(root: Node, name: str, skip_synthetic: bool = False) -> list[str]:
    errors: list[str] = []
    nodes = walk(root)
    countable = nodes[1:] if skip_synthetic and nodes and nodes[0].label == "ROOT" else nodes
    depth = max_depth(root) + (0 if not skip_synthetic else 0)
    # For mermaid, depth 0 is root; allowed max is 2.
    # For list, synthetic ROOT at 0, modules at 1, concepts at 2; max_depth should be 2.
    if skip_synthetic:
        if max_depth(root) > 2:
            errors.append(f"{name}: 深度 {max_depth(root)} 超过两层概念")
    else:
        if max_depth(root) > MAX_DEPTH - 1:
            errors.append(f"{name}: 深度 {max_depth(root)} 超过根+两层")
    n = len(countable)
    if n < MIN_NODES:
        errors.append(f"{name}: 节点数 {n} < {MIN_NODES}")
    if n > MAX_NODES:
        errors.append(f"{name}: 节点数 {n} > {MAX_NODES}")
    for node in countable:
        kids = node.children
        if len(kids) > MAX_CHILDREN:
            errors.append(f"{name}: 「{node.label}」有 {len(kids)} 个子枝，上限 {MAX_CHILDREN}")
        if node_too_long(node.label):
            errors.append(f"{name}: 节点过长「{node.label}」")
        if any(ch in node.label for ch in FORBIDDEN_CHARS):
            errors.append(f"{name}: 节点含禁用字符「{node.label}」")
        for pat in DETAIL_PATTERNS:
            if pat.search(node.label):
                errors.append(f"{name}: 节点像细节/定义「{node.label}」")
                break
    return errors


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", strip_shape(text))


def check_note(src: str) -> list[str]:
    errors: list[str] = []
    mmap = parse_mindmap(src)
    lst = parse_list_block(src)
    if mmap is None:
        errors.append("缺少 mermaid mindmap")
    if lst is None:
        errors.append("缺少知识框架图下的缩进列表")
    if mmap is not None:
        errors.extend(check_tree(mmap, "mindmap"))
        root_label = mmap.label
        if not re.search(r"[？?如何为何为什么怎样]", root_label):
            errors.append(f"根节点不是核心问题：「{root_label}」")
    if lst is not None:
        errors.extend(check_tree(lst, "list", skip_synthetic=True))
    if mmap is not None and lst is not None:
        m_labs = [normalize(x) for x in labels(mmap)]
        l_labs = [normalize(x) for x in labels(lst, skip_synthetic=True)]
        # List omits the root question; remaining mermaid labels must match.
        m_rest = m_labs[1:]
        if sorted(m_rest) != sorted(l_labs):
            errors.append(
                "mindmap 与缩进列表节点不一致: "
                f"map={m_rest} list={l_labs}"
            )
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--expect-fail", action="store_true")
    args = ap.parse_args()
    src = open(args.path, encoding="utf-8").read()
    errors = check_note(src)
    failed = bool(errors)
    if args.expect_fail:
        if failed:
            print(f"OK (expected fail): {args.path}")
            for e in errors:
                print(f"  - {e}")
            return 0
        print(f"FAIL: {args.path} 本应违规却通过")
        return 1
    if failed:
        print(f"FAIL: {args.path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
