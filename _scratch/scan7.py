# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
in_block = False
in_code = False
left = 0
examples = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('```'):
        in_code = not in_code
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '--' in l:
        if not (in_block or in_code or s.startswith('|')):
            left += 1
            if len(examples) < 15:
                examples.append((i, l.strip()[:110]))
print('非公式/表格/代码中的--:', left)
for e in examples:
    print(e)
