# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)

# 定位所有含 \[ 或 \] 的行
print('含 \[ 或 \] 的行:')
for i, l in enumerate(lines, 1):
    if '\\[' in l or '\\]' in l:
        print(i, repr(l.strip()[:70]))
