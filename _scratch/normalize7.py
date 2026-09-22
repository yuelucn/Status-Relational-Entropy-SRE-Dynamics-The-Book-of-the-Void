# -*- coding: utf-8 -*-
"""第七轮最终修复"""
import io

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()

# 1. 电动力学,作者 -> 电动力学，作者
n1 = text.count('电动力学,作者')
text = text.replace('电动力学,作者', '电动力学，作者')

# 2. 表格内 (高, 高) -> （高，高）等
n2 = 0
for a, b in [('(高, 高)', '（高，高）'), ('(高, 低)', '（高，低）'), ('(低, 高)', '（低，高）'), ('(低, 低)', '（低，低）')]:
    c = text.count(a)
    text = text.replace(a, b)
    n2 += c

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)
print(f'正文逗号修复: {n1}, 表格括号修复: {n2}')
