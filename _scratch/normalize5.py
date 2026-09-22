# -*- coding: utf-8 -*-
"""第五轮修复：文字错误、文档头统一、\[ \] 显示公式统一"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
report = {}

# 1. 雅共比 -> 雅可比
n1 = text.count('雅共比')
text = text.replace('雅共比', '雅可比')
report['雅共比修正'] = n1

# 2. 常数常数 -> 常数
n2 = text.count('常数常数')
text = text.replace('常数常数', '常数')
report['常数常数修正'] = n2

# 3. 缺书名号
n3 = text.count('《SRE通用图算子流水线与发布路线图的发布计划')
text = text.replace('《SRE通用图算子流水线与发布路线图的发布计划', '《SRE通用图算子流水线与发布路线图》的发布计划')
report['书名号修复'] = n3

# 4. 文档头统一：作者/版本行 -> **作者**：/**版本**：
lines = text.split('\n')
n4 = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('作者') and '岳路' in s and not s.startswith('**'):
        lines[i] = '**作者**：岳路'
        n4 += 1
    elif s.startswith('版本') and re.match(r'^版本[：:]\s*\S', s) and not s.startswith('**'):
        m = re.match(r'^版本[：:]\s*(\S.*)$', s)
        lines[i] = '**版本**：' + m.group(1)
        n4 += 1
    elif s.startswith(' 版本'):
        m = re.match(r'^ 版本[：:]\s*(\S.*)$', s)
        lines[i] = '**版本**：' + m.group(1)
        n4 += 1
report['文档头统一'] = n4
text = '\n'.join(lines)

# 5. 单独成行的 \[ 和 \] -> $$
lines = text.split('\n')
n5a = n5b = 0
for i, l in enumerate(lines):
    if l.strip() == '\\[':
        lines[i] = '$$'
        n5a += 1
    elif l.strip() == '\\]':
        lines[i] = '$$'
        n5b += 1
report['\\[ 转 $$'] = n5a
report['\\] 转 $$'] = n5b
text = '\n'.join(lines)

# 6. 行首多余空格清理（非代码/表格/列表缩进保留）
lines = text.split('\n')
n6 = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('```') or s.startswith('|') or s.startswith('* ') or s.startswith('- ') or s.startswith('>') or s.startswith('#') or s.startswith('1.') or s.startswith('2.') or s.startswith('3.') or s.startswith('4.') or s.startswith('5.') or s.startswith('6.') or s.startswith('7.') or s.startswith('8.') or s.startswith('9.') or s.startswith('10.') or re.match(r'^\d+\.', s):
        continue
    if l.startswith(' ') and not l.startswith('    '):
        n6 += 1
        lines[i] = l.lstrip()
text = '\n'.join(lines)
report['行首空格清理'] = n6

# 7. 压缩多余空行
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.rstrip('\n') + '\n'

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第五轮修复报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
