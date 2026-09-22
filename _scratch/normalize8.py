# -*- coding: utf-8 -*-
"""第八轮修复：钢性->刚性、标题双语括号转全角"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md'
DST = r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
report = {}

# 1. 钢性 -> 刚性
n1 = text.count('钢性')
text = text.replace('钢性', '刚性')
report['钢性修正'] = n1

# 2. 标题行 中文/数字+空格+(内容) -> 全角
lines = text.split('\n')
n2 = 0
for i, l in enumerate(lines):
    if l.startswith('#'):
        new = re.sub(r'([\u4e00-\u9fff0-9]) \(([^()\n]{1,80})\)', r'\1（\2）', l)
        if new != l:
            n2 += 1
        lines[i] = new
report['标题双语括号'] = n2
text = '\n'.join(lines)

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第八轮修复报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
