# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)

print('=== 中文后半角逗号 ===')
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'[\u4e00-\u9fff],', l):
        print(i, repr(l[max(0, m.start()-20):m.end()+20]))

print()
print('=== 中文间空格 ===')
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'[\u4e00-\u9fff] [\u4e00-\u9fff]', l):
        print(i, repr(l[max(0, m.start()-15):m.end()+15]))
