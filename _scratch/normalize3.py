# -*- coding: utf-8 -*-
"""第三轮修复：公式内全角括号、损坏分隔线、LaTeX星号、损坏标题、列表编号"""
import io, re

SRC = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')
report = {}

# 1. 公式 $...$ 内部的全角括号恢复为半角
n1 = 0
def fix_formula(m):
    global n1
    seg = m.group(0)
    if '（' in seg or '）' in seg:
        n1 += seg.count('（') + seg.count('）')
        seg = seg.replace('（', '(').replace('）', ')')
    return seg
lines = [re.sub(r'\$[^$\n]+\$', fix_formula, l) for l in lines]
report['公式内全角括号恢复'] = n1
text = '\n'.join(lines)

# 2. 损坏分隔线（全由横线/破折号组成的行）恢复为 ---
n2 = 0
out = []
for l in text.split('\n'):
    if re.match(r'^[—\-]{3,}$', l.strip()):
        if l.strip() != '---':
            n2 += 1
        out.append('---')
    else:
        out.append(l)
report['损坏分隔线恢复'] = n2
text = '\n'.join(out)

# 3. LaTeX 星号污染：\mathcal{X}* -> \mathcal{X}_
n3 = len(re.findall(r'(\\mathcal\{[A-Za-z]+\})\*', text))
text = re.sub(r'(\\mathcal\{[A-Za-z]+\})\*', r'\1_', text)
report['LaTeX星号修复'] = n3

# 4. 损坏标题
fixes = {
    '##-. 开放理论边界与未来拓展方向': '## 11. 开放理论边界与未来拓展方向',
    '##-. P0级紧急修订：拓扑权重 $w_\\alpha$ 显式映射及其SRE统计力学起源': '## 11. P0级紧急修订：拓扑权重 $w_\\alpha$ 显式映射及其SRE统计力学起源',
    '##-. 渐近极限与边界分析': '## 13. 渐近极限与边界分析',
    '###-.1 耦合常数 $\\lambda \\to 0$（零耗散结晶边界）': '### 13.1 耦合常数 $\\lambda \\to 0$（零耗散结晶边界）',
    '###-.2 耦合常数 $\\lambda \\to \\infty$（无穷耗散热寂边界）': '### 13.2 耦合常数 $\\lambda \\to \\infty$（无穷耗散热寂边界）',
}
n4 = 0
lines = text.split('\n')
for i, l in enumerate(lines):
    for k, v in fixes.items():
        if l.strip() == k:
            lines[i] = l.replace(k, v)
            n4 += 1
report['损坏标题修复'] = n4
text = '\n'.join(lines)

# 5. 第三部分简介列表编号重复：5,5,6,7 -> 5,6,7,8
n5 = 0
lines = text.split('\n')
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('5. **算子-4：局域拓扑度数统计算子') and '狄利克雷' in s:
        lines[i] = l.replace('5. **算子-4', '6. **算子-4')
        n5 += 1
    elif s.startswith('6. **算子-5：内生变量延迟校准算子') and '全量完整版' in s:
        lines[i] = l.replace('6. **算子-5', '7. **算子-5')
        n5 += 1
    elif s.startswith('7. **算子-6：子空间谱筛选与拼接算子') and '终审定稿规范' in s:
        lines[i] = l.replace('7. **算子-6', '8. **算子-6')
        n5 += 1
report['列表编号修正'] = n5
text = '\n'.join(lines)

text = text.rstrip('\n') + '\n'
with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 第三轮修复报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
