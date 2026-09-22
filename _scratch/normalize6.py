# -*- coding: utf-8 -*-
"""第六轮修复：表格内部空行、=lim、混合公式半角括号"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
report = {}

# 1. 表格内部空行删除（前后非空行均为表格行）
n1 = 0
result = []
for i, l in enumerate(lines):
    if not l.strip():
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        k = i + 1
        while k < len(lines) and not lines[k].strip():
            k += 1
        if j >= 0 and k < len(lines) and lines[j].strip().startswith('|') and lines[k].strip().startswith('|'):
            n1 += 1
            continue
    result.append(l)
report['表格内部空行删除'] = n1
text = '\n'.join(result)

# 2. =lim -> =\lim
n2 = text.count('=lim ')
text = text.replace('=lim ', '=\\lim ')
report['=lim修正'] = n2

# 3. 混合公式半角括号：($..$文本) -> （$..$文本）
n3 = len(re.findall(r'[\u4e00-\u9fff0-9]\(\$[^$\n]{1,120}\$[^()\n]{0,80}\)', text))
text = re.sub(r'([\u4e00-\u9fff0-9])\((\$[^$\n]{1,120}\$[^()\n]{0,80})\)', r'\1（\2）', text)
report['混合公式括号'] = n3

text = text.rstrip('\n') + '\n'
with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第六轮修复报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
