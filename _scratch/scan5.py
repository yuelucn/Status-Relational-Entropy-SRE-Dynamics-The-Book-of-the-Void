# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
# 查找公式块内或含 $ 的行中出现的 ——
bad = []
in_block = False
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '——' in l:
        if in_block or '$' in l:
            bad.append((i, in_block, l.strip()[:140]))
print('公式相关——数量:', len(bad))
for b in bad[:30]:
    print(b)
