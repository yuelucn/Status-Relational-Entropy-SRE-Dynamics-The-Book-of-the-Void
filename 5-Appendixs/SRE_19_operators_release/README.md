# SRE 19 Operators — Graph Topology & Emergent Physics Suite

A full implementation of the **SRE (Structured Reduction Engine) 19-operator pipeline**
for graph-based emergent-physics computation. Operators 1–10 cover graph transformation
and spectral gating; operators 11–19 extend the pipeline with electronic-structure,
spectral-shape, Hodge-homological, and Z₂ charge-channel analysis.

This package is released under the **MIT License** for open scientific verification.

---

## Package Contents

```
sre_19_operators_release/
├── sre_foundational_layer.py     # Op 1–4  (expansion, metrics, field, degree)
├── sre_transport_alignment.py    # Op 5–6  (latency, spectral splicing / Lanczos)
├── sre_commercial_core.py        # Op 7–10 (potential, valve flow, stitching, firewall)
├── sre_electronic_layer.py       # Op 11–12 (spin-charge adjacency, closed-loop audit)
├── sre_spectral_solver.py        # Op 13–18 (Chebyshev moments, Hodge, Newton, Hankel, audit, homology)
├── sre_charge_channel.py         # Op 19    (Z₂ holonomy / charge channel)
├── c_sources/                    # C source for Cython-accelerated modules (Op 1–10)
├── tests/                        # Unit tests
├── benchmarks/                   # Benchmark & Graph500 scripts
├── docs/                         # Graph500 report + article (EN/CN)
├── requirements.txt
└── LICENSE
```

---

## Operator Map

| Op  | File                        | Class                    | Name                              | Layer           |
|-----|-----------------------------|--------------------------|-----------------------------------|-----------------|
| 1   | sre_foundational_layer.py   | SREFoundationalOperatorSuite | Expansion                     | Foundational    |
| 2   | sre_foundational_layer.py   | SREFoundationalOperatorSuite | Metrics                       | Foundational    |
| 3   | sre_foundational_layer.py   | SREFoundationalOperatorSuite | Field                         | Foundational    |
| 4   | sre_foundational_layer.py   | SREFoundationalOperatorSuite | Degree (CSR SpGEMM)           | Foundational    |
| 5   | sre_transport_alignment.py  | SRETransportAlignmentSuite   | Latency / Timing              | Transport       |
| 6   | sre_transport_alignment.py  | SRETransportAlignmentSuite   | Spectral Splicing (Lanczos)   | Transport       |
| 7   | sre_commercial_core.py      | SRECommercialCoreSuite       | Adjoint Potential             | Commercial Core |
| 8   | sre_commercial_core.py      | SRECommercialCoreSuite       | Valve Flow                    | Commercial Core |
| 9   | sre_commercial_core.py      | SRECommercialCoreSuite       | Stitching                     | Commercial Core |
| 10  | sre_commercial_core.py      | SRECommercialCoreSuite       | Firewall                      | Commercial Core |
| 11  | sre_electronic_layer.py     | SREElectronicOperatorSuite   | Spin-Charge Adjacency         | Electronic      |
| 12  | sre_electronic_layer.py     | SREElectronicOperatorSuite   | Closed-Loop Audit             | Electronic      |
| 13  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Chebyshev Moments             | Spectral Solver |
| 14  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Hodge Projection              | Spectral Solver |
| 15  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Endogenous Newton Step        | Spectral Solver |
| 16  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Hankel Clamp                  | Spectral Solver |
| 17  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Audit (convergence verdict)   | Spectral Solver |
| 18  | sre_spectral_solver.py      | SRESpectralSolverSuite       | Homological Realization       | Spectral Solver |
| 19  | sre_charge_channel.py       | SREChargeChannelSuite        | Z₂ Charge Channel             | Charge Channel  |

---

## Installation

```bash
pip install -r requirements.txt
```

Python ≥ 3.10 recommended.

---

## Quick Start

```python
import numpy as np
from sre_foundational_layer import SREFoundationalOperatorSuite
from sre_transport_alignment import SRETransportAlignmentSuite
from sre_commercial_core import SRECommercialCoreSuite
from sre_electronic_layer import SREElectronicOperatorSuite
from sre_spectral_solver import SRESpectralSolverSuite
from sre_charge_channel import SREChargeChannelSuite

# Build a small weighted adjacency (N=8 ring)
n = 8
A = np.zeros((n, n))
for i in range(n):
    A[i, (i+1) % n] = 1.0
    A[(i+1) % n, i] = 1.0

# --- Op 4: Degree / CSR SpGEMM ---
found = SREFoundationalOperatorSuite(A)
A_s, deg = found.execute_operator_4_degree()
print("Symmetrized A_s shape:", A_s.shape)

# --- Op 6: Spectral splicing (Lanczos) ---
trans = SRETransportAlignmentSuite()
lam2, alpha_n, residual = trans.execute_operator_6_splicing(A_s, K=8)
print(f"lambda_2={lam2:.6f}, alpha_n={alpha_n:.6f}")

# --- Op 11: Spin-charge adjacency ---
elec = SREElectronicOperatorSuite()
chi = np.random.uniform(1.0, 3.0, size=n)
result_11 = elec.execute_operator_11_spin_charge_adjacency(A_s, chi, rho=0.5)
print(f"lambda_2_q={result_11['lambda_2_q']:.6e}")

# --- Op 14: Hodge projection ---
solver = SRESpectralSolverSuite()
m_g, n_face = 16, 4
rng = np.random.default_rng(0)
D = rng.standard_normal((m_g, n)); D = np.linalg.qr(D)[0][:m_g, :]  # grad
C = rng.standard_normal((n_face, m_g)); C = np.linalg.qr(C.T)[0].T[:n_face, :]  # curl
phi, harm, psi = solver.execute_operator_14_hodge_project(D, C, rng.standard_normal(m_g))
print(f"||grad||={np.linalg.norm(D @ phi):.4f}, ||harm||={np.linalg.norm(harm):.4f}")

# --- Op 19: Z2 charge channel ---
ch = SREChargeChannelSuite()
edges = [(i, (i+1) % n) for i in range(n)]
res_19 = ch.execute_operator_19_z2_charge_channel(edges, n)
print(f"beta_1={res_19['beta_1']}, deg={res_19['deg']}, sigma_trivial={res_19['sigma_trivial']}")
```

---

## Running Tests

```bash
cd tests
pytest test_operators_11_19.py -v       # 61 tests for Op 11–19
pytest test_sre_foundational.py -v      # Op 1–4
pytest test_sre_transport.py -v         # Op 5–6
pytest test_sre_core.py -v              # Op 7–10
pytest test_pyd.py -v                   # Cython acceleration tests
```

---

## Benchmarks

```bash
cd benchmarks
python benchmark_operators_11_19.py     # Per-operator latency sweep
python graph500_benchmark.py             # Graph500-compatible benchmark
```

Graph500 standard results (SCALE 12 / 20 / 24) are documented in
`docs/graph500_standard_report.md`. All 19 operators pass the official
`parse_graph500.py` format check (22 required fields, SRE extensions isolated
in `#` comment lines).

---

## C Acceleration

The `c_sources/` directory contains the C source for Cython-accelerated
versions of Op 1–10. To build:

```bash
python setup_build.py build_ext --inplace
```

The pure-Python modules are fully functional without compilation; the C
extension only improves performance for large graphs.

---

## References

- Graph500 benchmark specification: https://graph500.org/
- Hodge decomposition on graphs: Dodziuk (1976), Eckmann (1944)
- Chebyshev spectral methods: ChebNet (Defferrard et al., 2016)
- Z₂ holonomy and topological phases: Kitaev (2003)

## Citation

If you use this suite in academic work, please cite:

```
SRE 19-Operator Graph Topology Suite. Released under MIT License, 2025.
```
