"""Add the new turbulence paper (v4.0) companion artifacts into the book appendix."""
import os
import shutil

SRC = r"c:\mywork\wei"
APX = r"c:\mywork\SRE-Dynamics\5-Appendixs\Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence"

CODE = [
    "frontier_profile.py",
    "beta38_v13_final.py",
    "sre_ns_benchmark.py",
]
DATA = [
    "beta38_final_local.pkl",
    "beta38_N12800.pkl",
    "beta38_N12800_seed2.pkl",
    "beta38_N25600.pkl",
    "beta38_N25600_partial_C.json",
    "beta38_v13_final_output.txt",
]
ANALYSIS = ["sre_ns_benchmark.png"]
PAPERS_MD = [("n-s_C_4.0.md", "main_CN.md"), ("n-s_E_4.0.md", "main_EN.md")]
PAPERS_BIN = ["n-s_C_4.0.pdf", "n-s_E_4.0.pdf"]


def copy_bin(name, dst):
    shutil.copyfile(os.path.join(SRC, name), dst)
    print("  bin  %-34s -> %s" % (name, os.path.relpath(dst, APX)))


def copy_text(name, dst):
    with open(os.path.join(SRC, name), "rb") as f:
        t = f.read().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    with open(dst, "wb") as f:
        f.write(t.encode("utf-8"))
    print("  text %-34s -> %s" % (name, os.path.relpath(dst, APX)))


for name in CODE:
    copy_text(name, os.path.join(APX, "code", name))
for name in DATA:
    if name.endswith((".pkl", ".png")):
        copy_bin(name, os.path.join(APX, "data", name))
    else:
        copy_text(name, os.path.join(APX, "data", name))
for name in ANALYSIS:
    copy_bin(name, os.path.join(APX, "analysis", name))
for src, dst in PAPERS_MD:
    copy_text(src, os.path.join(APX, "papers", dst))
for name in PAPERS_BIN:
    copy_bin(name, os.path.join(APX, "papers", name))

print("DONE")
