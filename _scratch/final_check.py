# -*- coding: utf-8 -*-
"""最终收尾：结尾分页符清理 + 综合验证"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()

# 1. 删除文件结尾的孤立分页符
text = re.sub(r'\s*<div style="page-break-after: always;"></div>\s*$', '\n', text)
# 2. 空行规范
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.rstrip('\n') + '\n'

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

# ===== 综合验证 =====
with io.open(DST, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
issues = []

# 特殊字符残留
for ch, name in [('\u2011', 'U+2011'), ('\u2010', 'U+2010'), ('\u202f', 'U+202F'), ('\u2003', 'U+2003'),
                 ('\u25fc', '◼'), ('\u274c', '❌'), ('\u26a0', '⚠'), ('\u2757', '❗'), ('\ufe0f', 'FE0F'),
                 ('\ufffd', 'REPLACEMENT'), ('%E2%80%91', 'URL2011')]:
    c = text.count(ch)
    if c:
        issues.append(f'特殊字符 {name}: {c}')

# 中文后半角标点
for ch in [',', ':', ';', '?']:
    n = len(re.findall(r'[\u4e00-\u9fff]' + re.escape(ch), text))
    if n:
        issues.append(f'中文后{ch!r}: {n}')

# 双连字符（非---）
bad_dd = 0
in_block = in_code = False
for l in lines:
    s = l.strip()
    if s.startswith('```'):
        in_code = not in_code
        continue
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    if s.startswith('$$'):
        in_block = not in_block
        continue
    if '--' in l and '---' not in l and not (in_block or in_code or s.startswith('|')):
        bad_dd += 1
if bad_dd:
    issues.append(f'非分隔线--: {bad_dd}')

# $$ 配对
in_block = False
for l in lines:
    s = l.strip()
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    if s.startswith('$$'):
        in_block = not in_block
if in_block:
    issues.append('$$ 未配对')

# 表格内部空行
prev = None
tbl_gap = 0
for i, l in enumerate(lines):
    if not l.strip():
        continue
    s = l.strip()
    if s.startswith('|'):
        if prev is not None and prev[0] == 'BLANK':
            tbl_gap += 1
        prev = ('TBL', i)
    else:
        prev = ('TXT', i)

# 中文间多余空格
gap = len(re.findall(r'[\u4e00-\u9fff] [\u4e00-\u9fff]', text))

print('=== 最终综合验证 ===')
if issues:
    for it in issues:
        print('问题:', it)
else:
    print('特殊字符/标点/连字符/公式配对: 全部通过')
print('中文间多余空格:', gap)
print('总行数:', len(lines), '总字符:', len(text))
print('文件大小: %.1f KB' % (len(text.encode('utf-8')) / 1024))
