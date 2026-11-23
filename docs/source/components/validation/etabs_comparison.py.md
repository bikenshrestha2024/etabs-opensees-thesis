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

For a canonical run, `find_native_reference_csv` also accepts a native reference bundle under `05_COMPARISONS/ETABS_NATIVE_REFERENCE`. The provenance must match the run ID, original EDB path, EDB SHA-256 and CSV SHA-256. The GUI shows those references immediately under their native case names. This load path grants no approval of case equivalence.

`find_verified_etabs_csv(export_dir,results_root)` automatically reuses only `ETABS_Comparison_V148/ETABS_API_Normalized.csv` when `ETABS_API_Mapping_SELECTED.json`, `ETABS_API_Provenance.json` and original EDB are present and `edb_sha256`, EDB path and `assumptions_verified` match. Rejects blank/incomplete native CSV and mismatched EDB. Native CSV auto-selection is **not** a substitute for initial review of source case mapping. `OpenSees_Normalized.csv`, `ETABS_Normalized_Input.csv`, `NBC105_ESM_Storey_Forces*.csv`, review ZIP snapshots and original unverified workbooks must never be treated as native ETABS response.

The GUI shows why automatic selection was blocked, retains a clearly marked manual advanced option and allows one-click retry. The comparison must be REFRESHED after the MRSM/ESM solver finishes; an older zero-data comparison at 15:33 does not show whether a later 15:46 MRSM run completed. The API path remains read-only and is not a certified equivalence finding merely because rows can be compared.

## 2026-11-22: live native values and strict source-bound comparison

The comparison window now offers **Read native ETABS values (live, read-only)**. It connects to the *already-open exact source EDB* via the read-only CSI result API, lists actual load-case/combination names, and shows signed BaseReact FX/FY/FZ/MX/MY/MZ values in a separate table. The response is explicitly **RAW_ETABS_BASE_REACTIONS_SIGNED_NOT_CQC_NBC_MATCHED**, and is saved to a timestamped local `ETABS_Comparison_V148/Native_Observed/` JSON/CSV snapshot. No ETABS run, unlock, save or source mutation occurs. GUI supports a *preview-only* manual link to an OpenSees **MRSM BASE** shear row, with status **RAW_ETABS_PREVIEW_NOT_COMPARABLE**, no percentage error and no engineering acceptance.

To make an actual comparison with populated `etabs_value`, use **Direct ETABS API / EDB** with the exact selected EDB, reviewed case/story/point mapping and matched CQC/§7.5 force basis. Successful mapping emits `ETABS_API_Normalized.csv`, mapping JSON and EDB/model/native-CSV SHA-based provenance. The small normalized bundle is mirrored under the source-owned `05_COMPARISONS/ETABS_Comparison_V148` to be reusable across immutable individual MRSM run folders. `verify_native_bundle` refuses stale EDBs, changed model payloads, tampered CSVs, missing approved case mapping or incomplete normalized columns. Auto-selection carries the verified mapping policy only for the exact auto-selected CSV; selecting arbitrary local CSV does not grant approval.

**Critical stage identity:** older MRSM JSONs may have the correct geometry model SHA but lack *executed* `support_case`, `seismic_mass_policy` and actual runtime evidence. `source_execution_identity` and `compare` label those historical responses **NOT_COMPARABLE** even where a numeric native result has exactly the same semantic key. The comparison GUI now allows filtering the **32 physical support** case (default), 76/97 diagnostic sensitivities and distributed/optional story-lumped mass. Never infer native physical parity from geometry SHA or model name.

The three 2026-11-22 uploaded MRSM evidence ZIPs did not contain native analyzed ETABS responses. Live Windows ETABS v23 extraction is not performed by Linux CI and remains a native acceptance requirement.


## 2026-11-23 — Blank ETABS values: diagnostic presentation

The ETABS comparison window shows native `etabs_value` only when actual matching ETABS data have been loaded. If no normalized CSV / approved Direct ETABS API extraction is present, the OpenSees rows receive the **GUI-only** status `ETABS_DATA_NOT_LOADED` with a source-specific instruction; ETABS numeric values and percentage differences remain null, never zero. The underlying saved OpenSees response CSV and numeric comparison policy are unchanged. After a reviewed exact-source ETABS case/story mapping is applied using **Direct ETABS API / EDB…**, the window reports how many rows have matched native values and how many remain unmatched. Unmapped raw signed ETABS reactions must never be silently inserted into CQC-scaled MRSM fields. Synthetic tests: `tests/test_comparison_missing_native_status.py`.
