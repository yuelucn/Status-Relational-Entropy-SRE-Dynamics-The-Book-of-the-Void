# -*- coding: utf-8 -*-
"""
把 vasp 源项目里的核子论文 v1.5 同步为书内章节格式（SRE-Dynamics 规范）。

源：C:/mywork/vasp/SRE_Nucleon_Complete_Paper.md / _EN.md        (v1.5, 2026-09-23)
目标：2-Everything_Emerges/SRE_Nucleon_Complete_Paper_1.5_C.md / _E.md

按成书规范做的三步加工：
  1) 删除作者署名行（全书统一不含作者行），保留版本行；
  2) 删除资源与可用性声明块（全书只有前言一份），改用「项目参考（DOI）」引用清单；
  3) 版本行由 1.5 保留、日期行按源更新。
用法：python sync_nucleon_v15.py [--apply]
"""
import re
import sys
import os

APPLY = '--apply' in sys.argv

SRC = {
    'C': 'C:/mywork/vasp/SRE_Nucleon_Complete_Paper.md',
    'E': 'C:/mywork/vasp/SRE_Nucleon_Complete_Paper_EN.md',
}
DST = {
    'C': '2-Everything_Emerges/SRE_Nucleon_Complete_Paper_1.5_C.md',
    'E': '2-Everything_Emerges/SRE_Nucleon_Complete_Paper_1.5_E.md',
}

# ---------- 书内沿用 1.3 版的「项目参考（DOI）」块（中文） ----------
DOI_C = """**项目参考（DOI，正文引用见附录 E）：**

- https://doi.org/10.5281/zenodo.22077475 — SRE-v1.6 公理套件
- https://doi.org/10.5281/zenodo.22162514 — SRE-Dynamics 复合基本粒子与关系空间涌现（虚空之书）
- https://doi.org/10.5281/zenodo.22119957 — SRE 动力学：利用纯无量纲图上同调与全局演化步骤严格重构麦克斯韦场方程
- https://doi.org/10.5281/zenodo.20576606 — 层级耗散自组织二值网络动力学
- https://doi.org/10.5281/zenodo.22119635 — SRE 电学量定义（电荷/电流/电阻/电压/功率/E=mc²）
- https://doi.org/10.5281/zenodo.22162514 — SRE 框架下电子的完整刻画（丛书）
"""

# 英文版：从 1.3 的 _E 文件里读取原有 DOI 块，保持与书内一致
DOI_E = None


def strip_bom(raw):
    if raw.startswith(b'\xef\xbb\xbf'):
        return raw[3:], b'\xef\xbb\xbf'
    return raw, b''


def extract_header_end(lines):
    """找到头部（H1 + 元信息 + 声明块 + DOI 块）结束、正文开始的行号。"""
    # 正文起点 = 「## 摘要」/「## Abstract」所在行
    for i, l in enumerate(lines):
        if re.match(r'^##\s*(摘要|Abstract)\s*$', l.strip()):
            return i
    raise RuntimeError('未找到摘要标题')


def build(lang):
    src_path = SRC[lang]
    raw = open(src_path, 'rb').read()
    raw, bom = strip_bom(raw)
    text = raw.decode('utf-8')
    lines = text.split('\n')

    h1 = lines[0].rstrip()
    body_start = extract_header_end(lines)
    body = lines[body_start:]

    # 从头部里抽取版本行与日期行的值
    ver_line = None
    date_line = None
    for l in lines[1:body_start]:
        s = l.strip()
        if re.search(r'(版本|Version)\s*[:：]', s):
            ver_line = s
        if re.search(r'(日期|Date)\s*[:：]', s):
            date_line = s
    assert ver_line is not None, '未找到版本行'
    assert date_line is not None, '未找到日期行'

    # 版本/日期行去掉作者字段（源里中文版作者与版本同行）
    ver_line = re.sub(r'^\*\*(作者|Author)[^*]*\*\*[\s\u3000]*', '', ver_line)
    ver_line = re.sub(r'\*\*(Author:)\s*[^*]*\*\*[\s\u3000]*', '', ver_line)
    ver_line = ver_line.strip()
    if not ver_line.startswith('**'):
        ver_line = '**' + ver_line
    date_line = date_line.strip()

    # 组装头部：H1 + 版本 + 日期 + 项目参考
    if lang == 'C':
        head = [h1, '', ver_line, date_line, '', DOI_C.rstrip(), '']
    else:
        head = [h1, '', ver_line, date_line, '', DOI_E.rstrip(), '']

    out = '\n'.join(head + body)
    return out, h1, ver_line, date_line


# 先读英文版 1.3 的 DOI 块作为模板
old_e = open('2-Everything_Emerges/SRE_Nucleon_Complete_Paper_1.3_E.md',
             'rb').read()
if old_e.startswith(b'\xef\xbb\xbf'):
    old_e = old_e[3:]
old_e_text = old_e.decode('utf-8')
m = re.search(r'^\*\*(Project [Rr]eferences|References)[^\n]*\*\*.*?(?=\n---)',
              old_e_text, re.M | re.S)
if m:
    DOI_E = m.group(0).rstrip()
    print('=== 英文版沿用 1.3 的引用块 ===')
    print(DOI_E)
else:
    print('!! 未能从 1.3 英文版提取引用块，改用中文结构直译')
    DOI_E = """**Project references (DOI, cited in the text; see Appendix E):**

- https://doi.org/10.5281/zenodo.22077475 — SRE-v1.6 axiomatic suite
- https://doi.org/10.5281/zenodo.22162514 — SRE-Dynamics: composite elementary particles and relational-space emergence (Book of the Void)
- https://doi.org/10.5281/zenodo.22119957 — SRE dynamics: rigorous reconstruction of Maxwell's field equations
- https://doi.org/10.5281/zenodo.20576606 — Hierarchical dissipative self-organizing binary network dynamics
- https://doi.org/10.5281/zenodo.22119635 — SRE definitions of electrical quantities (charge/current/resistance/voltage/power/E=mc²)
- https://doi.org/10.5281/zenodo.22162514 — Complete characterization of the electron within the SRE framework (book series)
"""

print()
for lang in ('C', 'E'):
    out, h1, ver, date = build(lang)
    n_lines = out.count('\n') + 1
    print(f'--- {lang}: {DST[lang]}')
    print(f'    H1   : {h1[:70]}')
    print(f'    版本 : {ver}')
    print(f'    日期 : {date}')
    print(f'    行数 : {n_lines}')
    n_h1 = len(re.findall(r'^#\s+', out, re.M))
    print(f'    H1 数: {n_h1}')
    # 残留检查
    residue = []
    for i, l in enumerate(out.split('\n'), 1):
        if re.match(r'^\*\*\s*(作者|Author)\s*[:：]', l) and 'Note' not in l:
            residue.append((i, l[:60]))
        if 'Zenodo 开源数据仓库' in l or 'Zenodo open data repository' in l:
            residue.append((i, l[:60]))
    print(f'    残留 : {residue if residue else "无"}')
    if APPLY:
        with open(DST[lang], 'wb') as f:
            f.write(out.encode('utf-8'))
        print(f'    已写入 {DST[lang]}')
