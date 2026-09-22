# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()

# 模拟 normalize2 的 in_block 状态，检查 4879 行是否被跳过
in_block = False
hits = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '--' in l and '---' not in l and not in_block and not s.startswith('|'):
        hits.append((i, 'OK', l.strip()[:60]))
    elif '--' in l and '---' not in l and in_block:
        hits.append((i, 'IN_BLOCK', l.strip()[:60]))

print('含--且非---的行（按状态分类）:')
for h in hits:
    print(h)

# 检查 4879 行前后 $$ 分布
print()
print('4850-4885 行的 $$ 状态:')
in_block = False
for i, l in enumerate(lines[4849:4885], 4850):
    s = l.strip()
    if s.startswith('$$'):
        in_block = not in_block
        print(i, '$$', 'OPEN' if in_block else 'CLOSE', repr(s[:40]))
    elif '$$' in s:
        print(i, 'has $$', repr(s[:60]))
