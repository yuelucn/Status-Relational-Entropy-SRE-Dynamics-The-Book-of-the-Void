#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 math-graph 的算子 7/8/9/10/19 规范同步为书籍第三部分章节。

书籍约定：
  - 章内只保留一个 H1（标题）；作者署名行剔除；版本行保留；
  - 全书统一「全部开源」：源文件里的闭源/商业核心表述一律改写为开源；
  - 不写入 BOM，行尾 LF，与既有章节一致。
"""
import os
import re

SRC = r"c:\mywork\math-graph"
DST = r"c:\mywork\SRE-Dynamics\3-Mathematical_Support"

# (源文件, 目标文件, 署名键)
JOBS = [
    ("Operator_7_C.md",  "Operator_7_1.2_C.md",  "作者"),
    ("Operator_7_E.md",  "Operator_7_1.2_E.md",  "Author"),
    ("Operator_8_C.md",  "Operator_8_1.0_C.md",  "作者"),
    ("Operator_8_E.md",  "Operator_8_1.0_E.md",  "Author"),
    ("Operator_9_C.md",  "Operator_9_1.0_C.md",  "作者"),
    ("Operator_9_E.md",  "Operator_9_1.0_E.md",  "Author"),
    ("Operator_10_C.md", "Operator_10_1.0_C.md", "作者"),
    ("Operator_10_E.md", "Operator_10_1.0_E.md", "Author"),
    ("Operator_19_C.md", "Operator_19_1.0_C.md", "作者"),
]

# 闭源 -> 开源 的统一改写（按出现顺序逐条替换）
REWRITES = [
    # 版本行
    ("1.0 (2026年7月·封闭式商业核心专属规范)", "1.0 (2026年7月·开源规范)"),
    ("1.0 (July 2026 · Proprietary / Closed Core Subsystem Specification)",
     "1.0 (July 2026 · Open-Source Specification)"),
    # 摘要正文
    ("核心防御与闭源子系统", "核心防御与开源子系统"),
    ("首个核心商业级黑盒/闭源算子", "首个核心开源算子"),
    # 算子 19 §9 层级定位
    ("商业核心层（7–10）", "开源核心层（7–10）"),
]


def count_h1(text: str) -> int:
    """统计 H1（排除围栏代码块内的 # 注释）。"""
    fence = None
    out = []
    for line in text.split("\n"):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is None:
            if m:
                fence = m.group(1)[0]
                out.append("")
            else:
                out.append(line)
        else:
            if m and m.group(1)[0] == fence:
                fence = None
            out.append("")
    return len(re.findall(r"^#\s+", "\n".join(out), re.M))


def read_text(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def clean(text: str, author_key: str) -> str:
    lines = text.split("\n")
    kept = [ln for ln in lines if not re.match(r"^\*\*%s\*\*\s*[:：]" % author_key, ln)]
    return "\n".join(kept)


def apply_rewrites(text: str, dst_name: str) -> str:
    for old, new in REWRITES:
        if old in text:
            text = text.replace(old, new)
    # 兜底检查：不应再出现任何闭源口径
    left = re.findall(r"闭源|封闭式|商业核心|商业级|专属规范|Proprietary|Closed Core", text)
    assert not left, f"{dst_name}: 仍残留闭源口径 {set(left)}"
    return text


def main():
    for src_name, dst_name, key in JOBS:
        text = read_text(os.path.join(SRC, src_name))
        text = clean(text, key)
        text = apply_rewrites(text, dst_name)
        n = count_h1(text)
        assert n == 1, f"{dst_name}: H1 count = {n}"
        out_path = os.path.join(DST, dst_name)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"OK  {dst_name}  lines={len(text.splitlines())}  H1={n}")


if __name__ == "__main__":
    main()