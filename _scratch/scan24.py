# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md', encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

print('=== 钢性 ===')
for i, l in enumerate(lines, 1):
    if '钢性' in l:
        print(i, repr(l.strip()[:80]))
