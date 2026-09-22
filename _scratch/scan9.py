# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines, 1):
    if '##-' in l:
        lo = max(0, i-6)
        hi = min(len(lines), i+6)
        print(f'===== 行 {i} 上下文 =====')
        for j in range(lo, hi):
            print(f'{j}: {lines[j].rstrip()[:90]}')
        print()
