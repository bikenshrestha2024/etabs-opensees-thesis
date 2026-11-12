# etabs_comparison.py — source documentation

**Python source:** [components/validation/etabs_comparison.py](../../../../components/validation/etabs_comparison.py)
**Git baseline content SHA:** 4ad38ebb75318552ec43d9c64f7cb8878ee92cf9
**Subsystem:** Code criteria, benchmark comparison and experimental evidence
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the validation implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R04 R05 R10 R12 R13. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 source-first automatic ETABS CSV selection

`find_verified_etabs_csv(export_dir,results_root)` automatically reuses only `ETABS_Comparison_V148/ETABS_API_Normalized.csv` when `ETABS_API_Mapping_SELECTED.json`, `ETABS_API_Provenance.json` and original EDB are present and `edb_sha256`, EDB path and `assumptions_verified` match. Rejects blank/incomplete native CSV and mismatched EDB. Native CSV auto-selection is **not** a substitute for initial review of source case mapping. `OpenSees_Normalized.csv`, `ETABS_Normalized_Input.csv`, `NBC105_ESM_Storey_Forces*.csv`, review ZIP snapshots and original unverified workbooks must never be treated as native ETABS response.

The GUI shows why automatic selection was blocked, retains a clearly marked manual advanced option and allows one-click retry. The comparison must be REFRESHED after the MRSM/ESM solver finishes; an older zero-data comparison at 15:33 does not show whether a later 15:46 MRSM run completed. The API path remains read-only and is not a certified equivalence finding merely because rows can be compared.
