# -*- coding: utf-8 -*-
import io
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()

in_block = False
last_open = None
problems = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        if not in_block:
            last_open = i
            in_block = True
        else:
            in_block = False
    # 记录 4879 前最后状态
    if i == 4879:
        print('4879行时 in_block:', in_block, '最后打开的$$行:', last_open)

# 全文件未闭合检查
in_block = False
open_pos = None
unclosed = []
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('$$'):
        if not in_block:
            in_block = True
            open_pos = i
        else:
            in_block = False
    if not in_block:
        open_pos = None
    if in_block and i == 4879:
        print('4879 位于未闭合块, 起始于行:', open_pos)
