# -*- coding: utf-8 -*-
"""检查第四轮问题"""
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

print('=== 1. **作者**: 等加粗冒号 ===')
for i, l in enumerate(lines, 1):
    if re.search(r'\*\*[^*]+\*\*:', l):
        print(i, repr(l.strip()[:80]))

print()
print('=== 2. 含% E2%80%91的URL ===')
n = text.count('%E2%80%91')
print('数量:', n)
for m in list(re.finditer(r'.{30}%E2%80%91.{30}', text))[:3]:
    print(repr(m.group(0)))

print()
print('=== 3. 残留 --（非公式/表格/代码）===')
in_block = in_code = False
left = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('```'):
        in_code = not in_code
        continue
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '--' in l and not (in_block or in_code or s.startswith('|')):
        left.append((i, l.strip()[:110]))
print('数量:', len(left))
for e in left[:12]:
    print(e)

print()
print('=== 4. 含公式的半角括号（非表格/公式块）===')
in_block = False
n4 = 0
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if in_block or s.startswith('|'):
        continue
    for m in re.finditer(r'[\u4e00-\u9fff0-9]\(\$[^()]{1,120}\$\)', l):
        n4 += 1
        if n4 <= 10:
            print(i, repr(m.group(0)[:100]))
print('数量:', n4)

print()
print('=== 5. 全角句号后双空格 ===')
n5 = 0
for i, l in enumerate(lines, 1):
    if re.search(r'[。；：、）】」][ \t][ \t]+', l):
        n5 += 1
print('行数:', n5)
for i, l in enumerate(lines, 1):
    if re.search(r'[。；：、）】」][ \t][ \t]+', l) and n5 <= 8:
        m = re.search(r'[。；：、）】」][ \t][ \t]+', l)
        print(i, repr(l[max(0, m.start()-12):m.end()+12]))
