# -*- coding: utf-8 -*-
import io
p = r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md'
with io.open(p, encoding='utf-8') as f:
    text = f.read()
n = text.count(r'\varinjlim')
text = text.replace(r'\varinjlim', r'\underset{\longrightarrow}{\lim}')
with io.open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print('替换数量:', n)
