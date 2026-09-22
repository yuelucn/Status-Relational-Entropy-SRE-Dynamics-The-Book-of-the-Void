# -*- coding: utf-8 -*-
"""第二轮规范化：破折号、孤立引用行、半角冒号/括号、重复分页、LaTeX括号、杂项"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
report = {}

# 1. -- 破折号 -> —— （行级，保护公式$..$与跳过公式块/表格行）
lines = text.split('\n')
out = []
in_block = False
n1 = 0
for line in lines:
    s = line.strip()
    # 单行公式块 $$...$$（自闭合）不切换块状态
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        out.append(line)
        continue
    if s.startswith('$$'):
        in_block = not in_block
        out.append(line)
        continue
    if in_block or s.startswith('|') or s.strip().startswith('```'):
        out.append(line)
        continue
    # 保护 $...$ 公式内容
    parts = []
    def hold(m):
        parts.append(m.group(0))
        return '\x00%d\x00' % (len(parts) - 1)
    protected = re.sub(r'\$[^$\n]+\$', hold, line)
    cnt = len(re.findall(r'--', protected))
    if cnt:
        protected = re.sub(r'--(?!--)', '——', protected)
        n1 += cnt
    # 还原公式
    for i, p in enumerate(parts):
        protected = protected.replace('\x00%d\x00' % i, p)
    out.append(protected)
report['--破折号'] = n1
text = '\n'.join(out)

# 2. 孤立引用行（整行只有一个 >）删除
lines = text.split('\n')
n2 = sum(1 for l in lines if l.strip() == '>')
lines = [l for l in lines if l.strip() != '>']
report['孤立>行删除'] = n2
text = '\n'.join(lines)

# 3. 中文后半角冒号 -> 全角
n3 = len(re.findall(r'[\u4e00-\u9fff]:', text))
text = re.sub(r'([\u4e00-\u9fff]):', r'\1：', text)
report['半角冒号转全角'] = n3

# 4. 半角括号转全角（行级，跳过表格行与公式块）
lines = text.split('\n')
out = []
in_block = False
n4 = 0
for line in lines:
    s = line.strip()
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        out.append(line)
        continue
    if s.startswith('$$'):
        in_block = not in_block
        out.append(line)
        continue
    if in_block or s.startswith('|'):
        out.append(line)
        continue
    def conv(m):
        global n4
        inner = m.group(2)
        if 'http' in inner or '\\' in inner or '`' in inner:
            return m.group(0)
        n4 += 1
        return m.group(1) + '（' + inner + '）' + m.group(3)
    line = re.sub(r'([\u4e00-\u9fff0-9\u3001-\u303f\uff00-\uffef])\(([^()\n]{1,80})\)([\u4e00-\u9fff\u3001-\u303f\uff00-\uffef]?|$)', conv, line)
    out.append(line)
report['半角括号转全角(2轮)'] = n4
text = '\n'.join(out)

# 5. 重复分页符合并：分页符连续(间隔<=3行)仅保留一个
lines = text.split('\n')
n5 = 0
result = []
i = 0
while i < len(lines):
    if 'page-break-after' in lines[i]:
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or 'page-break-after' in lines[j]):
            if 'page-break-after' in lines[j]:
                n5 += 1
            j += 1
        result.append(lines[i])
        result.append('')
        i = j
        continue
    result.append(lines[i])
    i += 1
report['重复分页符合并'] = n5
text = '\n'.join(result)

# 6. LaTeX 圆括号 \(X\) -> $X$
n6 = len(re.findall(r'\\\(', text))
text = re.sub(r'\\\(([^\\()]+?)\\\)', r'$\1$', text)
report['LaTeX圆括号转$'] = n6

# 7. 描述 工具 -> 描述工具
n7 = text.count('描述 工具')
text = text.replace('描述 工具', '描述工具')
report['字间空格修正'] = n7

# 8. v1.0-rev -> v1.1-rev（版本号笔误）
n8 = text.count('v1.0-rev')
text = text.replace('v1.0-rev', 'v1.1-rev')
report['版本号v1.0-rev修正'] = n8

# 9. 数学斜体 c（U+1D450）-> c
n9 = text.count('\U0001D450')
text = text.replace('\U0001D450', 'c')
report['数学字母c修正'] = n9

# 10. 压缩多余空行
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.rstrip('\n') + '\n'

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第二轮规范化报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
