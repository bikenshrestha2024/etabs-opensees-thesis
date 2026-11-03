# wall_topology.py — implementation guide

**Source:** [components/nonlinear_time_history/wall_topology.py](../../../../components/nonlinear_time_history/wall_topology.py)
**Source blob SHA:** e1591d440ebbe318a1d49f1afb65b254554258fc
**Workstream:** 03 wall opening occupancy.

## Input contract and failure gate

Use the module's exact function docstrings and the corresponding stage guide under docs/programs. All data are kN-m-s model units unless source quantities explicitly say mm, MPa or g. Nonfinite, missing, mismatched or unapproved inputs must block the relevant analysis rather than be interpreted as zero.

## Provenance and cited method

NBC 105:2025 is governing seismic basis (DUDBC). Wall model formulation: Kolozvari et al. (2023), https://doi.org/10.1016/j.engstruct.2023.116700. Research device context: Korkmaz & Kircil (2026), https://doi.org/10.3390/buildings16040711. Only cite the relevant physical domain: these papers do not validate this specific building.

## Verification

Unit test: tests/verify_wall_openings.py. This is a solver-free input/response behavior check. A successful test cannot establish true nonlinear wall convergence, experimental calibration, structural performance or device approval. Native OpenSeesPy and source ETABS comparisons must still be run.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
