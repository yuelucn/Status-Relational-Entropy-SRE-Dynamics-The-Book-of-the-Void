# -*- coding: utf-8 -*-
"""Sync Oct-2026 paper updates into SRE-Dynamics book.

Items:
 1. N-S  turbulence  v2.0 -> v3.0  (replace existing chapter)
 2. Time emergence plain-language  (NEW chapter, supplement to time emergence)
 3. Nucleon  v1.5 -> v2.1  (replace existing chapter)
 4. Charge sign emergence  (NEW chapter)
"""
import os, re, shutil, glob

ROOT = r'C:/mywork/SRE-Dynamics'
PART2 = os.path.join(ROOT, '2-Everything_Emerges')
APPX = os.path.join(ROOT, '5-Appendixs')
WEI = r'C:/mywork/wei'
VASP = r'C:/mywork/vasp'
CHARGE = os.path.join(VASP, 'SRE-charge-emergence')

SRC = {
    'ns_c':  os.path.join(WEI, 'n-s_C_3.0.md'),
    'ns_e':  os.path.join(WEI, 'n-s_E_3.0.md'),
    'nuc_c': os.path.join(VASP, 'SRE_Nucleon_Complete_Paper.md'),
    'nuc_e': os.path.join(VASP, 'SRE_Nucleon_Complete_Paper_EN.md'),
    'tp_c':  os.path.join(VASP, 'SRE_时间涌现_通俗版.md'),
    'tp_e':  os.path.join(VASP, 'SRE_Time_Emergence_Plain_EN.md'),
    'ch_c':  os.path.join(CHARGE, 'SRE_charge_emergence_C.md'),
    'ch_e':  os.path.join(CHARGE, 'SRE_charge_emergence_E.md'),
}

DST = {
    'ns_c':  os.path.join(PART2, 'Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence_3.0_C.md'),
    'ns_e':  os.path.join(PART2, 'Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence_3.0_E.md'),
    'nuc_c': os.path.join(PART2, 'SRE_Nucleon_Complete_Paper_2.1_C.md'),
    'nuc_e': os.path.join(PART2, 'SRE_Nucleon_Complete_Paper_2.1_E.md'),
    'tp_c':  os.path.join(PART2, 'SRE_Time_Emergence_Plain_1.0_C.md'),
    'tp_e':  os.path.join(PART2, 'SRE_Time_Emergence_Plain_1.0_E.md'),
    'ch_c':  os.path.join(PART2, 'SRE_charge_emergence_1.0_C.md'),
    'ch_e':  os.path.join(PART2, 'SRE_charge_emergence_1.0_E.md'),
}

OLD_FILES = [
    os.path.join(PART2, 'Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence_2.0_C.md'),
    os.path.join(PART2, 'Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence_2.0_E.md'),
    os.path.join(PART2, 'SRE_Nucleon_Complete_Paper_1.5_C.md'),
    os.path.join(PART2, 'SRE_Nucleon_Complete_Paper_1.5_E.md'),
]


def read_text(p):
    with open(p, 'r', encoding='utf-8-sig') as f:
        return f.read()


def write_text(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


def remove_block(text, start_marker, end_marker):
    lines = text.split('\n')
    si = ei = None
    for i, l in enumerate(lines):
        if si is None and start_marker in l:
            si = i
        if si is not None and end_marker in l:
            ei = i
            break
    if si is not None and ei is not None:
        del lines[si:ei + 1]
        return '\n'.join(lines), (si, ei)
    return '\n'.join(lines), None


def remove_line_containing(text, substr):
    lines = text.split('\n')
    out = [l for l in lines if substr not in l]
    return '\n'.join(out)


def count_h1(text):
    in_fence = False
    n = 0
    for line in text.split('\n'):
        if line.strip().startswith('```') or line.strip().startswith('~~~'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r'^#\s+\S', line):
            n += 1
    return n


# ---- per-file cleaners -------------------------------------------------
def clean_ns_c(t):
    t = remove_line_containing(t, '**作者: 岳路**')
    t, blk = remove_block(t, '【资源与可用性声明】', '经典物理基础源自信息统计学')
    t = t.replace('**版本: v3（修订版）**', '版本: 3.0（修订版）')
    t = t.replace('交互验证：sre_phase_console.html', '交互验证：sim/sre_phase_console.html')
    return t


def clean_ns_e(t):
    t = remove_line_containing(t, '**Author: Yue Lu**')
    t, blk = remove_block(t, '[Resources and Availability Statement]', 'foundations of classical physics originate from information statistics')
    t = t.replace('**Version: v3 (Revised)**', 'Version: 3.0 (Revised)')
    t = t.replace('Interactive verification: sre_phase_console.html', 'Interactive verification: sim/sre_phase_console.html')
    return t


def clean_nuc_c(t):
    t = re.sub(r'\*\*作者：岳路\*\*\s*', '', t)
    t, blk = remove_block(t, '【资源与可获得性声明】', '经典物理基础源自信息统计学')
    return t


def clean_nuc_e(t):
    t = re.sub(r'\*\*Author: Yue Lu\*\*\s*', '', t)
    t, blk = remove_block(t, '[Resource and Availability Statement]', 'foundations of classical physics originate from information statistics')
    return t


def clean_tp_c(t):
    lines = t.split('\n')
    for i, l in enumerate(lines):
        if '作者：岳路' in l and '版本：1.0（通俗改写版）' in l:
            lines[i] = '版本：1.0（通俗改写版）\n原技术版日期：2026-10-04'
            break
    return '\n'.join(lines)


def clean_tp_e(t):
    lines = t.split('\n')
    for i, l in enumerate(lines):
        if 'Author: Yue Lu' in l and 'Version: 1.0 (plain-language rewrite)' in l:
            lines[i] = 'Version: 1.0 (plain-language rewrite)\nOriginal technical version dated: 2026-10-04'
            break
    return '\n'.join(lines)


def clean_ch_c(t):
    t = remove_line_containing(t, '作者: 岳路')
    t, blk = remove_block(t, '【资源与可用性声明】', '经典物理基础源自信息统计学')
    t = t.replace('《SRE框架下核子的完整刻画》v1.5', '《SRE框架下核子的完整刻画》v2.1')
    return t


def clean_ch_e(t):
    t = remove_line_containing(t, 'Author: Yue Lu')
    t, blk = remove_block(t, '[Resources and Availability Statement]', 'foundations of classical physics originate from information statistics')
    t = t.replace('Framework* v1.5', 'Framework* v2.1')
    return t


CLEAN = {
    'ns_c': clean_ns_c, 'ns_e': clean_ns_e,
    'nuc_c': clean_nuc_c, 'nuc_e': clean_nuc_e,
    'tp_c': clean_tp_c, 'tp_e': clean_tp_e,
    'ch_c': clean_ch_c, 'ch_e': clean_ch_e,
}


def main():
    print('=== generating chapter files ===')
    for key in DST:
        t = read_text(SRC[key])
        t = CLEAN[key](t)
        write_text(DST[key], t)
        print(f'  {os.path.basename(DST[key])}: H1={count_h1(t)}')

    # remove superseded old files
    print('=== removing superseded files ===')
    for p in OLD_FILES:
        if os.path.exists(p):
            os.remove(p)
            print('  removed', os.path.basename(p))

    # ---- appendix: N-S v3.0 scripts ----
    print('=== N-S appendix scripts ===')
    ns_appx = os.path.join(APPX, 'Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence')
    ns_code = [
        'sre_core.py', 'reproduce_ns62.py', 'verify_paper_claims.py',
        'beta_dissipation_theory.py', 'verify_dissipation.py', 'N-S.py',
        'export_v2.py', 'make_tables.py',
    ]
    for f in ns_code:
        sp = os.path.join(WEI, f)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(ns_appx, 'code', f))
            print('  code/', f)
    for f in ['phase_data_v2.json']:
        sp = os.path.join(WEI, f)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(ns_appx, 'data', f))
            print('  data/', f)
    sp = os.path.join(WEI, 'sre_phase_console.html')
    if os.path.exists(sp):
        shutil.copy2(sp, os.path.join(ns_appx, 'sim', 'sre_phase_console.html'))
        print('  sim/sre_phase_console.html')

    # ---- appendix: nucleon v2.1 figures + scripts ----
    print('=== nucleon figures ===')
    nuc_appx = os.path.join(APPX, 'SRE_Nucleon_Complete_Paper')
    fig_bases = ['sre_nucleon_skeleton_structure', 'sre_nucleon_skeleton_funnel', 'sre_nucleon_manybody_schematic']
    for base in fig_bases:
        for ext in ('.png', '.svg'):
            sp = os.path.join(VASP, 'figures', base + ext)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(ROOT, 'figures', base + ext))
                shutil.copy2(sp, os.path.join(PART2, 'figures', base + ext))
                shutil.copy2(sp, nuc_appx)
                print('  fig', base + ext)
    print('=== nucleon scripts (sync from vasp root) ===')
    nuc_patterns = ['_sre_nucleon*.py', '_sre_anchor_registry.py', '_sre_boson_transition.py',
                    '_sre_fission_chain*.py', '_sre_dimension_collapse*.py', '_enum_cubic12.py',
                    '_sre_nucleon_derivation.py', '_sre_sharedring*.py', '_sre_dimer*.py',
                    '_sre_nucleon_ec_env_test.py', '_sre_nucleon_latin_ckm.py']
    copied = set()
    for pat in nuc_patterns:
        for sp in glob.glob(os.path.join(VASP, pat)):
            name = os.path.basename(sp)
            if name in copied:
                continue
            shutil.copy2(sp, os.path.join(nuc_appx, name))
            copied.add(name)
    print(f'  nucleon scripts copied: {len(copied)}')

    # ---- appendix: charge emergence (NEW) ----
    print('=== charge appendix ===')
    ch_appx = os.path.join(APPX, 'SRE_charge_emergence')
    os.makedirs(ch_appx, exist_ok=True)
    for f in ['_sigma_deg_independence.py', '_se_assignment_test.py', '_nucleon_multibody_charge.py']:
        sp = os.path.join(CHARGE, f)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(ch_appx, f))
            print('  ', f)
    print('DONE')


if __name__ == '__main__':
    main()
