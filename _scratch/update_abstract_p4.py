import os

B = r"c:\mywork\SRE-Dynamics"
A4_C = "c:\\mywork\\SRE-Dynamics\\4-Applications&Hypothesis\\0\u2011Abstract_Part_4_C.md"
A4_E = "c:\\mywork\\SRE-Dynamics\\4-Applications&Hypothesis\\0\u2011Abstract_Part_4_E.md"

C_TITLE = '9. **SRE 拓扑谱模型：从离散算子到可微分 AI 模型层**'
C_SUM = ('>系统记录 SRE 拓扑谱模型从离散算子到可微分 AI 模型层的完整设计推理、架构实现与实验验证。'
         '自“算子首尾相衔、桥接恒等精确成立”出发，阐明算子微积分的 torch 镜像实现、可微分'
         '层级压缩这一缺失承重件的构造，以及 $\\tau_k$ 不可保真的数学发现与替代方案；给出符号'
         '约定与图拉普拉斯、Betti 数 $\\beta_1$、Chebyshev 函数演算、Galerkin 投影、热核迹五概念'
         '的精确定义；构筑由链复形输入、解析可微 Laplacian 构造、可学习粗粒化 SoftAggPooler、'
         'SRE Topo Encoder、层级注意力谱融合与五项损失组成的模型架构。在自监督边权反演（UC1）、'
         '分子性质回归（UC2）、图分类/$\\beta_1$ 拓扑识别（UC3）三个用例上完成实验与因果分析，'
         '并附环境搭建、权重加载推理、超参数调优、诚实边界与改进路线图。')

E_TITLE = '9. **SRE Topological Spectral Model: From Discrete Operators to a Differentiable AI Model Layer**'
E_SUM = ('> Abstract: This chapter documents the complete design reasoning, architectural implementation, '
         'and experimental validation of the SRE Topological Spectral Model, charting the path from discrete '
         'operators to a differentiable AI model layer. Beginning with the end-to-end bridging identity of the '
         'operator chain, it sets out the torch mirror implementation of operator calculus, the construction of '
         'the missing load-bearing component for differentiable hierarchical compression, and the mathematical '
         'discovery that $\\tau_k$ is not preservable together with its alternative. It gives the notation '
         'convention and precise definitions of five concepts — graph Laplacian, Betti number $\\beta_1$, '
         'Chebyshev functional calculus, Galerkin projection, and heat-kernel trace — and then builds the model '
         'architecture from chain-complex input, an analytic differentiable Laplacian construction, the learnable '
         'SoftAggPooler coarse-graining, the SRE Topo Encoder, level-attention spectral fusion, and a five-term '
         'loss. Experiments and causal analysis are conducted on three use cases — self-supervised edge-weight '
         'inversion (UC1), molecular property regression (UC2), and graph classification / $\\beta_1$ topology '
         'identification (UC3) — together with environment setup, weight-loading inference, hyperparameter tuning, '
         'honest boundaries, and an improvement roadmap.')


def rt(p):
    with open(p, "rb") as f:
        d = f.read()
    if d.startswith(b"\xef\xbb\xbf"):
        d = d[3:]
    return d.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def wt(p, t):
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


def patch(path, title_new, sum_new, title_prefix, sum_prefix):
    lines = rt(path).split("\n")
    idx = None
    for i, ln in enumerate(lines):
        if ln.startswith(title_prefix):
            idx = i
            break
    assert idx is not None, "item 9 title not found in " + path
    assert lines[idx + 1].startswith(sum_prefix), "summary line mismatch at %d" % (idx + 1)
    lines[idx] = title_new
    lines[idx + 1] = sum_new
    wt(path, "\n".join(lines))
    print("PATCHED", os.path.basename(path), "line", idx + 1)


patch(A4_C, C_TITLE, C_SUM, "9. **状态", ">针对传统GNN")
patch(A4_E, E_TITLE, E_SUM, "9. **SRE", "> Abstract: Targeting GNN")
print("DONE")
