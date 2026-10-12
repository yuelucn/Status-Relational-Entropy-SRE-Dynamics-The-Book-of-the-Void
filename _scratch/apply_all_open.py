# -*- coding: utf-8 -*-
"""Turn every operator open/closed-source statement in the book into the
'uniformly open-source (Operators 1-19)' wording the author has decided on.

Only statement/positioning wording is touched. Technical uses of 'black-box'
(e.g. black-box numerical VJP, black-box GNN embeddings) are left alone.
"""
import os, re, sys

ROOT = r'C:/mywork/SRE-Dynamics'
P3 = os.path.join(ROOT, '3-Mathematical_Support')
P2 = os.path.join(ROOT, '2-Everything_Emerges')
APP = os.path.join(ROOT, '5-Appendixs', 'SRE_Time_Emergence')

# (relative path, regex, replacement, label)
RULES = [
    # ---- preface (CN) ----
    ('preface_C.md',
     r'\*\*算子体系的开源范围\*\*：算子 1-6、11、12 的完整数学规范、代数推导与仿真代码全部开源，构成本书第三部分与第五部分的主体内容；算子 7、8、9、10 属于后续闭源商业核心模块，其内部实现不予披露，仅在第三部分公开接口规范、输入输出与不变量收敛目标。',
     '**算子体系的开源范围**：算子 1-19 的完整数学规范、代数推导与仿真代码全部开源，构成本书第三部分与第五部分的主体内容，整套流水线以开源许可发布，供复现、审计与二次开发。',
     'preface_C / open-source scope'),
    ('preface_C.md',
     r'本部分开源发布1-6号算子及2026年9月新增的11、12号扩展算子，可为本本体理论提供数理支撑；7-10号算子选择闭源。[\s\S]*?因此现阶段选择将7-10号算子予以闭源。',
     '本部分以开源方式完整发布 1-19 号全套算子，包括 2026 年 9 月新增的 11、12 号电子自由度扩展算子，以及 13-19 号谱形方程求解与电荷符号通道算子，为本书本体理论提供完整的数理支撑。整套算子流水线以开源许可发布，供同行复现、审计与二次开发。',
     'preface_C / part-III paragraph'),

    # ---- preface (EN) ----
    ('preface_E.md',
     r'\*\*Open-source scope of the operator suite\*\*: the complete mathematical specifications, algebraic derivations and simulation code for Operators 1-6, 11 and 12 are fully open-source, and constitute the main body of Parts III and V of this book\. Operators 7, 8, 9 and 10 are subsequent closed-source commercial core modules whose internal implementations are not disclosed; only their interface specifications, input-output behaviour and invariant-convergence targets are published in Part III\.',
     '**Open-source scope of the operator suite**: the complete mathematical specifications, algebraic derivations and simulation code for all Operators 1-19 are fully open-source, and constitute the main body of Parts III and V of this book. The entire operator pipeline is released under an open-source licence for reproduction, audit and secondary development.',
     'preface_E / open-source scope'),
    ('preface_E.md',
     r'Within this part, Operators 1-6 together with the two extension operators 11 and 12 introduced in September 2026 are open-source released to provide mathematical-physical support for the ontological theory; Operators 7-10 remain closed-source\.[\s\S]*?For these reasons Operators 7-10 are kept closed-source at this stage\.',
     'Within this part, the complete suite of Operators 1-19 is released under an open-source licence to provide full mathematical-physical support for the ontological theory, including the two electronic-degrees-of-freedom extension operators 11 and 12 introduced in September 2026 and the spectral-equation-solving and charge-symbol-channel operators 13-19. The entire pipeline is open-sourced for reproduction, audit and secondary development.',
     'preface_E / part-III paragraph'),

    # ---- Part III abstract (CN) ----
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_C.md'),
     r'> 核心立场：SRE算子流水线以二元自旋实对称矩阵作为底层载体；算子1‑6全部开源，给出严格数学定义、方程、定理与完备证明；算子7‑10属于闭源商业核心模块，仅公开接口规范、输入输出与不变量收敛目标，不披露内部实现。算子11、12为2026年9月新增的\*\*开源扩展算子\*\*，构成电子自由度扩展算子组，负责把电负性差异与化学环拓扑编码进算子流水线。',
     '> 核心立场：SRE算子流水线以二元自旋实对称矩阵作为底层载体；算子1‑19全部开源，给出严格数学定义、方程、定理与完备证明，并公开接口规范、输入输出、不变量收敛目标及内部实现。算子11、12为2026年9月新增的**电子自由度扩展算子**，构成电子自由度扩展算子组，负责把电负性差异与化学环拓扑编码进算子流水线；算子13‑19进一步构成**谱形方程求解层**与**电荷符号 / $\\mathbb{Z}_2$ holonomy 通道层**。',
     'part3-C / core position'),
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_C.md'),
     r'算子1‑6开源部分完整复盘；算子7‑10闭源商业组件仅公开黑盒接口、不变量收敛目标；',
     '算子1‑19全开源、完整复盘；',
     'part3-C / item 1'),
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_C.md'),
     r'开源算子仅定义数学规范；大规模分布式仿真工程实现、以及算子7‑10闭源组件属于后续研发工作。',
     '算子 1‑19 均以开源方式发布数学规范与仿真代码；大规模分布式仿真工程实现属于后续研发工作。',
     'part3-C / trailing note'),

    # ---- Part III abstract (EN) ----
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     r'> Core Position: The SRE operator pipeline adopts real‑symmetric matrices of binary spins as its underlying carrier\. Operators 1‑6 are fully open‑source, with rigorous mathematical definitions, equations, theorems and complete proofs provided\. Operators 7‑10 are closed‑source commercial core modules; only interface specifications, input‑output behaviour and invariant convergence targets are published, while internal implementations are undisclosed\. Operators 11 and 12 are \*\*open‑source extension operators\*\* introduced in September 2026, forming the electronic‑degrees‑of‑freedom extension operator set that encodes electronegativity differences and chemical ring topology into the operator pipeline\.',
     '> Core Position: The SRE operator pipeline adopts real‑symmetric matrices of binary spins as its underlying carrier. Operators 1‑19 are fully open‑source, with rigorous mathematical definitions, equations, theorems and complete proofs provided, together with published interface specifications, input‑output behaviour, invariant‑convergence targets and internal implementations. Operators 11 and 12 are the **electronic‑degrees‑of‑freedom extension operators** introduced in September 2026, forming the extension operator set that encodes electronegativity differences and chemical ring topology into the operator pipeline; Operators 13‑19 further form the **spectral‑equation‑solving layer** and the **charge‑symbol / $\\mathbb{Z}_2$ holonomy channel layer**.',
     'part3-E / core position'),
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     r'reviews the open‑source Operators 1‑6; for closed‑source commercial Operators 7‑10 only black‑box interfaces and invariant‑convergence targets are exposed;',
     'reviews the fully open‑source Operators 1‑19;',
     'part3-E / item 1'),
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     r'The open‑source operators define only mathematical specifications\. Large‑scale distributed‑simulation engineering implementations plus closed‑source Operators 7‑10 are subjects for subsequent research work\.',
     'Operators 1‑19 are all released open‑source with mathematical specifications and simulation code; large‑scale distributed‑simulation engineering implementations are subjects for subsequent research work.',
     'part3-E / trailing note'),

    # ---- Operator-1 interpretation statement ----
    (os.path.join('3-Mathematical_Support', 'Operator_1_Interpretation_C.md'),
     r'该框架全部理论资料均存档于 Zenodo 开源数据仓库。除算子 7、8、9、10 为闭源商业核心\s*\n?\s*模块之外，全套系统论文、算子 1‐6 完整代数推导过程以及仿真代码均完全开源。',
     '该框架全部理论资料均存档于 Zenodo 开源数据仓库。全套系统论文、算子 1-19 完整代数推导过程以及仿真代码均完全开源。',
     'Operator_1_Interpretation_C'),
    (os.path.join('3-Mathematical_Support', 'Operator_1_Interpretation_E.md'),
     r'Except for the closed-source commercial engineering implementation modules corresponding to Operators 7, 8, 9 and 10, the mathematical-specification papers, algebraic derivations and simulation codes for Operators 1-6 are fully open-source\.',
     'The mathematical-specification papers, algebraic derivations and simulation codes for all Operators 1-19 are fully open-source.',
     'Operator_1_Interpretation_E'),

    # ---- Operator-4 positioning ----
    (os.path.join('3-Mathematical_Support', 'Operator_4_1.1_E.md'),
     r'It belongs to the open-source Operator 1-6 suite; Operators 7-10 are closed-source commercial-core modules and are outside the scope of this document\.',
     'All Operators 1-19 are now released open-source with complete derivations and reference implementations.',
     'Operator_4_1.1_E'),

    # ---- Nucleon v2.1 (EN statement) ----
    (os.path.join('2-Everything_Emerges', 'SRE_Nucleon_Complete_Paper_2.1_E.md'),
     r'\*\*This document suite includes system papers, application development, scientific hypotheses, operators 1-6,11,12 complete algebraic derivations and simulation code fully open source\*\*; operators 7, 8, 9, 10,13-18 belong to subsequent closed-source commercial core modules,\s*\n?> and are not included in this document suite\.',
     '**This document suite includes system papers, application development, scientific hypotheses, and the complete algebraic derivations and simulation code for all operators 1-19, fully open source**.',
     'SRE_Nucleon_Complete_Paper_2.1_E'),

    # ---- Time-emergence appendix abstract ----
    (os.path.join('5-Appendixs', 'SRE_Time_Emergence', 'SRE_时间涌现_摘要.md'),
     r'\*\*本文档套件包括系统论文、应用开发、科学假说、算子1‑6,11,12完整代数推导及仿真代码完全开源\*\*；算子7、8、9、10、13-18 属于后续闭源商业核心模块，不在本文档套件范围内。',
     '**本文档套件包括系统论文、应用开发、科学假说、算子1-19完整代数推导及仿真代码完全开源**。',
     'SRE_Time_Emergence appendix abstract'),

    # ---- legacy leftover in part-2 (not in manifest, kept consistent) ----
    (os.path.join('2-Everything_Emerges', 'Classical_Mechanics_from_Discrete_Causal‑Information_Networks_E_1.0.md'),
     r'\*\*The full package includes system manuscript, application development, scientific hypotheses, complete algebraic derivations for operators 1-6, and simulation source code, all open-source\*\*\. Operators 7, 8, 9, 10 belong to subsequent closed-source commercial core modules and are not included in this document suite\.',
     '**The full package includes system manuscript, application development, scientific hypotheses, and complete algebraic derivations for all operators 1-19, with simulation source code, all open-source**.',
     'legacy Classical_Mechanics_E_1.0'),
]


def main():
    cache = {}
    for rel, pat, rep, label in RULES:
        p = os.path.join(ROOT, rel)
        if p not in cache:
            with open(p, 'r', encoding='utf-8-sig') as f:
                cache[p] = f.read()
        txt = cache[p]
        cnt = len(re.findall(pat, txt))
        if cnt == 0:
            print(f'[MISS] {label}  ({rel})')
            continue
        txt = re.sub(pat, rep.replace('\\', '\\\\'), txt)
        cache[p] = txt
        print(f'[OK x{cnt}] {label}')

    for p, txt in cache.items():
        with open(p, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(txt)
    print('written', len(cache), 'files')


if __name__ == '__main__':
    main()