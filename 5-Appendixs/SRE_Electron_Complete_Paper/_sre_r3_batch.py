"""
R3 补充: 批量容错合并算子 R_batch_eps (连通分量式, 抗边噪声) 的鲁棒性 + 步数标度验证.
ε 从已保存的 sre_r3_deepcore_results.json 读取 (物理定标值).
"""
import numpy as np
import networkx as nx
import json, importlib.util

R2 = r"C:\mywork\vasp\_sre_r2_convergence.py"
r2 = importlib.util.module_from_spec(importlib.util.spec_from_file_location("r2", R2))
importlib.util.spec_from_file_location("r2", R2).loader.exec_module(r2)

# ε 物理定标值 (来自主 R3 运行, 中位数休眠概率 1/(1+lam*d/(|M@M|+1)))
EPS = 0.1832


def holonomy_sign(M, i, j):
    S = M.copy(); np.fill_diagonal(S, 0)
    s = 1 if np.sum(S[i] * S[j]) >= 0 else -1
    return s

def R_batch_eps(M, eps):
    """连通分量式容错合并: 以 tension<=eps 为边建图, 取连通分量作商.
    每遍并行合并所有 holonomy-链接对 => 抗单条边翻转, 步数 ~ O(L)."""
    M = M.astype(int)
    while True:
        n = M.shape[0]
        S = M.copy(); np.fill_diagonal(S, 0)
        # tension 图
        adj = np.zeros((n, n), dtype=bool)
        for i in range(n):
            for j in range(i + 1, n):
                # tension
                s = 1 if np.sum(S[i] * S[j]) >= 0 else -1
                agree = 0.0; cnt = 0
                for k in range(n):
                    if k == i or k == j: continue
                    if S[i, k] == 0 and S[j, k] == 0: continue
                    cnt += 1
                    if S[i, k] == s * S[j, k]: agree += 1
                t = 0.0 if cnt == 0 else 1 - agree / cnt
                if t <= eps:
                    adj[i, j] = adj[j, i] = True
        # 连通分量
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    ri, rj = find(i), find(j)
                    if ri != rj: parent[ri] = rj
        comps = {}
        for i in range(n):
            r = find(i); comps.setdefault(r, []).append(i)
        blocks = list(comps.values())
        if len(blocks) == n:  # 无合并
            break
        m = len(blocks)
        C = np.zeros((m, m), dtype=int)
        for a in range(m):
            for b in range(m):
                if a == b: continue
                vals = []
                for x in blocks[a]:
                    for y in blocks[b]:
                        if M[x, y] != 0:
                            vals.append(int(M[x, y]))
                if vals:
                    C[a, b] = 1 if np.sum(vals) >= 0 else -1
                    C[b, a] = C[a, b]
        M = C
    return M


def add_edge_noise(M, rho, rng):
    M = M.copy().astype(int); n = M.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if M[i, j] != 0 and rng.random() < rho:
                M[i, j] = -M[i, j]; M[j, i] = -M[i, j]
    return M

def is_Q3(S):
    V, E, b1, _, _ = r2.graph_invariants(S)
    if (V, E, b1) != (8, 12, 5): return False, (V, E, b1)
    G = nx.from_numpy_array((np.fill_diagonal(S.copy(), 0) or S) != 0)
    Q = nx.from_numpy_array((np.fill_diagonal(r2.cube_Q3().copy(), 0) or r2.cube_Q3()) != 0)
    return nx.is_isomorphic(G, Q), (V, E, b1)


def main():
    out = {}
    print(f"[batch] using eps={EPS:.4f}", flush=True)
    # 噪声鲁棒性
    rhos = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2]
    noise = {}
    for L in [1, 2, 3]:
        base = r2.z2_lift(r2.cube_Q3(), levels=L)
        row = {}
        for rho in rhos:
            rng = np.random.default_rng(7000 * L + int(rho * 1000))
            noisy = add_edge_noise(base, rho, rng)
            rb = R_batch_eps(noisy, EPS)
            ok, inv = is_Q3(rb)
            # 邻域
            fac = {}
            for f in [0.5, 2.0]:
                r2b, _ = is_Q3(R_batch_eps(noisy, EPS * f))
                fac[str(f)] = bool(r2b)
            row[str(rho)] = dict(batch_recovered=bool(ok), batch_inv=list(inv), eps_fac=fac)
        noise[f"L{L}"] = row
        print(f"[batch noise L={L}]", flush=True)
        for rho in rhos:
            r = row[str(rho)]
            print(f"   rho={rho}: batch={r['batch_recovered']}{tuple(r['batch_inv'])} fac={r['eps_fac']}", flush=True)
    out["batch_noise_robustness"] = noise

    # 步数标度 (批处理: 每遍合并所有链接对, 步数应 ~ O(L))
    scaling = {}
    for L in range(1, 6):
        base = r2.z2_lift(r2.cube_Q3(), levels=L)
        cur = base; steps = 0
        for _ in range(L + 5):
            nxt = R_batch_eps(cur, EPS) if False else None
            # 单遍
            n = cur.shape[0]
            S = cur.copy(); np.fill_diagonal(S, 0)
            adj = np.zeros((n, n), dtype=bool)
            for i in range(n):
                for j in range(i + 1, n):
                    s = 1 if np.sum(S[i]*S[j]) >= 0 else -1
                    agree=0.0; cnt=0
                    for k in range(n):
                        if k==i or k==j: continue
                        if S[i,k]==0 and S[j,k]==0: continue
                        cnt+=1
                        if S[i,k]==s*S[j,k]: agree+=1
                    t = 0.0 if cnt==0 else 1-agree/cnt
                    if t <= EPS: adj[i,j]=adj[j,i]=True
            parent=list(range(n))
            def find(x):
                while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
                return x
            for i in range(n):
                for j in range(i+1,n):
                    if adj[i,j]:
                        ri,rj=find(i),find(j)
                        if ri!=rj: parent[ri]=rj
            comps={}
            for i in range(n):
                r=find(i); comps.setdefault(r,[]).append(i)
            blocks=list(comps.values())
            if len(blocks)==n: steps+=1; break
            m=len(blocks); C=np.zeros((m,m),int)
            for a in range(m):
                for b in range(m):
                    if a==b: continue
                    vals=[]
                    for x in blocks[a]:
                        for y in blocks[b]:
                            if cur[x,y]!=0: vals.append(int(cur[x,y]))
                    if vals:
                        C[a,b]=1 if np.sum(vals)>=0 else -1; C[b,a]=C[a,b]
            cur=C; steps+=1
        ok,_=is_Q3(cur)
        scaling[f"L{L}"]=dict(start_nodes=base.shape[0], batch_steps=steps, is_Q3=bool(ok))
        print(f"[batch scaling L={L}] start={base.shape[0]} steps={steps} Q3={ok}", flush=True)
    out["batch_step_scaling"]=scaling

    with open("sre_r3_batch_results.json","w") as f:
        json.dump(out,f,indent=2,default=str)
    print("[OK] sre_r3_batch_results.json", flush=True)

if __name__ == "__main__":
    main()
