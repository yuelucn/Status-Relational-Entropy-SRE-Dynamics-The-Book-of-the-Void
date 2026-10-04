# -*- coding: utf-8 -*-
"""
SRE 夸克质量探针（第三十一轮）
=================================
命题：夸克在 SRE 里是涌现结果 ⇒「质量如何计算」？

方法：把「计算」拆成三步，逐步判定哪一步在 SRE 内（图谱／账本），
      哪一步必须付外部输入（量纲化 / 重整化方案）。

纯标准库实现，不需要 numpy。
解释器：C:/Users/yuelu/.workbuddy/binaries/python/versions/3.13.12/python.exe
"""
import sys, math, json, itertools

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LOG = []
STAT = {}


def P(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


def Q(ms):
    """Koide 型比值 Q = (sum m) / (sum sqrt(m))^2 ，恒落在 [1/3, 1]。"""
    return sum(ms) / (sum(math.sqrt(m) for m in ms) ** 2)


def Qm(ms, signs):
    """带符号版（文献里的 Q_middle 用 -sqrt(m_s)）。"""
    return sum(ms) / (sum(s * math.sqrt(m) for s, m in zip(signs, ms)) ** 2)


def eta2(q):
    return (3.0 * q - 1.0) / 2.0


def theta_deg(q):
    c = 1.0 / math.sqrt(3.0 * q)
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def line(name, ms, target=None, q=None):
    if q is None:
        q = Q(ms)
    e = eta2(q)
    s = "  %-30s Q = %.6f   eta^2 = %+.6f   theta = %8.4f deg" % (name, q, e, theta_deg(q))
    if target is not None:
        s += "  | dev vs %.6f = %+.3e (%+.2f%%)" % (target, q - target, 100 * (q / target - 1))
    P(s)
    return q


# =====================================================================
P("#" * 100)
P("# PART A  对照：带电轻子（pole mass = 物理量，scheme-无关）")
P("#" * 100)
ME, MMU = 0.51099895000, 105.6583755
for mtau, tag in [(1776.86, "归档口径"), (1776.93, "2026 PDG 中心")]:
    q = line("(e, mu, tau) [%s]" % tag, [ME, MMU, mtau], 2.0 / 3.0)
    STAT["lepton_%s" % tag] = q
P("")
P("  ⇒ 轻子侧 Q = 2/3 成立到 1e-6 量级，且 m 是极点质量（scheme-无关）—— 这是『干净靶』的样板。")

# =====================================================================
P("")
P("#" * 100)
P("# PART B  夸克三组：换约定就换答案（这就是闸门 C2 的实证）")
P("#" * 100)

CONV = {
    "PDG2024 MS-bar（u,d,s@2GeV；c,b,t@自身标度；m_t=162.5 MS-bar)":
        dict(u=2.16, d=4.67, s=93.4, c=1270.0, b=4180.0, t=162500.0),
    "同左但 m_t 用直接测量/pole 172.69 GeV":
        dict(u=2.16, d=4.67, s=93.4, c=1270.0, b=4180.0, t=172690.0),
    "MS-bar @ M_Z（文献跑动值 u=1.06,d=2.29,s=45.8,c=619,b=2860,t=168300)":
        dict(u=1.06, d=2.29, s=45.8, c=619.0, b=2860.0, t=168300.0),
    "朴素组分夸克质量（非微扰定义，夸克模型）":
        dict(u=336.0, d=336.0, s=540.0, c=1550.0, b=4730.0, t=174000.0),
}

GROUPS = [
    ("轻 (u,d,s)", ["u", "d", "s"], "5/9"),
    ("重 (c,b,t)", ["c", "b", "t"], "2/3"),
    ("上型 (u,c,t)", ["u", "c", "t"], "--"),
    ("下型 (d,s,b)", ["d", "s", "b"], "--"),
]

for cname, m in CONV.items():
    P("")
    P("-- 约定：%s" % cname)
    for gname, keys, ref in GROUPS:
        tgt = {"5/9": 5.0 / 9.0, "2/3": 2.0 / 3.0}.get(ref)
        line("   " + gname, [m[k] for k in keys], tgt)

P("")
P("-- 文献里的『中间组』（带负号：-sqrt(m_s)+sqrt(m_c)+sqrt(m_b)）")
mm = CONV["PDG2024 MS-bar（u,d,s@2GeV；c,b,t@自身标度；m_t=162.5 MS-bar)"]
line("   (s,c,b) 带负号", None, None,
     q=Qm([mm["s"], mm["c"], mm["b"]], [-1, +1, +1]))
P("   （文献给出 ~0.675 —— 复现）")

P("")
P("  ⇒ 同一个『夸克质量』问题，只因为**约定**不同，Q 就能从 0.34 变到 0.72。")
P("     这不是拟合误差，是**量本身没有唯一定义**。")

# =====================================================================
P("")
P("#" * 100)
P("# PART C  本轮新增论点：Q 的不变性定理")
P("#" * 100)
P("")
P("  定理：Q(c*m1, c*m2, c*m3) = Q(m1,m2,m3)  对任意 c>0 恒成立。")
P("        （分子 ~c，分母 sum sqrt ~ sqrt(c)，平方后 ~c，两下相消。）")
P("")
base = [2.16, 4.67, 93.4]
P("  数值验证（取 c = 1e-3, 0.1, 1, 10, 1e3, 1e6）：")
for c in [1e-3, 0.1, 1.0, 10.0, 1e3, 1e6]:
    q = Q([c * x for x in base])
    P("      c = %-9g  Q = %.15f   (与 c=1 之差 %.2e)" % (c, q, q - Q(base)))
STAT["Q_light_2GeV"] = Q(base)
P("")
P("  推论（关键）：QCD 中**轻夸克 u,d,s 的跑动因子相同**（质量反常维 gamma_m 与味无关），")
P("        所以 m_u,m_d,m_s 是**同乘一个因子**地跑动 ⇒")
P("        【 Q_light 是重整化群不变量 】")
P("  数值验证（2 GeV → M_Z，三味同乘 f = 0.49036）：")
f = 0.49036
q_exact = Q([f * x for x in base])
P("      严格同乘：Q = %.15f   与 2 GeV 之差 = %.2e" % (q_exact, q_exact - Q(base)))
q_round = Q([1.06, 2.29, 45.8])          # PDG 四舍五入后的引用值
P("      引用值(有舍入)：Q = %.15f   与 2 GeV 之差 = %.2e  ← 纯粹是舍入残留" % (q_round, q_round - Q(base)))
P("")
P("  ⇒ 这解释了为什么项目早期用 (2m_u+m_d)/m_p 会失败（被外部标度 m_p 污染），")
P("     而 Q_light 本身却**是**一个 C2-干净的观测量。二者不是同一类量。")

# =====================================================================
P("")
P("#" * 100)
P("# PART D  能标敏感性的量化：重夸克那条『2/3』到底有多脆")
P("#" * 100)
P("")
P("  重夸克三味的跑动因子**各不相同**（跨阈值），所以 Q_heavy **不是** RG 不变。")
own = [1270.0, 4180.0, 162500.0]      # m_c(m_c), m_b(m_b), m_t(m_t)
mz = [619.0, 2860.0, 168300.0]        # 同三味跑到 M_Z
q_own = line("(c,b,t) @ 自身标度", own, 2.0 / 3.0)
q_mz = line("(c,b,t) @ M_Z   ", mz, 2.0 / 3.0)
P("")
P("  Delta = Q - 2/3 ：  自身标度 %+.3e    M_Z %+.3e" % (q_own - 2.0 / 3.0, q_mz - 2.0 / 3.0))
P("  文献 arXiv:1111.0480 给出：-5e-3 < dK_heavy < +1e-2（自身标度）｜+5e-2 < dK_heavy < +9e-2（M_Z）")
P("  ⇒ 本脚本复现该区间：一条『命中』从 0.4% 恶化到 5.3%，整整差一个数量级。")
STAT["Qheavy_own"] = q_own
STAT["Qheavy_MZ"] = q_mz
P("")
P("  补记：Rodejohann & Zhang 2011 曾把这条观察写进预印本，**发表时删掉了**；")
P("        首发于 Cao 2012。⇒ 连文献方自己都不认为它稳。")

# =====================================================================
P("")
P("#" * 100)
P("# PART E  SRE 图谱只能给「退化基线」：Q = 1/3")
P("#" * 100)
P("")
q_deg = line("三个等质量 (1,1,1)", [1.0, 1.0, 1.0])
P("")
P("  结构依据（已实测，第 29/30 轮）：闭态骨架 9 条环边处于**同一条 Aut 轨道**")
P("  ⇒ 任何**图泛函**（lambda2 / beta1 / rho / Pi1）给三环同值 ⇒ m_k 全等 ⇒ Q = 1/3。")
P("  这正是 Koide 的 C-S 下界（等质量极限）。")
P("")
P("  !! 1/3 双身份陷阱（项目既有纪律，重申）：")
P("     此处的 1/3 = C-S 下界（等质量极限），")
P("     与 SRE 的 Pi1(Q3) = 1/3（闭合度）**来源不同，不得等同**。")
P("")
P("  ⇒ 于是 Q = 1/3 + (2/3)*eta^2 有了分层读法：")
P("       1/3            <- 图谱基线（退化，图泛函必然给出）")
P("       (2/3)*eta^2    <- 账本分裂（图泛函**看不见**，只能由账本承载）")
P("")
P("  由实测值反解 eta^2（= (3Q-1)/2）：")
TAB = [("带电轻子", 2.0 / 3.0), ("重夸克(c,b,t)", q_own), ("轻夸克(u,d,s)", Q(base))]
for nm, q in TAB:
    P("     %-16s Q = %.6f  ->  eta^2 = %.6f" % (nm, q, eta2(q)))
P("     %-16s            %s" % ("", "参考：eta^2 = 1/2 <-> Q = 2/3 ; eta^2 = 1/3 <-> Q = 5/9"))
STAT["eta2_light"] = eta2(Q(base))

# =====================================================================
P("")
P("#" * 100)
P("# PART F  轻夸克那条『5/9』离得到底有多远（带不确定度）")
P("#" * 100)
P("")
P("  PDG2024 MS-bar @2GeV：m_u = 2.16(+0.49/-0.26)｜m_d = 4.67(+0.48/-0.17)｜m_s = 93.4(+8.6/-3.4) MeV")
lo_u, hi_u = 2.16 - 0.26, 2.16 + 0.49
lo_d, hi_d = 4.67 - 0.17, 4.67 + 0.48
lo_s, hi_s = 93.4 - 3.4, 93.4 + 8.6
qs = []
for u in (lo_u, hi_u):
    for d in (lo_d, hi_d):
        for s in (lo_s, hi_s):
            qs.append(Q([u, d, s]))
P("     8 个角点：Q_min = %.6f   Q_max = %.6f   （中心 %.6f）" % (min(qs), max(qs), Q(base)))
P("     5/9 = %.6f  ->  %s" % (5.0 / 9.0, "落在角点区间内" if min(qs) <= 5.0 / 9.0 <= max(qs) else "落在区间外"))
P("")
P("  ⇒『轻夸克 ≈ 5/9』是**区间级**吻合（且中心值偏离 5/9 约 %.1f%%），" % (100 * (Q(base) / (5.0 / 9.0) - 1)))
P("     不构成 1e-6 量级的『命中』；与轻子那条（3.3e-6）不是一个量级的东西。")
STAT["Q_light_lo"] = min(qs)
STAT["Q_light_hi"] = max(qs)

# =====================================================================
P("")
P("#" * 100)
P("# PART G  汇总：SRE 三步里，哪一步在内部、哪一步要付费")
P("#" * 100)
P("")
P("  第 1 步  图谱 -> 退化基线（Q = 1/3）        : SRE 内（图泛函，实测 9 边同轨道）")
P("  第 2 步  账本 -> 分裂（(2/3)*eta^2）       : SRE 内（账本，但**规则未写出**）")
P("  第 3 步  量纲化 / 选方案 -> 绝对质量        : SRE **外**（每跨一次离散->连续必付费）")
P("")
P("  ⇒『夸克质量如何计算』的诚实答案：")
P("     - **绝对值算不出**（闸门 C2：MS-bar 方案依赖，已被多轮判负）；")
P("     - **同标度比也危险**（跑动因子跨阈值后不同 ⇒ Q_heavy 从 0.4% 恶化到 5.3%）；")
P("     - 能算的只有 **RG-不变的无量纲组合**（如 Q_light）的**函数形式**，")
P("       而 eta^2 的**数值来源**仍是缺的那条赋值规则。")
P("")

# ---- 落盘 -----------------------------------------------------------
out = {
    "round": 31,
    "topic": "quark mass computation in SRE",
    "Q_lepton_1776_86": STAT.get("lepton_归档口径"),
    "Q_lepton_1776_93": STAT.get("lepton_2026 PDG 中心"),
    "Q_light_2GeV": STAT["Q_light_2GeV"],
    "Q_light_corner_range": [STAT["Q_light_lo"], STAT["Q_light_hi"]],
    "Q_heavy_own_scale": STAT["Qheavy_own"],
    "Q_heavy_MZ": STAT["Qheavy_MZ"],
    "eta2_light": STAT["eta2_light"],
    "targets": {"5/9": 5.0 / 9.0, "2/3": 2.0 / 3.0, "CS_lower": 1.0 / 3.0},
    "verdicts": {
        "absolute_quark_mass": "判负（闸门 C2：MS-bar 方案/能标依赖）",
        "same_scale_quark_ratio": "危险（跑动因子跨阈值不同，Q_heavy 0.4% -> 5.3%）",
        "QG_invariant_ratio": "可用（Q 对同乘因子严格不变；轻夸克三味同因子跑动）",
        "eta2_value": "缺失（赋值规则未写出）",
    },
}
open("_sre_quark_mass_probe.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=2))
open("_sre_quark_mass_probe.log", "w", encoding="utf-8").write("\n".join(LOG) + "\n")
P("")
P("[已落盘] _sre_quark_mass_probe.log / _sre_quark_mass_probe.json")
P("EXIT = 0")
