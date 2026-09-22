# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
bad = 0
in_block = False
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '——' in l:
        if in_block or (s.startswith('|')):
            bad += 1
            print('公式/表格内——:', i, repr(l[:120]))
print('公式/表格内——数量:', bad)
# 列出所有 —— 的上下文（样本）
import re
cnt = 0
for i, l in enumerate(lines, 1):
    if '——' in l and not l.strip().startswith('$$'):
        cnt += 1
        if cnt <= 12:
            m = re.search(r'.{15}——.{15}', l)
            if m:
                print(i, repr(m.group(0)))
print('总——行数:', cnt)
