# variant_comparison.py — implementation guide

**Source:** [components/nonlinear_time_history/variant_comparison.py](../../../../components/nonlinear_time_history/variant_comparison.py)
**Source blob SHA:** cf469f3355b250b6f7df1233145ccd227ea6108b
**Workstream:** 06 M0–M6 source-matched comparison.

## Input contract and failure gate

Use the module's exact function docstrings and the corresponding stage guide under docs/programs. All data are kN-m-s model units unless source quantities explicitly say mm, MPa or g. Nonfinite, missing, mismatched or unapproved inputs must block the relevant analysis rather than be interpreted as zero.

## Provenance and cited method

NBC 105:2025 is governing seismic basis (DUDBC). Wall model formulation: Kolozvari et al. (2023), https://doi.org/10.1016/j.engstruct.2023.116700. Research device context: Korkmaz & Kircil (2026), https://doi.org/10.3390/buildings16040711. Only cite the relevant physical domain: these papers do not validate this specific building.

## Verification

Unit test: tests/verify_variant_comparison.py. This is a solver-free input/response behavior check. A successful test cannot establish true nonlinear wall convergence, experimental calibration, structural performance or device approval. Native OpenSeesPy and source ETABS comparisons must still be run.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## 2026-11-04 eight-pair NBC response aggregation addition

The ULS and SLS outputs now retain both `maximum` of all orientation-cases AND a separate `nbc105_aggregate`, which for **8 complete pairs** is an **AVERAGE of each event's governing XY/YX demand**. `response_per_pair_governing` uses the larger of XY/YX for each event as a documented conservative engineering orientation rule; review this interpretation separately from literal NBC §9.3.3 wording. All eight pairs and all fourteen per-event X/Y records for all seven variants must be complete, source-hash matched and finite. Exactly-seven suite remains interpretation-required; do not call a mixture of failed runs a full suite. Review the complete JSON schema [Stage 37](../../../programs/37_SOIL_C_NLTHA_JSON_SCHEMA.md).
