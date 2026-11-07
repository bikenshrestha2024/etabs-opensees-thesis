# export_dashboard.py — implementation guide

**Source:** [tools/export_dashboard.py](../../../tools/export_dashboard.py)
**Workstream:** 09 Interpretation. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

openpyxl workbook: README (gate definitions), Run_Matrix (planned config × XY/YX joined to results), Case_Results (peaks and gates), Summary_Variant (mean of accepted cases per variant and limit state, with chart), Gate_Counts. Gates: G_RUN, G_COMPLETE (completion gate), G_ENERGY, G_DRIFT (§5.5.3 screen), G_DAMPING. They are numerical screens, not design acceptance.

## References

NBC 105:2025 §5.5.3, §9.3.2.3, §9.3.3 (R10); docs/00_THESIS_ACCEPTANCE_GATES.md. Tag convention: [REF_TAG_CONVENTION.md](../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_plot_and_dashboard.py`. Passing tests establish solver behaviour on small test models or synthetic data. They do **not** establish convergence, calibration or NBC acceptance of the thesis building.

[Guide index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
