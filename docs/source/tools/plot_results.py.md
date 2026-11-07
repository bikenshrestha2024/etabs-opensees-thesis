# plot_results.py — implementation guide

**Source:** [tools/plot_results.py](../../../tools/plot_results.py)
**Workstream:** 09 Interpretation. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

Read-only matplotlib figures from completed run folders: storey drift / shear / overturning envelopes per M0–M6 (mean of accepted cases; exploratory cases dashed), roof drift histories, FVD/BRB force-deformation loops, stacked energy balance, modal period/damping table, matched-record spectra against the NBC C(T)/Ωu target, and the workflow flowchart. The target is drawn only when `--zone-Z` and `--importance-I` (or `--target-csv`) are given; no project value is assumed. Storey shear and overturning use storey mass × absolute floor acceleration (damping forces neglected, stated on the figure). Uses only numpy/matplotlib already in the conda env.

## References

NBC 105:2025 §5.5.3, §9.3.3, §4.1.2 (R10); Chopra, Dynamics of Structures. Tag convention: [REF_TAG_CONVENTION.md](../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_plot_and_dashboard.py`. Passing tests establish solver behaviour on small test models or synthetic data. They do **not** establish convergence, calibration or NBC acceptance of the thesis building.

[Guide index](../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
