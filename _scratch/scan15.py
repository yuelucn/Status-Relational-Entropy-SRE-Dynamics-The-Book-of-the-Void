# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)

print('=== **作者**: 半角冒号 ===')
n = 0
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'\*\*[^*\n]+\*\*:', l):
        n += 1
        if n <= 10:
            print(i, repr(m.group(0)))
print('数量:', n)

print()
print('=== **版本: ** 冒号在加粗内 ===')
n2 = 0
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'\*\*[^*\n]*: [^*\n]*\*\*', l):
        n2 += 1
        if n2 <= 8:
            print(i, repr(l.strip()[:80]))
print('数量:', n2)

print()
print('=== 含公式半角括号 ===')
n3 = 0
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'[\u4e00-\u9fff0-9]\(\$[^$]{1,120}\$\)', l):
        n3 += 1
        if n3 <= 8:
            print(i, repr(m.group(0)[:90]))
print('数量:', n3)
