# -*- coding: utf-8 -*-
"""第四轮修复：加粗后半角冒号、URL编码连字符、含公式半角括号"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
report = {}

# 1. 加粗文本后半角冒号 -> 全角
n1 = len(re.findall(r'\*\*[^*\n]+\*\*:', text))
text = re.sub(r'(\*\*[^*\n]+\*\*):', r'\1：', text)
report['加粗后半角冒号'] = n1

# 2. URL 编码的 U+2011（%E2%80%91）-> -
n2 = text.count('%E2%80%91')
text = text.replace('%E2%80%91', '-')
report['URL编码连字符'] = n2

# 3. 含公式的半角括号 -> 全角
n3 = len(re.findall(r'[\u4e00-\u9fff0-9]\(\$[^$\n]{1,120}\$\)', text))
text = re.sub(r'([\u4e00-\u9fff0-9])\((\$[^$\n]{1,120}\$)\)', r'\1（\2）', text)
report['含公式半角括号'] = n3

text = text.rstrip('\n') + '\n'
with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第四轮修复报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
