# src/opensees_engine/standalone.py — limited elastic OpenSees benchmark

**Scope:** `run_standalone(data, ops=None)` validates the versioned `src.thesis_core.neutral_model` contract, creates an independent 3D six-DOF OpenSees domain with a single elastic beam-column, applies explicit nodal loads, computes six-component node responses, checks finite results and translational force equilibrium, and returns `NUMERICALLY_CONVERGED_ONLY`. `ops` may be injected for source-only fake-solver testing; otherwise OpenSeesPy is imported when the function runs. There is no ETABS source dependency.

`axial_cantilever_check(data, results)` compares a **two-node vertical axial synthetic cantilever** against the elementary elastic axial solution. Its endpoint selection must use element tag references, not node-list order; regression `tests/verify_standalone_neutral_model.py` checks reversed input ordering. Units are kN-m-s, displacement m, reactions kN/kNm. This is not 3D RCC wall/shell/FVD/BRB/full NLTHA validation; `etabs_equivalence=NOT_APPLICABLE`.


## 3D force and moment equilibrium gate (2026-11-15)

The opt-in runner evaluates `force_residual_kN` and `moment_residual_kNm` independently after reading OpenSees reactions. For every applied nodal action and support reaction, the global moment about a shared origin includes `r × F` plus that node's explicit moment components. Missing reaction couples are rejected even if all three translational reactions balance. The new moment residual field is additive to the existing results schema. A synthetic fake solver test supplies an off-axis horizontal force with balanced translation and deliberately missing support couple and requires failure; native elastic beam verification remains a separate gate.
