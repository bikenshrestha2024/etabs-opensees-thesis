# NLTHA settings: literature cross-check (2026-11-25)

Review notes only. Nothing here changes a solver default or sets any approval flag.

| Repo setting | Literature position | Status |
|---|---|---|
| Rayleigh damping, 2.5 % (NBC 105:2025 s8.1.1.5 cap 5 %) | PEER 2020/01 (Qian & Chopra) does not recommend Rayleigh damping for nonlinear RHA of steel frames because demands come out smaller; constant modal damping is the alternative. PEER/ATC-72-1 (2010) uses tangent-stiffness Rayleigh with the first period elongated about 1.5x. Charney-type comparisons (arXiv 1309.2741) show initial vs tangent stiffness gives different elastic damping. | REVIEW: record the damping basis in the thesis; steel-frame result, not RC-wall specific. |
| Newmark 0.5/0.25, transformation constraints | Standard in OpenSees outrigger/core-wall studies (e.g. Buildings 2025, 15(19), 3563, 24/48-storey RC and BRB-core with outriggers). | Consistent |
| Opt-in `final_relaxed_tolerance` (1e-7 < tol <= 1e-5) | No source fixes a value; it is a numerical-floor workaround and is counted and reported in diagnostics. | Exploratory only |

Sources: peer.berkeley.edu 2020_01_chopra_final_report.pdf; peer.berkeley.edu peer-atc-72-1_report.pdf; arxiv.org/abs/1309.2741; mdpi.com/2075-5309/15/19/3563.
Not verified: the Springer 2026 damping-model paper (s10518-026-02406-y) was seen only as a snippet.
