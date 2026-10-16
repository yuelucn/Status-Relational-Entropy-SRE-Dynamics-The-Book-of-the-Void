"""Stage the turbulence v4.0 sync for commit."""
import subprocess

B = r"c:\mywork\SRE-Dynamics"
APX = r"5-Appendixs\Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence"

paths = [
    r"2-Everything_Emerges",
    r"4-Applications&Hypothesis\Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_C.md",
    r"4-Applications&Hypothesis\Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_E.md",
    APX,
    "file_order_C.txt",
    "file_order_E.txt",
    "combined_C.md",
    "combined_E.md",
    "SRE-Dynamics-Book-v1_C.pdf",
    "SRE-Dynamics-Book-v1_E.pdf",
    r"_scratch\replace_turbulence.py",
    r"_scratch\fix_shield_xrefs.py",
    r"_scratch\add_turbulence_appendix.py",
]

r = subprocess.run(["git", "add", "--"] + paths, cwd=B, capture_output=True, text=True)
print("add rc", r.returncode, r.stderr.strip())
r = subprocess.run(["git", "status", "--short"], cwd=B, capture_output=True, text=True)
print(r.stdout)
print("---- staged count ----")
r = subprocess.run(["git", "diff", "--cached", "--name-status"], cwd=B, capture_output=True, text=True)
print(len(r.stdout.splitlines()), "entries")
