#!/usr/bin/env python3
import os
import re
import sys

def strip_fenced_code(content: str) -> str:
    """把 ``` 或 ~~~ 围栏代码块的内容替换为空行。

    章节里经常出现 `# Step 1: ...` 这类脚本注释，若不剔除会被朴素正则
    误判成 H1，触发"Multiple H1"假警报。围栏行本身一并置空，
    保证剩余文本的行号与原文件一一对应。
    """
    out = []
    fence_char = None   # 当前围栏字符（` 或 ~）
    fence_len = 0
    for line in content.split("\n"):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_char is None:
            if m:
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                out.append("")
            else:
                out.append(line)
        else:
            if m and m.group(1)[0] == fence_char and len(m.group(1)) >= fence_len:
                fence_char = None
            out.append("")
    return "\n".join(out)


def check_markdown_heading_warnings(filepath: str):
    """Scan md, output heading risk warnings, auto‑strip UTF‑8 BOM, do not modify source file"""
    # 二进制读取，内存剥离BOM，不改动磁盘文件
    with open(filepath, "rb") as f:
        raw_bytes = f.read()
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        raw_bytes = raw_bytes[3:]
    content = raw_bytes.decode("utf-8")

    # 统计 H1 时排除代码围栏内的内容
    h1_pattern = re.compile(r"^#\s+", re.MULTILINE)
    h1_hits = h1_pattern.findall(strip_fenced_code(content))
    cnt = len(h1_hits)
    warns = []
    if cnt == 0:
        warns.append(f"⚠️ {os.path.basename(filepath)} : No H1 heading (#) found in file")
    if cnt > 1:
        warns.append(f"⚠️ {os.path.basename(filepath)} : Multiple H1 (#) detected, one chapter should have exactly one H1!")
    for w in warns:
        print(w)
    return warns

def main():
    order_list_file = "file_order_E.txt"
    out_combined = "combined_E.md"

    md_inputs = []
    with open(order_list_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            md_inputs.append(line)

    missing = []
    for fn in md_inputs:
        if not os.path.exists(fn):
            missing.append(fn)
        else:
            check_markdown_heading_warnings(fn)
    if missing:
        print("\n❌ Missing files:")
        for f in missing:
            print(f"   {f}")
        sys.exit(1)

    print(f"\n✅ Merge {len(md_inputs)} chapters → {out_combined}")

    combined_parts = []

    # 1.作者序（第一个文件）
    preface_fn = md_inputs[0]
    with open(preface_fn, "rb") as f:
        raw_bytes = f.read()
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        raw_bytes = raw_bytes[3:]
    preface_text = raw_bytes.decode("utf-8")
    combined_parts.append(preface_text)
    combined_parts.append('\n\n<div style="page-break-after: always;"></div>\n\n')

    # 2.手动生成目录（跳过作者序）
    body_files = md_inputs[1:]
    toc_lines = ["# Table of content\n"]
    for fn in body_files:
        with open(fn, "rb") as f:
            raw_bytes = f.read()
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            raw_bytes = raw_bytes[3:]
        content = raw_bytes.decode("utf-8")
        h1_pattern = re.compile(r"^#\s+(.+)$", re.MULTILINE)
        h1_list = h1_pattern.findall(content)
        if len(h1_list)>=1:
            title = h1_list[0].strip()
            anchor = re.sub(r"\s+","-",title)
            toc_lines.append(f"- [{title}](#{anchor})\n")
    toc_block = "".join(toc_lines)
    combined_parts.append(toc_block)
    combined_parts.append('\n\n<div style="page-break-after: always;"></div>\n\n')

    # 3.拼接全部正文章节，修复变量 total → total_body
    total_body = len(body_files)
    for idx, fn in enumerate(body_files):
        with open(fn, "rb") as f:
            raw_bytes = f.read()
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            raw_bytes = raw_bytes[3:]
        text = raw_bytes.decode("utf-8")
        combined_parts.append(text)
        # 修复此处变量名错误 total_body
        if idx != total_body - 1:
            combined_parts.append('\n\n<div style="page-break-after: always;"></div>\n\n')

    full_text = "".join(combined_parts)
    with open(out_combined, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"\n🎉 Finished! Open {out_combined} in Typora → File → Export → PDF")
    print("💡说明：")
    print(" 1. 作者序原样输出，不会出现在目录中")
    print(" 2. 脚本手动生成#目录，只包含正文章节，支持点击跳转")
    print(" 3. 作者序→换页→目录页→换页→正文，每个md章节结束自动换页")
    print(" ⚠️限制：Typora导出PDF，手动生成目录依旧没有页码，只能超链接跳转。")

if __name__ == "__main__":
    main()
