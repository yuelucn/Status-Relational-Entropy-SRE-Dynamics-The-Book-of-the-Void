# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines, 1):
    if '\\(' in l or '\\)' in l:
        print(i, repr(l.strip()[:160]))
