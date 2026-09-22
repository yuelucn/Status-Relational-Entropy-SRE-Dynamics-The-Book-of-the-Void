# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)

print('=== 1. 雅共比 ===')
for i, l in enumerate(lines, 1):
    if '雅共比' in l:
        print(i, repr(l.strip()[:90]))

print()
print('=== 2. 常数常数 ===')
for i, l in enumerate(lines, 1):
    if '常数常数' in l:
        print(i, repr(l.strip()[:90]))

print()
print('=== 3. 缺书名号 ===')
for i, l in enumerate(lines, 1):
    if '《SRE通用图算子流水线与发布路线图的发布计划' in l:
        print(i, repr(l.strip()[:90]))

print()
print('=== 4. 文档头作者/版本行 ===')
for i, l in enumerate(lines, 1):
    s = l.strip()
    if re.match(r'^(作者|版本| 版本)\s*[：:]\s*\S', s) and len(s) < 40:
        print(i, repr(l))

print()
print('=== 5. \[ 和 \] 数量 ===')
print('\\[ :', text.count('\\['), ' \\] :', text.count('\\]'))
# 找含 \[ 的行（非公式内）
for i, l in enumerate(lines, 1):
    if '\\[' in l:
        if i <= 3:
            print(i, repr(l.strip()[:60]))
