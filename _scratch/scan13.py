# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)

print('4879:', repr(lines[4878][:70]))

# 1. 非分隔线残留 --
in_block = False
bad = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '--' in l and '---' not in l and not in_block and not s.startswith('|'):
        bad.append((i, l.strip()[:90]))
print('非分隔线残留--:', len(bad), bad[:5])

# 2. $$ 块配对
in_block = False
unclosed_start = None
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    if s.startswith('$$'):
        if not in_block:
            in_block = True
            unclosed_start = i
        else:
            in_block = False
print('$$ 块配对正常:', not in_block)

# 3. 公式内全角括号残留
n = 0
for i, l in enumerate(lines, 1):
    if re.search(r'\$[^$\n]*[（][^$\n]*\$', l):
        n += 1
        if n <= 5:
            m = re.search(r'\$[^$\n]*[（][^$\n]*\$', l)
            print('公式内全角括号:', i, repr(l.strip()[:90]))
print('公式内全角括号行数:', n)

# 4. 特殊符号残留
for ch, name in [('\u2011', 'U+2011'), ('\u2010', 'U+2010'), ('\u202f', 'U+202F'), ('\u2003', 'U+2003'), ('◼', '◼'), ('❌', '❌'), ('⚠', '⚠'), ('❗', '❗'), ('\ufe0f', 'FE0F')]:
    c = text.count(ch)
    if c:
        print(f'{name} 残留: {c}')
print('特殊符号检查完成')
