# reports.py — source documentation

**Python source:** [components/response_spectrum/reports.py](../../../../components/response_spectrum/reports.py)
**Git baseline content SHA:** d136a968b6dfb5fbe418db5e414873a5f4902c9d
**Subsystem:** Modal response spectrum and NBC scaling
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the response_spectrum implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 NBC 105:2025 §5.5 audit and canonical saved-result choice

`saved_cases` prefers only current `MRSM_ULS/MRSM_Results_V132.json` and `MRSM_SLS/MRSM_Results_V132.json`, and excludes `Organized_Results`, `Seismic_Review_Packages`, `Gravity_Evidence_Upload`, `ETABS_Comparison_V148` snapshots during fallback search. Deduplicates by state, case and model fingerprint. Previously `rglob` could display repeated curves for duplicated report copies. Regression: `tests/test_mrsm_saved_report_deduplication.py`.

Per-case Excel now includes `NBC 5.5 Deflections` with elastic raw master displacement, design master displacement and ratio, elastic and design drift ratios, ULS limit 0.025 / SLS 0.006 and physical acceptance left open. NBC §5.5.1.1 requires ULS ESM/MRSM deflections ×Rμ, §5.5.1.2 requires unamplified SLS deflection; §5.5.3 uses effective §3.4 stiffness. Force-only MRSM base-shear scale is not reapplied to displacement/drift. Native ETABS unamplified solver displacement must only be compared with unamplified OpenSees response; do not accidentally multiply Rμ twice. CQC envelopes are non-concurrent. Official source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf, pp.36–37.
