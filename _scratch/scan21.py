# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.md', encoding='utf-8') as f:
    lines = f.readlines()
text = ''.join(lines)
print('varinjlim 数量:', text.count('\\varinjlim'))
for i, l in enumerate(lines, 1):
    if '\\varinjlim' in l:
        m = re.search(r'.{40}\\varinjlim.{40}', l)
        print(i, repr(m.group(0)) if m else repr(l[:100]))
# 检查其他可能不支持的 LaTeX 宏
for macro in ['\\varprojlim', '\\projlim', '\\injlim', '\\varinjlim', '\\xrightarrow', '\\xleftarrow', '\\textcircled', '\\mathring', '\\circledast', '\\boxplus', '\\boxminus', '\\boxdot', '\\boxtimes', '\\leftthreetimes', '\\rightthreetimes', '\\lhd', '\\rhd', '\\unlhd', '\\unrhd', '\\Subset', '\\Supset']:
    c = text.count('\\' + macro)
    if c:
        print(f'{macro}: {c}')
