# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md', encoding='utf-8') as f:
    lines = f.readlines()
for target in [181, 185, 189, 4847, 4855, 4867, 4897, 4923, 4925, 4935, 5005, 5015]:
    for j in range(max(0, target-4), min(len(lines), target+3)):
        print(f'{j+1}: {lines[j].rstrip()[:90]}')
    print('---')
