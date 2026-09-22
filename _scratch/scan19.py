# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()

# 表格空行检查：连续表格行之间出现空行
in_tbl = False
issues = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    is_tbl = s.startswith('|')
    if is_tbl and not in_tbl:
        in_tbl = True
        tbl_start = i
    elif not is_tbl and in_tbl:
        in_tbl = False
    elif is_tbl and in_tbl:
        pass
    # 检测表格内部空行：上一个非空是表格行，当前是空行，下一个非空是表格行
prev_nonempty = None
for i, l in enumerate(lines, 1):
    s = l.strip()
    if not s:
        continue
    if s.startswith('|') and prev_nonempty is not None and prev_nonempty[0].strip() == '':
        issues.append((prev_nonempty[1], i))
    prev_nonempty = (l, i)

print('表格前有空行的表格行数:', len(issues))
for a, b in issues[:15]:
    print(f'空行位于 {a}-{b} 之间')

# 统计所有表格块中内部空行
in_tbl = False
block_start = None
inner_blanks = 0
blocks_with_blanks = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('|'):
        if not in_tbl:
            in_tbl = True
            block_start = i
        continue
    if in_tbl and not s:
        # 表格块内的空行（下一行是表格行时算内部空行）
        if i + 1 <= len(lines) and lines[i].strip().startswith('|'):
            inner_blanks += 1
            blocks_with_blanks.append(block_start)
    elif in_tbl:
        in_tbl = False
print('表格内部空行总数:', inner_blanks)
print('受影响表格块起始行:', sorted(set(blocks_with_blanks)))
