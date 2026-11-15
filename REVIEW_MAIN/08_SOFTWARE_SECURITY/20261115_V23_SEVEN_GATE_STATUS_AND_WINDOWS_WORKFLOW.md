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

## V23 follow-up: current-head tracked-file review register and actual Windows evidence

A new independent inventory utility `tools/audit_tracked_review_coverage.py` uses Git-index blob identities to enumerate **all tracked files** and creates a **fresh**, private-local `09_SOFTWARE_DIAGNOSTICS/REVIEW_REGISTERS/RUNS/<UTC_RANDOM>/{JSON,CSV,REPORT}` report only when an explicit export directory is supplied. Its default is read-only. Every entry is labeled `NOT_REVIEWED_CURRENT_HEAD`; no historic reviewed status is silently carried across changed blobs. Per-file source inspections must subsequently be documented by a human with exact revision and lines. A new regression and GitHub Actions workflow `review-coverage-inventory.yml` verify its behavior.

**Verified GitHub Actions coverage inventory on commit `ff4c0ad51145580bc6b068bf9bbd80354201510c`:** 2,982 tracked files in that revision, consisting of 325 active Python source, 193 Python tests, 814 historical/archives, 843 documentation/review, 20 GitHub/CI configuration and 787 other files. The inventory reports `reviewed_current_head_count=0` because none were independently attested *through this new register*—**not** because old project reviews have been erased or are necessarily invalid. <https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43671317181> passed. Count changes with future commits; never hardcode it as current forever.

**Native Windows integration boundary:** the new `.github/workflows/windows-source-contract.yml` runs tests using Windows-latest and Python 3.12, confirms availability of a headless Tcl interpreter, and exercises actual Windows filesystem creation, source and audit contracts, gravity support consistency, and Soil-C completion screens. The first two Windows attempts exposed 8.3 short-path aliases (`RUNNER~1` versus `runneradmin`) in synthetic assertions and a direct-script Python import context failure. Test expectations now compare normalized physical paths, and verifier modules run through `python -m unittest discover`. The corrected workflow on commit `2efe7b0cd1e9aec11603f443f9d9f0265b65fe30` **passed**: <https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43671371305>.

These are **Windows headless software checks**, not interactive GUI regression or ETABS OAPI. Native GUI must still be opened on the actual Windows computer with real ETABS/OpenSees executables, source file identities, ULS/SLS outputs and screenshots/logging. Do not promote this result to any of the seven engineering gates marked OPEN above.

### Local commands for current working copy

```powershell
python tools/audit_tracked_review_coverage.py --repo .
python tools/audit_tracked_review_coverage.py --repo . --export "<SELECTED_LOCAL_EXPORT_CASE>"
python -m unittest discover -s tests -p test_tracked_review_coverage_v23.py -v
python -m unittest discover -s tests -p test_project_output_layout_v171.py -v
python -m unittest discover -s tests -p verify_gravity_support_scenarios.py -v
python -m unittest discover -s tests -p verify_soil_c_case_completion.py -v
```

If native files cannot be supplied, the real-source engineering gate remains blocked. Do not make or publish artificial equivalence values or synthetic successful full-duration runs.
