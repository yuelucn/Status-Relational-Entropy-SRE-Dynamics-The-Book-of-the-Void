import os, re

SRC_DIR = r"c:\mywork\math-graph\math-vector_v2\sre_ai_model\release"
DST_DIR = r"c:\mywork\SRE-Dynamics\4-Applications&Hypothesis"
B = r"c:\mywork\SRE-Dynamics"


def rt(p):
    with open(p, "rb") as f:
        d = f.read()
    if d.startswith(b"\xef\xbb\xbf"):
        d = d[3:]
    return d.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def wt(p, t):
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


def count_h1(t):
    n = 0
    fence = False
    for line in t.split("\n"):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence
            continue
        if fence:
            continue
        if s.startswith("# ") or s == "#":
            n += 1
    return n


AUTHOR = re.compile(r"^\s*(\*\*)?(作者|Author)(\*\*)?\s*[:：]")

PAIRS = [
    ("SRE_AI_Model_C.md", "SRE-AI_2.0_C.md", "SRE-AI_1.0_C.md"),
    ("SRE_AI_Model_E.md", "SRE-AI_2.0_E.md", "SRE-AI_1.0_E.md"),
]

for sname, newname, oldname in PAIRS:
    t = rt(os.path.join(SRC_DIR, sname))
    out = "\n".join(ln for ln in t.split("\n") if not AUTHOR.match(ln))
    n = count_h1(out)
    assert n == 1, "H1=%d in %s" % (n, sname)
    wt(os.path.join(DST_DIR, newname), out)
    print("WROTE", newname, "chars", len(out), "H1", n)
    op = os.path.join(DST_DIR, oldname)
    if os.path.exists(op):
        os.remove(op)
        print("REMOVED", oldname)

for fo, old, new in [
    ("file_order_C.txt", "SRE-AI_1.0_C.md", "SRE-AI_2.0_C.md"),
    ("file_order_E.txt", "SRE-AI_1.0_E.md", "SRE-AI_2.0_E.md"),
]:
    p = os.path.join(B, fo)
    t = rt(p)
    assert old in t, old + " not found in " + fo
    wt(p, t.replace(old, new))
    print("ORDER", fo, "->", new)

print("DONE")
