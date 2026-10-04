# -*- coding: utf-8 -*-
"""《SRE 体系下的质量起源》v2.0 全部读数核对（纯复核，不产生新结论）。

复用项目既有闭式：code/_sre_anchor_registry.py 的 mobius_pi1。
运行：C:/myapp/miniconda3/envs/ai/python.exe -u _sre_paper_v2_check.py
"""
import numpy as np, math, cmath, json
from math import gcd
import networkx as nx

W = cmath.exp(2j*math.pi/3)
OUT = {}
def P(*s): print(*s, flush=True)

ALPHA = 7.2973525693e-3          # 精细结构常数 (CODATA)
m_e, m_mu = 0.51099895069, 105.6583755

P("="*72); P("SRE Mass-Origin Paper v2.0  ---  numeric cross-check"); P("="*72)

# ---------------- 例 1 与定理 3 ----------------
P("\n[例1 & 定理3]  u=(1, 1.2, 0.7)")
u = np.array([1.0, 1.2, 0.7])
z = sum(u[k]*W**(-k) for k in range(3))
mu_ = u.mean(); c1_ = abs(z)/3.0; th_ = (-cmath.phase(z)) % (2*math.pi)
rec = np.array([mu_ + 2*c1_*math.cos(th_ + 2*math.pi*k/3) for k in range(3)])
P("  mean=%.6f  |z|=%.6f  |c1|=%.6f  theta=%.6f rad" % (mu_, abs(z), c1_, th_))
P("  recon =", np.round(rec, 6), "  multiset match =", sorted(np.round(rec, 8)) == sorted(u.tolist()))
errs = []
rng = np.random.default_rng(7)
for _ in range(8):
    a = rng.uniform(-5, 5, 3)
    zz = sum(a[k]*W**(-k) for k in range(3))
    m0 = a.mean(); q1 = abs(zz)/3.0; t0 = (-cmath.phase(zz)) % (2*math.pi)
    r = np.array([m0 + 2*q1*math.cos(t0 + 2*math.pi*k/3) for k in range(3)])
    errs.append(np.abs(np.sort(r) - np.sort(a)).max())
P("  随机8组 反解-重构 最大误差 = %.3e" % max(errs))
OUT["ex1"] = dict(mean=float(mu_), absz=float(abs(z)), c1=float(c1_), theta=float(th_),
                  recon=rec.tolist(), maxerr=float(max(errs)))

# ---------------- 例 2 ----------------
P("\n[例2]  c0=1, c1=0.3 e^{i40deg}")
t40 = math.radians(40.0)
lam = np.sort([1.0 + 2*0.3*math.cos(t40 + 2*math.pi*k/3) for k in range(3)])
A = np.array([[1.0, 0.3*np.exp(1j*t40), 0.3*np.exp(-1j*t40)],
              [0.3*np.exp(-1j*t40), 1.0, 0.3*np.exp(1j*t40)],
              [0.3*np.exp(1j*t40), 0.3*np.exp(-1j*t40), 1.0]], dtype=complex)
ev = np.sort(np.linalg.eigvalsh(A).real)
P("  analytic(升序) =", ["%.6f" % x for x in lam])
P("  eig(实测,升序) =", ["%.6f" % x for x in ev])
OUT["ex2"] = dict(analytic=lam.tolist(), eig=ev.tolist())

# ---------------- 例 3 / 表 10 / 表 11 ----------------
P("\n[例3 & 表10 & 表11]  带电轻子")
res = {}
for mtau in (1776.86, 1776.93):
    m = np.array([m_e, m_mu, mtau])
    sm, ss = float(m.sum()), float(np.sqrt(m).sum())
    Q = sm/ss**2; e2 = (3*Q-1)/2
    phi = math.degrees(math.acos(np.sqrt(m).sum()/(np.linalg.norm(np.sqrt(m))*math.sqrt(3))))
    res[mtau] = dict(Q=Q, eta2=e2, ssum=ss, sum=sm, phi=phi)
    P("  m_tau=%.2f: sum(m)=%.9f  sum(sqrt m)=%.9f" % (mtau, sm, ss))
    P("             Q=%.9f  eta^2=%.9f  dev=%.3e  phi=%.4f deg" % (Q, e2, Q-2/3, phi))
Q = res[1776.93]["Q"]; eta = math.sqrt((3*Q-1)/2)
P("  eta = %.9f   1/sqrt2 = %.9f   dev = %.3e" % (eta, 1/math.sqrt(2), eta-1/math.sqrt(2)))
m = np.array([m_e, m_mu, 1776.93]); a0 = float(np.sqrt(m).mean())
uk = (np.sqrt(m)/a0 - 1)/math.sqrt(2)
d_asc = cmath.phase(sum(uk[k]*W**(-k) for k in range(3))) % (2*math.pi/3)
ukd = uk[::-1]
d_des = cmath.phase(sum(ukd[k]*W**(-k) for k in range(3))) % (2*math.pi/3)
P("  相位 升序 delta=%.9f (vs 2/9, dev=%+.3e)" % (d_asc, d_asc-2/9))
P("  相位 降序 delta=%.9f (dev=%+.3e)" % (d_des, d_des-2/9))
OUT["ex3"] = {str(k): v for k, v in res.items()}
OUT["phase"] = dict(asc=float(d_asc), desc=float(d_des), ref=2/9, eta=float(eta))

# ---------------- alpha 锚 ----------------
P("\n[§11.3]  alpha 锚：Π₁(M_60)（复用 code/_sre_anchor_registry.py 闭式）")
def mobius_pi1(n, w=1.0):
    x = 2.0*np.pi/n
    return 4.0*np.sin(x)**2/(2.0 + 2.0*w + 2.0*np.cos(x))
pi60 = float(mobius_pi1(60))
P("  Pi1(M_60, w=1) = %.12e" % pi60)
P("  alpha (CODATA) = %.12e" % ALPHA)
P("  相对偏差       = %.3e" % (abs(pi60-ALPHA)/ALPHA))
lo, hi = 40.0, 90.0
for _ in range(200):
    mid = (lo+hi)/2
    if (mobius_pi1(lo)-ALPHA)*(mobius_pi1(mid)-ALPHA) <= 0: hi = mid
    else: lo = mid
P("  解 Pi1(M_n)=alpha  =>  n* = %.6f" % ((lo+hi)/2))
OUT["alpha"] = dict(pi60=pi60, alpha=ALPHA, rel=float(abs(pi60-ALPHA)/ALPHA), nstar=(lo+hi)/2)

# ---------------- 骨架 ----------------
P("\n[定理1 & 表2 & 表3]  骨架 Y3⋉△3")
def Y3(open_ring=None):
    G = nx.Graph()
    for i in range(3):
        G.add_node("c%d" % i)
        for j in range(3):
            G.add_node("L%d%d" % (i, j)); G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("L%d%d" % (a, j), "L%d%d" % (b, j))
    if open_ring is not None:
        G.remove_edge("L0%d" % open_ring, "L1%d" % open_ring)
    return G
def perm_order(p):
    seen, l = set(), 1
    for x in p:
        if x in seen: continue
        c, y = 0, x
        while y not in seen:
            seen.add(y); y = p[y]; c += 1
        l = l*c//gcd(l, c)
    return l
for tag, r in (("闭态", None), ("开态", 0)):
    G = Y3(r)
    autos = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    rings = {j: sorted(["L0%d" % j, "L1%d" % j, "L2%d" % j]) for j in range(3)}
    c3 = sum(1 for p in autos if perm_order(p) == 3)
    c2 = sum(1 for p in autos if perm_order(p) == 2)
    seen, orb = set(), []
    for j in rings:
        if j in seen: continue
        o = sorted({s for s in rings if any(sorted(p[x] for x in rings[j]) == rings[s] for p in autos)})
        seen |= set(o); orb.append(o)
    P("  %s: |Aut|=%d  阶3元=%d  阶2元=%d  V=%d E=%d  beta1=%d"
      % (tag, len(autos), c3, c2, G.number_of_nodes(), G.number_of_edges(),
         G.number_of_edges()-G.number_of_nodes()+1))
    P("        三环轨道 = %s" % (orb,))
    OUT["skel_"+tag] = dict(aut=len(autos), o3=c3, o2=c2, orbits=[[int(x) for x in o] for o in orb])
G = Y3()
phi = lambda nm: nm if nm.startswith("c") else ("L%s%d" % (nm[1], (int(nm[2])+1) % 3))
P("  phi 保边 = %s ; 阶 = %d" % (all(G.has_edge(phi(a), phi(b)) for a, b in G.edges()),
                                perm_order({x: phi(x) for x in G.nodes()})))
chi_v = sum(1 for x in G.nodes() if phi(x) == x)
chi_e = sum(1 for a, b in G.edges() if {phi(a), phi(b)} == {a, b})
P("  顶点 dim=12 chi=%d -> 平凡 %d/12 ; 非平凡 %d/12" % (chi_v, (12+2*chi_v)//3, (12-chi_v)//3))
P("  边   dim=18 chi=%d -> 平凡 %d/18 ; 非平凡 %d/18" % (chi_e, (18+2*chi_e)//3, (18-chi_e)//3))
OUT["char"] = dict(chi_v=chi_v, chi_e=chi_e)

P("\n" + "="*72)
json.dump(OUT, open("_sre_paper_v2_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
P("saved _sre_paper_v2_check.json")
