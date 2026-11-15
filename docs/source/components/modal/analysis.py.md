# analysis.py — source documentation

**Python source:** [components/modal/analysis.py](../../../../components/modal/analysis.py)
**Git baseline content SHA:** 364f8060812a9dd156cf423fa3369e22d137a0d3
**Subsystem:** Modal analysis and numerical damping
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the modal implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-15 exact mode-count gate

The shared eigensolver and modal audit reject fractional, boolean and nonfinite requested mode counts rather than silently truncating them with `int()`. The MRSM caller validates the count before model assembly; the modal audit validates manually selected X/Y fundamental modes and a positive finite frequency threshold. The already-working integer-count eigen solver and source model parameters are unchanged. Regression: `tests/test_modal_mode_count_contract.py`; engineering review: `REVIEW_MAIN/04_MODAL/20261115_MODAL_MODE_COUNT_NUMERIC_IDENTITY_GATE.md`. Native modal mass, ETABS equivalence, mode-shape physics and NBC 105:2025 acceptance remain NOT_VERIFIED.
