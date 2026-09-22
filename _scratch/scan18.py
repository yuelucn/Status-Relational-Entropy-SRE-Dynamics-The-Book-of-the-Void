# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
in_block = False
open_at = None
total = 0
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    if s.startswith('$$'):
        total += 1
        if not in_block:
            in_block = True
            open_at = i
        else:
            in_block = False
print('总块标记:', total, '配对正常:', not in_block)
if in_block:
    print('未闭合起始行:', open_at)
