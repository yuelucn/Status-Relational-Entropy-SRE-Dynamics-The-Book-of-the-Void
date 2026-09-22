# -*- coding: utf-8 -*-
import io, re
with io.open(r'C:\mywork\SRE-Dynamics\combined_C.normalized.md', encoding='utf-8') as f:
    lines = f.readlines()

# 真正的公式内全角括号：单个 $...$ 段内部含（ 且（ 前后都是该段内字符
real = 0
for i, l in enumerate(lines, 1):
    for m in re.finditer(r'\$[^$\n]+\$', l):
        seg = m.group(0)
        # 去掉首尾 $
        inner = seg[1:-1]
        if '（' in inner or '）' in inner:
            real += 1
            if real <= 5:
                print(i, repr(seg[:90]))
print('真实公式内全角括号段:', real)

# 验证修复样本
samples = ['$M_5(1,1)$', '核心成员——', '（$\\mathcal{G}', '**作者**：', '**版本**：']
text = ''.join(lines)
for s in samples:
    print(repr(s), '出现:', text.count(s))
