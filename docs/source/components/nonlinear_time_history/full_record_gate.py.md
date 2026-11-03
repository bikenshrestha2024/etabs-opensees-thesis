# full_record_gate.py — implementation guide

**Source:** [components/nonlinear_time_history/full_record_gate.py](../../../../components/nonlinear_time_history/full_record_gate.py)
**Source blob SHA:** 32594f1c60b01be293008172ab63ad7e2d6800d2
**Workstream:** 05 full record evidence.

## Input contract and failure gate

Use the module's exact function docstrings and the corresponding stage guide under docs/programs. All data are kN-m-s model units unless source quantities explicitly say mm, MPa or g. Nonfinite, missing, mismatched or unapproved inputs must block the relevant analysis rather than be interpreted as zero.

## Provenance and cited method

NBC 105:2025 is governing seismic basis (DUDBC). Wall model formulation: Kolozvari et al. (2023), https://doi.org/10.1016/j.engstruct.2023.116700. Research device context: Korkmaz & Kircil (2026), https://doi.org/10.3390/buildings16040711. Only cite the relevant physical domain: these papers do not validate this specific building.

## Verification

Unit test: tests/verify_full_record_gate.py. This is a solver-free input/response behavior check. A successful test cannot establish true nonlinear wall convergence, experimental calibration, structural performance or device approval. Native OpenSeesPy and source ETABS comparisons must still be run.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
