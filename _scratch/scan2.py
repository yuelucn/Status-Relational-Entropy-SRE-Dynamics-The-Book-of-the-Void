# -*- coding: utf-8 -*-
"""第二轮检查：残留问题扫描"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

# 1. LaTeX 圆括号
print('LaTeX圆括号 \\( :', text.count('\\('), ' \\) :', text.count('\\)'))

# 2. 重复分页符
pb = [i for i, l in enumerate(lines) if 'page-break-after' in l]
print('分页符数:', len(pb))
dups = [(pb[i-1], pb[i]) for i in range(1, len(pb)) if pb[i]-pb[i-1] <= 2]
print('相邻重复分页对:', dups)

# 3. 中文间多余空格
gap = [l for l in lines if re.search(r'[\u4e00-\u9fff] [\u4e00-\u9fff]', l)]
print('中文间含空格行数:', len(gap))
for l in gap[:12]:
    print('  ', repr(l[:100]))

# 4. v1.0-rev
v10 = [l for l in lines if 'v1.0-rev' in l]
print('v1.0-rev 出现次数:', len(v10))
for l in v10:
    print('  ', repr(l[:120]))

# 5. 数学字母
mathlet = re.findall(r'[\U0001D400-\U0001D7FF]', text)
print('数学字母数量:', len(mathlet), mathlet[:20])

# 6. 中文后半角问号
cn_q = [l for l in lines if re.search(r'[\u4e00-\u9fff]\?', l)]
print('中文后半角问号行数:', len(cn_q))
for l in cn_q[:8]:
    print('  ', repr(l[:100]))

# 7. 全角百分号/其他
for ch in ['％', '：', '；']:
    print(f'字符 {ch!r} 数量:', text.count(ch))
