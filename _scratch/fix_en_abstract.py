# -*- coding: utf-8 -*-
import glob

files = glob.glob('2-Everything_Emerges/0*Abstract_Part_2_E.md')
assert files, 'EN abstract not found'
p = files[0]
t = open(p, encoding='utf-8').read()

# 1) N-S version bump
t = t.replace('(v2.0 revised)', '(v3.0 revised)', 1)

# 2) append v3 note after entry-6 ending (ASCII anchor)
anchor6 = 'calibration for fluid systems is reserved for future work.'
if anchor6 in t:
    note6 = (' Version 3 further corrects v2 via a program-correctness gate '
             '(reproduce_ns62.py reproduces the section 6.2 phase diagram to Delta<=1e-4) '
             'and two prior verifications (verify_paper_claims.py): it recasts Psi in logarithmic '
             'form and closes the loop with verify_dissipation.py (error <=1.1 percent); it supplements '
             'an analytic finite-size convergence mechanism (dissipation master equation -> universal '
             'curve C(z), beta_infinity=0, via beta_dissipation_theory.py), and uses large-N extrapolation '
             'to refute the persistent-steepening claim.')
    t = t.replace(anchor6, anchor6 + note6, 1)

# 3) nucleon version bump
t = t.replace('ontological account of the nucleon (v1.5)', 'ontological account of the nucleon (v2.1)', 1)

# 4) append v2.1 note inside entry 10 (match exact existing fragment with U+2011)
old10 = '8/8 on the 8\u2011entry scorecard)'
new10 = ('8/8 on the 8\u2011entry scorecard); Version 2.1 further adds a "contextual-limitations" '
         'boundary statement and extends the configuration-level test of the electronic-state '
         'objection (S1\u2013S4 rerun, S2\u2245S1) and the disproof of "boson = transition quantum"')
if old10 in t:
    t = t.replace(old10, new10, 1)
else:
    print('WARN: entry-10 anchor not found (v2.1 note not added)')

# 5) insert entries 14 and 15 before closing blockquote
anchor_bq = '> This suite inherits the axiomatic foundations of Part'
if anchor_bq in t:
    e14 = ('14. **A Plain-Language Version of the Emergence of Time in the SRE Framework**: '
           'A plain-language rewrite of the time-ontology paper Emergence of Time in the SRE Framework, '
           'aimed at general science-and-engineering readers. It preserves every core conclusion and datum, '
           'replacing project-internal jargon with everyday language and analogies; the seven verdicts '
           '(saturation law, universality, incompatibility of two clocks, etc.) and the structure-without-memory '
           'semantic separation are retold non-technically, and the three honest boundaries (notably emergent '
           'time has shape but no scale) are retained. Reproduction scripts are shared with the technical version '
           '(appendix SRE_Time_Emergence).')
    e15 = ('15. **Emergence of Positive and Negative Electric Charge in the SRE Framework: Magnitude, Sign, and '
           'Numerical Verification**: A paper closing the sign gap of charge. SRE expresses charge as the counting '
           'of topological knots (magnitude only); this paper rigorously gives Q(K)=sigma(K) middot deg(K) middot e, '
           'yielding electron Q=-e, positron Q=+e, proton Q=+e, neutron Q=0, antiproton Q=-e, and explaining the '
           'charge-mass decoupling (proton and electron share the same magnitude but differ in mass by about 1836 times). '
           'Two numerical tests confirm: the sign channel and the magnitude channel are mutually independent '
           '(section 10.1); the electron is forced by skeleton symmetry into the trivial holonomy class while the '
           'proton lands in the non-trivial class (section 10.2), giving the electron/proton sign opposition a '
           'structural origin.')
    t = t.replace(anchor_bq, '\n' + e14 + '\n\n' + e15 + '\n\n' + anchor_bq, 1)

open(p, 'w', encoding='utf-8').write(t)
print('EN abstract updated:', p)
