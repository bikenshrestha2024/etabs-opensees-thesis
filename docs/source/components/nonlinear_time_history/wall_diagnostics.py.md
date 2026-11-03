# wall_diagnostics.py — implementation guide

**Source:** [components/nonlinear_time_history/wall_diagnostics.py](../../../../components/nonlinear_time_history/wall_diagnostics.py)
**Source blob SHA:** bd3f03f76ed3363b4cf692531d06ea18b04d40db
**Workstream:** 01 X-only wall preflight.

## Input contract and failure gate

Use the module's exact function docstrings and the corresponding stage guide under docs/programs. All data are kN-m-s model units unless source quantities explicitly say mm, MPa or g. Nonfinite, missing, mismatched or unapproved inputs must block the relevant analysis rather than be interpreted as zero.

## Provenance and cited method

NBC 105:2025 is governing seismic basis (DUDBC). Wall model formulation: Kolozvari et al. (2023), https://doi.org/10.1016/j.engstruct.2023.116700. Research device context: Korkmaz & Kircil (2026), https://doi.org/10.3390/buildings16040711. Only cite the relevant physical domain: these papers do not validate this specific building.

## Verification

Unit test: tests/verify_wall_geometry_preflight.py. This is a solver-free input/response behavior check. A successful test cannot establish true nonlinear wall convergence, experimental calibration, structural performance or device approval. Native OpenSeesPy and source ETABS comparisons must still be run.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
