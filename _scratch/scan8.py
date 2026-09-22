# -*- coding: utf-8 -*-
"""扫描第三轮问题：公式内全角括号、分隔线损坏、LaTeX星号、编号"""
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()

# 1. 公式内全角括号（$...（...）...$）
print('=== 1. 公式内全角括号 ===')
n1 = 0
for i, l in enumerate(lines, 1):
    if re.search(r'\$[^$\n]*[（（][^$\n]*\$', l):
        n1 += 1
        if n1 <= 8:
            print(i, repr(l.strip()[:120]))
print('数量:', n1)

# 2. 被破坏的分隔线
print('=== 2. 损坏分隔线 ===')
n2 = 0
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s in ('——-', '-——', '—-—', '——–', '————', '——') and len(s) <= 6:
        n2 += 1
print('数量:', n2)
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s in ('——-', '-——', '—-—') and n2 <= 10:
        print(i, repr(s))

# 3. LaTeX 星号污染
print('=== 3. LaTeX星号模式 ===')
n3 = 0
pat = re.compile(r'\\mathcal\{[A-Za-z]+\}\*\{[^}]*\}')
for i, l in enumerate(lines, 1):
    if pat.search(l) or re.search(r'\\mathcal\{[A-Za-z]+\}\*[a-zA-Z]', l):
        n3 += 1
        if n3 <= 8:
            print(i, repr(l.strip()[:130]))
print('数量:', n3)

# 4. 损坏标题
print('=== 4. ##-. 标题 ===')
for i, l in enumerate(lines, 1):
    if '##-.' in l or '## -.' in l:
        print(i, repr(l.strip()[:80]))
