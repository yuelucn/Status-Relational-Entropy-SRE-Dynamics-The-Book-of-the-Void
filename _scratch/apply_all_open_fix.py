# -*- coding: utf-8 -*-
"""Second pass: finish the all-open rewording for patterns that failed the
first pass because English/typographic hyphen variants (U+2010/U+2011/U+2013)
did not match a plain ASCII '-'. All patterns are matched hyphen-agnostically.
Rules already applied in the first pass simply report MISS here (harmless).
"""
import os, re

ROOT = r'C:/mywork/SRE-Dynamics'
H = '[' + '-' + chr(0x2010) + chr(0x2011) + chr(0x2013) + ']'          # hyphen variants
SP = ('[' + ' ' + chr(0x202f) + chr(0xa0) + chr(0x2009) + chr(0x2007)
      + chr(0x2002) + '-' + chr(0x2006) + ']')                         # space variants (incl. U+202F)
SUFFIX = r'[\s\S]*?'


def lit(s):
    """Escape a literal fragment; make hyphen and space variants tolerant.

    re.escape() escapes spaces as '\\ ' (because of VERBOSE mode), which would
    corrupt the space class. So split on spaces first, escape each token, then
    re-join with the tolerant space class.
    """
    parts = []
    for tok in s.split(' '):
        # re.escape() escapes '-' as '\\-'; swap that escaped hyphen for the class
        parts.append(re.escape(tok).replace('\\-', H))
    return SP.join(parts)


RULES = [
    # preface_E part-III paragraph
    ('preface_E.md',
     lit('Within this part, Operators 1-6 together with the two extension operators 11 and 12 introduced in September 2026 are open-source released to provide mathematical-physical support for the ontological theory;')
     + SUFFIX +
     lit('For these reasons Operators 7-10 are kept closed-source at this stage.'),
     'Within this part, the complete suite of Operators 1-19 is released under an open-source licence to provide full mathematical-physical support for the ontological theory, including the two electronic-degrees-of-freedom extension operators 11 and 12 introduced in September 2026 and the spectral-equation-solving and charge-symbol-channel operators 13-19. The entire pipeline is open-sourced for reproduction, audit and secondary development.',
     'preface_E / part-III paragraph'),

    # Part III abstract (EN) core position
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     lit('Core Position: The SRE operator pipeline adopts real-symmetric matrices of binary spins as its underlying carrier. Operators 1-6 are fully open-source, with rigorous mathematical definitions, equations, theorems and complete proofs provided. Operators 7-10 are closed-source commercial core modules; only interface specifications, input-output behaviour and invariant convergence targets are published, while internal implementations are undisclosed. Operators 11 and 12 are **open-source extension operators** introduced in September 2026, forming the electronic-degrees-of-freedom extension operator set that encodes electronegativity differences and chemical ring topology into the operator pipeline.'),
     '> Core Position: The SRE operator pipeline adopts real‑symmetric matrices of binary spins as its underlying carrier. Operators 1‑19 are fully open‑source, with rigorous mathematical definitions, equations, theorems and complete proofs provided, together with published interface specifications, input‑output behaviour, invariant‑convergence targets and internal implementations. Operators 11 and 12 are the **electronic‑degrees‑of‑freedom extension operators** introduced in September 2026, forming the extension operator set that encodes electronegativity differences and chemical ring topology into the operator pipeline; Operators 13‑19 further form the **spectral‑equation‑solving layer** and the **charge‑symbol / $\\mathbb{Z}_2$ holonomy channel layer**.',
     'part3-E / core position'),

    # Part III abstract (EN) item 1
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     lit('reviews the open-source Operators 1-6; for closed-source commercial Operators 7-10 only black-box interfaces and invariant-convergence targets are exposed;'),
     'reviews the fully open‑source Operators 1‑19;',
     'part3-E / item 1'),

    # Part III abstract (EN) trailing note
    (os.path.join('3-Mathematical_Support', '0‑Abstract_Part_3_E.md'),
     lit('The open-source operators define only mathematical specifications. Large-scale distributed-simulation engineering implementations plus closed-source Operators 7-10 are subjects for subsequent research work.'),
     'Operators 1‑19 are all released open‑source with mathematical specifications and simulation code; large-scale distributed-simulation engineering implementations are subjects for subsequent research work.',
     'part3-E / trailing note'),

    # Operator-4 positioning
    (os.path.join('3-Mathematical_Support', 'Operator_4_1.1_E.md'),
     lit('It belongs to the open-source Operator 1-6 suite; Operators 7-10 are closed-source commercial-core modules and are outside the scope of this document.'),
     'All Operators 1-19 are now released open-source with complete derivations and reference implementations.',
     'Operator_4_1.1_E'),

    # legacy leftover in part-2
    (os.path.join('2-Everything_Emerges', 'Classical_Mechanics_from_Discrete_Causal‑Information_Networks_E_1.0.md'),
     lit('**The full package includes system manuscript, application development, scientific hypotheses, complete algebraic derivations for operators 1-6, and simulation source code, all open-source**. Operators 7, 8, 9, 10 belong to subsequent closed-source commercial core modules and are not included in this document suite.'),
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
            print(f'[MISS] {label}')
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