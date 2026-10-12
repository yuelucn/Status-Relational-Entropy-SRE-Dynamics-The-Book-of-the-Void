#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 math-graph 的算子 13-18 规范（中/英）同步为书籍第三部分章节。

书籍约定：
  - 章内只保留一个 H1（标题）；作者署名行剔除；版本行保留；
  - 不写入 BOM，行尾 LF，与既有章节一致。
"""
import os
import re

SRC = r"c:\mywork\math-graph"
DST = r"c:\mywork\SRE-Dynamics\3-Mathematical_Support"

JOBS = [
    ("算子-13_18_谱形方程求解算子组_严格数学规范.md", "Operator_13_18_1.3_C.md", "作者"),
    ("Operator-13_18_Strict-Mathematical-Specification_EN.md", "Operator_13_18_1.3_E.md", "Author"),
]


def count_h1(text: str) -> int:
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


def clean(text: str, author_key: str) -> str:
    lines = text.split("\n")
    kept = [ln for ln in lines if not re.match(r"^\*\*%s\*\*\s*[:：]" % author_key, ln)]
    return "\n".join(kept)


def main():
    for src_name, dst_name, key in JOBS:
        with open(os.path.join(SRC, src_name), "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        text = clean(text, key)
        n = count_h1(text)
        assert n == 1, f"{dst_name}: H1 count = {n}"
        out_path = os.path.join(DST, dst_name)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"OK  {dst_name}  lines={len(text.splitlines())}  H1={n}")


if __name__ == "__main__":
    main()