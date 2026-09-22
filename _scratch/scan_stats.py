# -*- coding: utf-8 -*-
"""扫描全书结构统计"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.md'
with io.open(SRC, encoding='utf-8') as f:
    text = f.read()

fences = re.findall(r'^```.*$', text, re.M)
print('代码围栏数:', len(fences))

dollars = text.count('$$')
print('$$ 数量:', dollars)

# 内联公式粗估（行内 $...$）
lines = text.split('\n')
inline_count = 0
in_code = False
for line in lines:
    if line.strip().startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    # 去掉块公式行
    s = line.strip()
    if s.startswith('$$') or s.endswith('$$'):
        continue
    n = s.count('$')
    if n >= 2:
        inline_count += n // 2
print('含内联公式行数(粗估):', inline_count)

heads = re.findall(r'^#{1,6} .*$', text, re.M)
print('标题行数:', len(heads))

# 各级标题统计
from collections import Counter
lv = Counter(len(m.group(0).split(' ')[0]) for m in re.finditer(r'^(#{1,6}) .*$', text, re.M))
print('各级标题数:', dict(sorted(lv.items())))

# 表格行
tbl = [l for l in lines if l.strip().startswith('|')]
print('表格行数:', len(tbl))

# 图片
imgs = re.findall(r'!\[[^\]]*\]\([^)]+\)', text)
print('图片引用数:', len(imgs))

# 链接
links = re.findall(r'\[[^\]]+\]\(https?://[^)]+\)', text)
print('外部链接数:', len(links))
