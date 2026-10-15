import os
import subprocess

B = r"c:\mywork\SRE-Dynamics"
A4 = os.path.join(B, "4-Applications&Hypothesis")


def find(prefix, suffix):
    for n in os.listdir(A4):
        if n.startswith(prefix) and n.endswith(suffix):
            return os.path.join(A4, n)
    raise SystemExit("not found: %s*%s" % (prefix, suffix))


paths = [
    find("0", "Abstract_Part_4_C.md"),
    find("0", "Abstract_Part_4_E.md"),
    os.path.join(A4, "SRE-AI_1.0_C.md"),
    os.path.join(A4, "SRE-AI_1.0_E.md"),
    os.path.join(A4, "SRE-AI_2.0_C.md"),
    os.path.join(A4, "SRE-AI_2.0_E.md"),
    os.path.join(B, "5-Appendixs", "SRE-AI", "results.zip"),
    os.path.join(B, "5-Appendixs", "SRE-AI", "sre_ai_model_release_v2.0.zip"),
    os.path.join(B, "combined_C.md"),
    os.path.join(B, "combined_E.md"),
    os.path.join(B, "file_order_C.txt"),
    os.path.join(B, "file_order_E.txt"),
    os.path.join(B, "SRE-Dynamics-Book-v1_C.pdf"),
    os.path.join(B, "SRE-Dynamics-Book-v1_E.pdf"),
    os.path.join(B, "_scratch", "replace_sre_ai.py"),
    os.path.join(B, "_scratch", "update_abstract_p4.py"),
]

r = subprocess.run(["git", "add", "--"] + paths, cwd=B, capture_output=True, text=True)
print("add rc", r.returncode)
print(r.stdout.strip())
print(r.stderr.strip())
r2 = subprocess.run(["git", "status", "--short"], cwd=B, capture_output=True, text=True)
print("---- status ----")
print(r2.stdout)
