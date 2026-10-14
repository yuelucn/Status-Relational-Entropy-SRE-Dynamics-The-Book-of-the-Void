import os, re

MV2 = r"c:\mywork\math-graph\math-vector_v2"
DST = r"c:\mywork\SRE-Dynamics\4-Applications&Hypothesis"


def rt(p):
    with open(p, "rb") as f:
        d = f.read()
    if d.startswith(b"\xef\xbb\xbf"):
        d = d[3:]
    return d.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


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


def wt(p, t):
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


AUTHOR = re.compile(r"^\s*(\*\*)?(作者|Author)(\*\*)?\s*[:：]")

PAIRS = [
    ("SRE_19_operators_graph500_article_2.1_C.md", "Graph500_2.1_C.md"),
    ("SRE_19_operators_graph500_article_2.1_E.md", "Graph500_2.1_E.md"),
]

for sname, dname in PAIRS:
    src = os.path.join(MV2, sname)
    dst = os.path.join(DST, dname)
    t = rt(src)
    out = "\n".join(ln for ln in t.split("\n") if not AUTHOR.match(ln))
    n = count_h1(out)
    assert n == 1, "H1=%d for %s" % (n, sname)
    wt(dst, out)
    print("OK", dname, "chars", len(out), "H1", n, "authorline_removed", t.count("\n") - out.count("\n"))
print("DONE")
