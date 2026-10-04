# Emergence of Time in the SRE Framework — Short Abstract

**A Saturation Law for the Rate of Change, Universality, and the Incompatibility of Two Internal Clocks**

**作者**：岳路（Yue Lu）　|　**版本**：1.0　|　**日期**：2026-10-04

Full paper: `SRE_时间涌现.md` (Chinese) / `SRE_时间涌现_EN.md` (English).

---

## Abstract (English)

In the State–Relational Entropy (SRE) framework the word "time" carries three distinct objects under one name — the external step count $t_{\rm ext}=n$, the memory-intrinsic time $\tau_{\rm mem}\propto\sqrt n$, and a third quantity defined here. We propose to read the *expected amount of change in the world at step $n$* as the time worth of that step,

$$
\Omega(n)=\big\langle a_{ij}(n)\big\rangle_{\text{all }n^{2}\text{ entries}},\qquad
a_{ij}=\frac{\rho_{ij}}{1+\rho_{ij}},\quad \rho_{ij}=\frac{\lambda d_{ij}}{|M^{2}|_{ij}+1},
\qquad T_{\rm em}(n)=\sum_{k<n}\Omega(k),
$$

and call $T_{\rm em}$ the **emergent time**. No new free real number is introduced; $\lambda$ and the step scale follow existing registrations and the evolution loop is unaltered.

Seven verdicts follow. (1) $\Omega$ saturates monotonically toward $1$ (gap $0.1540$ at $n=999$; self-consistency $2.2\times10^{-16}$). (2) The approach obeys $1-\Omega=c\ln n/\sqrt n$ with $c=0.694157$, maximum relative residual $1.589\%$, versus $26.43\%$ for a pure power law — the logarithm is the fingerprint of the harmonic tail; the same law is predicted with zero free parameters from two laws of round 77, agreeing to $0.28\%$–$1.65\%$. (3) Relative step-to-step non-uniformity falls from $4.23\times10^{-3}$ to $6.10\times10^{-5}$ and matches the value differentiated from the saturation law within $[0.873,1.407]$ — uniformity is a *derived* property, not an assumption. (4) Locally it is not uniform: a single element's rewriting rate rises with its own age, from $0.058931$ (newborn) to $0.957750$ (oldest) at $n=999$. (5) Universality: sweeping $\lambda$ over a factor of $15$ does not move the limit, only the speed of approach — because the limit is a saturation value and a saturation value carries no coupling strength. (6) A phase transition lives in the *form* of the update rule, not in the value of parameters: squaring one denominator moves the limit from $1.0000$ to about $0.390$, the gap reaching $0.4629$ at $1099$ steps and still widening. (7) The price of emergence is that time is not unique: $\tau_{\rm mem}\propto\sqrt n$ and $T_{\rm em}\propto n$ diverge in ratio ($6.89\times$ and growing), so no rescaling makes both uniform.

Three limits are stated explicitly. The emergent time has **shape but no scale** — "how many seconds is one step" remains external input. At attainable sizes time constancy holds only to about $22\%$ ($T_{\rm em}/n=0.7776$ at $n=999$). And two pre-registered guesses were refuted by measurement ($c\propto\lambda^{-1}$ gives slope $-0.577$; the variant kernel settles at a fixed point near $0.39$ instead of freezing) and are registered as open items, not evidence.

The load-bearing separation is **structure without memory**: the joint distribution of the state matrix rejects full independence (row-sum variance $1.94$–$2.03\times$ the iid value, KS $p<10^{-4}$), yet two different histories become indistinguishable after continued evolution (exact permutation $p\ge0.3841$, none significant after Holm correction). The present state carries zero bits about its own past — which is exactly why time must be *accumulated* rather than *read off*. All numbers hold **inside the SRE model only**; comparisons with physical time are structural analogies, not numerical predictions.

**Keywords**: State–Relational Entropy (SRE); emergence of time; saturation law; rewriting rate; age law; memory horizon; incompatibility of two clocks; separation of structure and memory; exact permutation test; discrete closure law.

---

## 摘要（中文）

在状态—关系熵（SRE）框架里，「时间」一词同时承载着三个互不相同的对象：外部步数 $t_{\rm ext}=n$、记忆内禀时间 $\tau_{\rm mem}\propto\sqrt n$，以及本文定义的第三个量。本文主张把**第 $n$ 步世界的期望改变量**读作该步所值的时间，

$$
\Omega(n)=\big\langle a_{ij}(n)\big\rangle_{\text{全部 }n^{2}\text{ 个元素}},\qquad
a_{ij}=\frac{\rho_{ij}}{1+\rho_{ij}},\quad \rho_{ij}=\frac{\lambda d_{ij}}{|M^{2}|_{ij}+1},
\qquad T_{\rm em}(n)=\sum_{k<n}\Omega(k),
$$

并称 $T_{\rm em}$ 为**涌现时间**。本文不引入任何新的自由实数：$\lambda$ 与步数规模沿用既有登记，演化循环一字未改。

七项判决如下。（1）**饱和**：$\Omega$ 单调趋于 $1$（$n=999$ 处缺口 $0.1540$，自洽校验 $2.2\times10^{-16}$）。（2）**饱和律**：$1-\Omega=c\ln n/\sqrt n$，$c=0.694157$，最大相对残差 $1.589\%$，而纯幂律残差达 $26.43\%$——$\ln n$ 是调和尾巴的指纹；该律由第 77 轮两条既有律**零参数**预测，与实测差 $0.28\%$–$1.65\%$。（3）**渐近均匀**：相对步进非均匀度从 $4.23\times10^{-3}$ 降到 $6.10\times10^{-5}$，与由饱和律**微分而来**的预测之比落在 $[0.873,1.407]$——均匀性是**推论**，不是假设。（4）**内部不均匀**：单个元素的改写率随自身年龄单调上升，$n=999$ 时从 $0.058931$（新生）到 $0.957750$（最老）。（5）**普适性**：$\lambda$ 扫过 $15$ 倍不改极限，只改逼近速度——因为极限是饱和值，而饱和值不携带耦合强度。（6）**相变在规则形态、不在参数取值**：把一处分母平方，极限由 $1.0000$ 移到约 $0.390$，$1099$ 步处差距已达 $0.4629$ 且持续扩大。（7）**代价**：时间不唯一。$\tau_{\rm mem}\propto\sqrt n$ 与 $T_{\rm em}\propto n$ 的比值发散（$6.89$ 倍且继续），不存在使两者同时匀速的重标定。

三条限定必须写明。涌现时间**只有形状、没有尺度**——「一步等于多少秒」仍是外加输入；在可达规模上「时间恒定」只有约 $22\%$ 的精度（$n=999$ 时 $T_{\rm em}/n=0.7776$）；另有两条**动笔之前的猜测**被实测推翻（$c\propto\lambda^{-1}$ 实测斜率 $-0.577$；变体核落到约 $0.39$ 的不动点而非失控冻结），按纪律登记为开放项，不作证据。

承重的一条分离是**有结构、无记忆**：状态矩阵的联合分布拒斥完全 iid（行和方差为 iid 的 $1.94$–$2.03$ 倍，KS $p<10^{-4}$），但两条互异历史在续跑后不可分辨（精确置换 $p\ge0.3841$，Holm 校正后无显著）。当前状态对自己的过去携带零比特——这正是「时间只能被累积、不能被读取」的确切含义。全部数值**仅在 SRE 模型内部成立**，与物理时间的对照一律为结构类比，非数值预言。

**关键词**：状态—关系熵（SRE）；时间涌现；饱和律；改写率；年龄律；记忆视界；双钟不可共存；结构与记忆的分离；精确置换检验；离散闭合律。

---

> 【资源与可用性声明】 本框架基于状态‑关系熵（SRE）动力学构建。 全部理论资料归档于 Zenodo 开源数据仓库。**本文档套件包括系统论文、应用开发、科学假说、算子1‑6,11,12完整代数推导及仿真代码完全开源**；算子7、8、9、10、13-18 属于后续闭源商业核心模块，不在本文档套件范围内。
>
> 可访问支持 AI 辅助查阅的腾讯智能文档空间（PC、微信移动端均可访问）。截至 2026‑08‑14，受谷歌服务使用条款约束，作者不再维护谷歌 Gemini Notebook 内的 SRE 文档库，该链接仅作历史存档，请勿作为正式引用来源：[https://notebooklm.google.com/notebook/ef52bf5a‑f6d0‑4a2a‑aed4‑b25d6520ab2c](https://notebooklm.google.com/notebook/ef52bf5a%E2%80%91f6d0%E2%80%914a2a%E2%80%91aed4%E2%80%91b25d6520ab2c)；腾讯智能文档：[https://docs.qq.com/space/DUkRjYUtNWFdyV253](https://docs.qq.com/space/DUkRjYUtNWFdyV253)。根据 SRE 原理，经典物理基础源自信息统计学。
