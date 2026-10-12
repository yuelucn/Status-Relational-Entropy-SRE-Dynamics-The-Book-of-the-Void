# -*- coding: utf-8 -*-
"""Sync Nov-2026 updates into the SRE-Dynamics book.

Items:
  1. Operator-pipeline white paper  v1.1 -> v2.0   (source: math-graph/SRE-math_C|E.md)
  2. Graph500 benchmark chapter     v1.0 -> v2.0   (source: math-graph/math-vector_v2/SRE_19_operators_graph500_article_2.0_C|E.md)
  3. Anti-gravity hypothesis        NEW chapter    (source: SRE-antigravity/Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_C|E.md)

Book conventions applied on each incoming chapter:
  - drop the author by-line (keep the version line);
  - drop the leading resource/availability statement block (the book keeps exactly one, in the preface);
  - ensure exactly one H1 (anti-gravity source has 3; demote its Part headings to H2).
"""
import os, re

ROOT = r'C:/mywork/SRE-Dynamics'
P3 = os.path.join(ROOT, '3-Mathematical_Support')
P4 = os.path.join(ROOT, '4-Applications&Hypothesis')
MG = r'C:/mywork/math-graph'
MV = os.path.join(MG, 'math-vector_v2')
AG = r'C:/mywork/SRE-antigravity'

SRC = {
    'pipe_c': os.path.join(MG, 'SRE-math_C.md'),
    'pipe_e': os.path.join(MG, 'SRE-math_E.md'),
    'g500_c': os.path.join(MV, 'SRE_19_operators_graph500_article_2.0_C.md'),
    'g500_e': os.path.join(MV, 'SRE_19_operators_graph500_article_2.0_E.md'),
    'anti_c': os.path.join(AG, 'Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_C.md'),
    'anti_e': os.path.join(AG, 'Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_E.md'),
}
DST = {
    'pipe_c': os.path.join(P3, 'Universal_Graph_Operator_Pipeline_in_SRE_2.0_C.md'),
    'pipe_e': os.path.join(P3, 'Universal_Graph_Operator_Pipeline_in_SRE_2.0_E.md'),
    'g500_c': os.path.join(P4, 'Graph500_2.0_C.md'),
    'g500_e': os.path.join(P4, 'Graph500_2.0_E.md'),
    'anti_c': os.path.join(P4, 'Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_C.md'),
    'anti_e': os.path.join(P4, 'Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_E.md'),
}
OLD_FILES = [
    os.path.join(P3, 'Universal_Graph_Operator_Pipeline_in_SRE_1.1_C.md'),
    os.path.join(P3, 'Universal_Graph_Operator_Pipeline_in_SRE_1.1_E.md'),
    os.path.join(P4, 'Graph500_1.0_C.md'),
    os.path.join(P4, 'Graph500_1.0_E.md'),
]


def read_text(p):
    with open(p, 'r', encoding='utf-8-sig') as f:
        return f.read()


def write_text(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(s)


def remove_block(text, start_marker, end_marker):
    """Delete from the line containing start_marker through the line containing end_marker (inclusive)."""
    lines = text.split('\n')
    si = ei = None
    for i, l in enumerate(lines):
        if si is None and start_marker in l:
            si = i
            continue
        if si is not None and end_marker in l:
            ei = i
            break
    if si is not None and ei is not None:
        del lines[si:ei + 1]
    return '\n'.join(lines)


def remove_line_containing(text, substr):
    return '\n'.join(l for l in text.split('\n') if substr not in l)


def count_h1(text):
    in_fence = False
    n = 0
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('```') or s.startswith('~~~'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r'^#\s+\S', line):
            n += 1
    return n


def strip_bom_only(t):
    return t


# ---- cleaners ---------------------------------------------------------
def clean_pipe_c(t):
    t = remove_line_containing(t, '**作者**：')
    t = remove_line_containing(t, '**安全声明**：')
    return t


def clean_pipe_e(t):
    t = remove_line_containing(t, '**Author**:')
    t = remove_line_containing(t, '**Security Notice**:')
    return t


def clean_g500_c(t):
    t = remove_line_containing(t, '作者: 岳路')
    t = remove_block(t, '【资源与可用性声明】', '经典物理基础源自信息统计学')
    return t


def clean_g500_e(t):
    t = remove_line_containing(t, 'Author: Yue Lu')
    t = remove_block(t, 'Resource‑Availability Statement', 'physical foundation originates from information statistics')
    return t


def clean_anti_c(t):
    t = remove_line_containing(t, '作者: 岳路')
    t = remove_block(t, '【资源与可用性声明】', '经典物理基础源自信息统计学')
    # single-H1 requirement: demote the two Part headings to H2
    lines = t.split('\n')
    for i, l in enumerate(lines):
        if l.startswith('# 上篇'):
            lines[i] = '#' + l
        elif l.startswith('# 下篇'):
            lines[i] = '#' + l
    return '\n'.join(lines)


def clean_anti_e(t):
    t = remove_line_containing(t, 'Author: Yue Lu')
    t = remove_block(t, 'Resources and Availability Statement', 'foundations of classical physics originate from information statistics')
    lines = t.split('\n')
    for i, l in enumerate(lines):
        if l.startswith('# Part I\u3000') or l.startswith('# Part I '):
            lines[i] = '#' + l
        elif l.startswith('# Part II\u3000') or l.startswith('# Part II '):
            lines[i] = '#' + l
    return '\n'.join(lines)


CLEAN = {
    'pipe_c': clean_pipe_c, 'pipe_e': clean_pipe_e,
    'g500_c': clean_g500_c, 'g500_e': clean_g500_e,
    'anti_c': clean_anti_c, 'anti_e': clean_anti_e,
}


def main():
    print('=== generating chapter files ===')
    for key in DST:
        t = read_text(SRC[key])
        t = CLEAN[key](t)
        write_text(DST[key], t)
        print(f'  {os.path.basename(DST[key])}: H1={count_h1(t)}, lines={len(t.split(chr(10)))}')

    print('=== removing superseded files ===')
    for p in OLD_FILES:
        if os.path.exists(p):
            os.remove(p)
            print('  removed', os.path.basename(p))
        else:
            print('  (not found)', os.path.basename(p))
    print('DONE')


if __name__ == '__main__':
    main()