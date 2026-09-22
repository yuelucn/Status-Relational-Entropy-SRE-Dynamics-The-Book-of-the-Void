# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    text = f.read()
for m in re.finditer(r'.{0,40}\\(.{0,100}\\).{0,20}', text):
    print(repr(m.group(0)))
    print('---')
