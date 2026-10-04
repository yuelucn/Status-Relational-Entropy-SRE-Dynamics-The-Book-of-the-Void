# -*- coding: utf-8 -*-
"""把 vasp 的三篇新论文（质量起源 / 光与电磁波定位 / 时间涌现）转为书内章节。

加工规则（与既有成书规范一致）：
  1) 删除作者署名行（保留版本行、日期行）
  2) 删除开头的「资源与可用性声明」样板块（全书统一收敛于前言）
  3) 删除篇内「## 声明 / ## Declaration / ## Statement」小节
  4) 删除「## 附录 E 归属映射与项目参考 / ## Appendix E ...」小节（含其前的分隔线）
  5) 修正 §1.4 中指向附录 E 的悬空交叉引用
  6) 保证恰好 1 个 H1

用法：python sync_origin_papers.py [--apply]
"""
import os
import re
import sys

VASP = 'C:/mywork/vasp'
PROJ = 'C:/mywork/SRE-Dynamics'
DEST_DIR = os.path.join(PROJ, '2-Everything_Emerges')

PAIRS = [
    ('SRE_Mass_Origin_Paper.md',     'SRE_Mass_Origin_Paper_1.0_C.md'),
    ('SRE_Mass_Origin_Paper_EN.md',  'SRE_Mass_Origin_Paper_1.0_E.md'),
    ('SRE_Light_Origin_Paper.md',    'SRE_Light_Origin_Paper_1.0_C.md'),
    ('SRE_Light_Origin_Paper_EN.md', 'SRE_Light_Origin_Paper_1.0_E.md'),
    ('SRE_时间涌现.md',               'SRE_Time_Emergence_1.0_C.md'),
    ('SRE_时间涌现_EN.md',            'SRE_Time_Emergence_1.0_E.md'),
]

AUTHOR_RE = re.compile(r'^\*{0,2}\s*(?:作者|Author)\s*\*{0,2}\s*[:：]')
DECL_START_RE = re.compile(r'^>\s*[【\[].*(资源与可用性声明|Resource and Availability Statement)')
SECTION_RE = re.compile(r'^##\s+(?:声明|Declaration|Statement|附录\s*E|Appendix\s*E)\b')
APPENDIX_E_RE = re.compile(r'^##\s+(?:附录\s*E|Appendix\s*E)\b')
NEXT_H2_RE = re.compile(r'^##\s+')
# §1.4 悬空引用
DANGLING_RE = re.compile(
    r'[，,]\s*(?:and\s+)?(?:附录\s*E\s*为归属映射|Appendix\s*E\s+the\s+attribution\s+mapping)'
    r'(?=[。.])'
)


def load(path):
    raw = open(path, 'rb').read()
    bom = b''
    if raw.startswith(b'\xef\xbb\xbf'):
        bom, raw = raw[:3], raw[3:]
    return bom, raw.decode('utf-8')


def transform(text, tag):
    lines = text.split('\n')
    dels = []          # (start, end_inclusive)
    report = []

    # --- 1) 作者行（只在前 15 行内找） ---
    for i in range(min(15, len(lines))):
        if AUTHOR_RE.match(lines[i].strip()):
            dels.append((i, i))
            report.append('删作者行 @%d: %r' % (i + 1, lines[i].strip()))
            break

    # --- 2) 资源与可用性声明样板块（到其后第一条 --- 之前） ---
    ds = next((i for i, l in enumerate(lines) if DECL_START_RE.match(l)), None)
    if ds is not None:
        sep = next((j for j in range(ds + 1, len(lines)) if lines[j].strip() == '---'), None)
        if sep is None:
            raise SystemExit('找不到声明块的结束分隔线: %s' % tag)
        dels.append((ds, sep - 1))
        report.append('删声明样板块 @%d-%d' % (ds + 1, sep))

    # --- 3) 篇内 ## 声明 小节（到下一个 ## 之前） ---
    m = next((i for i, l in enumerate(lines) if SECTION_RE.match(l)), None)
    if m is not None:
        nxt = next((j for j in range(m + 1, len(lines)) if NEXT_H2_RE.match(lines[j])), len(lines))
        dels.append((m, nxt - 1))
        report.append('删「%s」小节 @%d-%d' % (lines[m].strip(), m + 1, nxt))

    # --- 4) 附录 E 小节（连同其前的 --- 分隔线，删到文件末） ---
    e = next((i for i, l in enumerate(lines) if APPENDIX_E_RE.match(l)), None)
    if e is not None:
        k = e - 1
        while k >= 0 and lines[k].strip() == '':
            k -= 1
        if k >= 0 and lines[k].strip() == '---':
            start = k
        else:
            start = e
        dels.append((start, len(lines) - 1))
        report.append('删附录E @%d-EOF' % (start + 1))

    # --- 应用删除（倒序） ---
    out = list(lines)
    for a, b in sorted(dels, key=lambda x: -x[0]):
        del out[a:b + 1]

    text2 = '\n'.join(out)

    # --- 5) 悬空引用修正 ---
    text2, n_fix = DANGLING_RE.subn('', text2)
    if n_fix:
        report.append('修正 §1.4 对附录E的悬空引用 %d 处' % n_fix)

    # --- 收尾：折叠 3+ 连续换行；去掉尾部悬空的 --- 分隔线；保证单个末尾换行 ---
    text2 = re.sub(r'\n{3,}', '\n\n', text2)
    while True:
        stripped = text2.rstrip('\n')
        if stripped.endswith('\n---') or stripped == '---':
            text2 = stripped[:-3] if stripped != '---' else ''
        else:
            break
    text2 = text2.rstrip('\n') + '\n'

    n_h1 = len(re.findall(r'^#\s+', text2, re.M))
    report.append('H1 数量 = %d' % n_h1)
    if n_h1 != 1:
        raise SystemExit('H1 数量异常（%d）：%s' % (n_h1, tag))

    return text2, report


def main():
    apply = '--apply' in sys.argv
    for src, dst in PAIRS:
        sp = os.path.join(VASP, src)
        dp = os.path.join(DEST_DIR, dst)
        bom, text = load(sp)
        new, rep = transform(text, src)
        print('=' * 72)
        print('%s\n  -> %s   %d 行 -> %d 行' % (src, dst, len(text.split('\n')), len(new.split('\n'))))
        for r in rep:
            print('   *', r)
        print('   --- 头部 12 行 ---')
        for l in new.split('\n')[:12]:
            print('   |', l)
        print('   --- 尾部 4 行 ---')
        for l in new.split('\n')[-5:-1]:
            print('   |', l)
        if apply:
            with open(dp, 'wb') as f:
                f.write(bom + new.encode('utf-8'))
            print('   [已写入]', dp)
    if not apply:
        print('\n（干跑，未写盘；加 --apply 落盘）')


if __name__ == '__main__':
    main()
