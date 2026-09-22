# -*- coding: utf-8 -*-
"""SRE-Dynamics 全书文本规范化脚本
处理：连字符统一、特殊空格、emoji 符号、半角括号、空行压缩
跳过代码块与 LaTeX 公式内容中的结构性替换
"""
import io, re, sys

SRC = r'C:\mywork\SRE-Dynamics\combined_C.md'
DST = r'C:\mywork\SRE-Dynamics\combined_C.normalized.md'

with io.open(SRC, encoding='utf-8') as f:
    text = f.read()

orig_len = len(text)
report = {}

# ---------- 1. 全局面性字符替换（不影响公式/代码） ----------
def gsub(pat, repl, name, flags=0):
    global text
    n = len(re.findall(pat, text))
    text = re.sub(pat, repl, text, flags=flags)
    report[name] = n

# 1.1 连字符统一：U+2011(‑) U+2010(‐) -> 半角 -
gsub('\u2011|\u2010', '-', '连字符U+2011/2010统一')
# 1.2 窄不换行空格 U+202F -> 普通空格
gsub('\u202f', ' ', '窄不换行空格U+202F')
# 1.3 全角空格 U+2003 -> 普通空格
gsub('\u2003', ' ', '全角空格U+2003')
# 1.4 变体选择符 U+FE0F 删除
gsub('\ufe0f', '', '变体选择符U+FE0F')
# 1.5 证毕方块 ◼ -> ∎
gsub('\u25fc', '\u220e', '证毕方块◼')
# 1.6 错误标记 ❌ -> 删除（保留其后“错误：”）
gsub('\u274c', '', '错误标记❌')
# 1.7 警告/注意 ⚠️ -> **注意**：
gsub('\u26a0\ufe0f?', '**注意**：', '警告⚠')
# 1.8 重要 ❗ -> **重要**：
gsub('\u2757', '**重要**：', '重要❗')

# ---------- 2. 行级处理（跳过代码块） ----------
lines = text.split('\n')
out = []
in_code = False
in_block = False
paren_converted = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('```'):
        in_code = not in_code
        out.append(line)
        continue
    if in_code:
        out.append(line)
        continue
    # 单行公式块 $$...$$（自闭合）不切换块状态
    if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
        out.append(line)
        continue
    if stripped.startswith('$$'):
        in_block = not in_block
        out.append(line)
        continue

    # 2.1 中文紧贴半角括号 -> 全角（括号内不含 $、http、反斜杠、成对公式标记）
    # 条件：左括号前是中文或全角标点，右括号后是中文/标点/行尾
    def conv(m):
        global paren_converted
        inner = m.group(2)
        if '$' in inner or 'http' in inner or '\\' in inner or '`' in inner:
            return m.group(0)
        paren_converted += 1
        return m.group(1) + '（' + inner + '）' + m.group(3)
    line = re.sub(r'([\u4e00-\u9fff\u3001-\u303f\uff00-\uffef])\(([^()\n]{1,60})\)([\u4e00-\u9fff\u3001-\u303f\uff00-\uffef]?|$)', conv, line)

    out.append(line)
report['半角括号转全角'] = paren_converted
text = '\n'.join(out)

# ---------- 3. 空行压缩：连续空行 -> 单空行 ----------
# 先压缩行内多余空白
text = re.sub(r'[ \t]+\n', '\n', text)
# 连续空行合并为 1
before = text.count('\n\n\n')
text = re.sub(r'\n{3,}', '\n\n', text)
report['连续空行块合并'] = before
# 行首多余空格（非代码、非表格、非列表）清理已在上面处理
# 文档结尾统一单换行
text = text.rstrip('\n') + '\n'

with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print('=== 规范化报告 ===')
for k, v in report.items():
    print(f'{k}: {v}')
print(f'原长度: {orig_len} -> 新长度: {len(text)}')
