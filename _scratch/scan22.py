# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md', encoding='utf-8') as f:
    lines = f.readlines()
# 标题中 中文/数字 + 空格 + (内容)
n = 0
for i, l in enumerate(lines, 1):
    if l.startswith('#'):
        for m in re.finditer(r'[\u4e00-\u9fff0-9] \(([^()\n]{1,80})\)', l):
            n += 1
            print(i, repr(m.group(0)[:80]))
print('标题中空格半角括号:', n)
