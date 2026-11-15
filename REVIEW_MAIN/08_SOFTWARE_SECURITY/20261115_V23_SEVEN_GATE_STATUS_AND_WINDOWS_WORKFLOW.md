# V23 — Seven-gate repository acceptance, output structure and Windows regression
**Date:** 2026-11-15  
**Reference HEAD at review start:** `7144c7cabe375bd7fda1f34dcb7fd3cf3e52c572`  
**Overall:** `TARGETED_P0_P1_SOURCE_FIXES_COMMITTED; NATIVE_ACCEPTANCE_OPEN`

## Scope accounting

A recursive GitHub tree listing found 2,973 tracked blobs before V23. Read `AGENTS.md`, existing source-review ledger, eight open PR titles, CI definitions, support sensitivity code/tests, accepted full record and time-step gate code/tests, soil-C run-matrix auditor/tests, project output mapping, and existing native wall-probe runner. Full semantic line-by-line coverage of all 2,973 blobs did **not** occur. The frozen `docs/review/ledger/` status cannot be upgraded from static inventory.

## Seven requested work items

| ID | Requested deliverable | Completed source work this round | Actual status / mandatory evidence to close |
|---|---|---|---|
| G1 | Every file reviewed line-by-line | Focused examination and tested edits of identified modules; source tree + PR overlap inventoried | **OPEN.** Per-file, per-function semantics and actual source SHA must be recorded for all active files, then archives; AST-only inventories are not semantic review. |
| G2 | Complete legacy writer/reader migration | V22 writer and filesystem inventory tools remain in place; V23 does not move historical outputs | **OPEN.** Stage-by-stage producers, GUI readers, ZIP/Excel/plot publishers and old output compatibility must all be tested before moving a location. |
| G3 | Native Windows GUI regression | Added `.github/workflows/windows-source-contract.yml` for Windows 3.12 **headless** filesystem, source, gravity and NLTHA tests. Includes Tcl availability check; labels itself NOT native ETABS or interactive GUI | **OPEN.** Requires actual Spyder/Tk interactions, ETABS COM OAPI, scroll/copy/status/cancel/export and reopen on native workstation. |
| G4 | X-wall first nonlinear step | Existing native ZERO/X/Y/XY probes and wall/failure diagnostics reviewed; no unsafe model-material override | **OPEN.** Native wall constitutive tests and original ~0.005 s source step/root cause, element mapping and last accepted state required. |
| G5 | 32/76/97 support equivalence | Rejected duplicate/missing/nonfinite/coordinate-inconsistent support evidence and mismatched reaction row totals | **OPEN.** Native restraint DOFs/axes, signed six components, source EDB identity, gravity load/mesh convergence and actual base reaction attribution needed. |
| G6 | ETABS–OpenSees numerical equivalence | Existing code identity/case gates preserved | **OPEN.** Independent ETABS and OpenSees runs on matching geometry, mass, wall frame properties, diaphragm, gravity reactions, period, ESM/MRSM scaling, displacement, drift, torsion, P-Delta, local element forces. |
| G7 | Full-duration nonlinear sensitivity | Hardened 224-case scanner: SHA256 grammar, measured source/requested/achieved durations, accepted state count | **OPEN.** Full paired native XY/YX records, two states, M0–M6, device/material calibration, time-step sensitivity and explicit failure handling. |

## Source code and regression corrections

- `components/gravity/support_scenarios.py` with `tests/verify_gravity_support_scenarios.py`: no duplicate node tags, no coordinate-mismatched reaction comparisons, validated source-only XYZ and independent nodal-sum-to-report agreement.
- `tools/audit_soil_c_case_completion.py` with `tests/verify_soil_c_case_completion.py`: research full-duration screen cannot rely on a status boolean or an invalid SHA256 string.
- `.github/workflows/windows-source-contract.yml`: Windows-latest, Python 3.12, no source uploads, headless Tcl and source tests. **Passing Windows headless CI is not a GUI/OAPI test.**

## Output hierarchy for each new producer (not yet universally migrated)

```text
<SELECTED_EXPORT_CASE>/
├── 00_SOURCE_MANIFEST/
├── 01_ETABS_EXPORT/
├── 02_MODEL/
├── 02_GRAVITY/
├── 03_ESM/
├── 04_MODAL/
├── 05_MRSM/
├── 06_LINEAR_TIME_HISTORY/
├── 07_NONLINEAR_TIME_HISTORY/
├── 08_ETABS_COMPARISONS/
├── 09_SOFTWARE_DIAGNOSTICS/
├── 90_UPLOAD_PACKAGES/
├── REVIEW_MAIN/
└── OpenSees_Analysis_Results/  (historic; preserve readers)
```

Use `<STAGE>/RUNS/<STATE>/<CASE_ID>/<UTC_RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}` for **newly migrated** runs and retain source/model SHA in `CASE_MANIFEST.json`. Do not move files from live stage writers until tested GUI consumers and archives can still reopen them.

## Next native execution on Windows

1. Checkout current main and execute source tests, especially the Windows source-contract workflow. Confirm that a headless pass and model-specific acceptance are kept distinct.
2. Run `tools/audit_active_repository.py`, `tools/audit_live_output_writers.py`, `tools/audit_stage_output_migration.py` against the **selected local export case**; keep local private diagnostics outside GitHub.
3. Run the existing original gravity/32 support scenario, 76 source restraints and 97 continuous wall only in independently identified native cases; preserve six-component ETABS reactions and original source EDB identity.
4. Run the existing research-only `tools/run_native_wall_probes.py` preparatory workflow followed by explicitly approved native probes with source configuration/record SHA checks. Uncalibrated material cards remain blocked for `THESIS_NLTHA`.
5. Complete ULS and SLS stage-by-stage comparisons and then all 224 native orientation records with drift/shear/torsion/damper outcomes, accepted states, failure logs and source hashes.
6. Record sign-off with numerical acceptance tolerances and independent verification under `REVIEW_MAIN`.

**Engineering prohibition:** no native result was executed by GitHub source access. This report records open gates, not a completed physical verification or NBC compliance certificate.
