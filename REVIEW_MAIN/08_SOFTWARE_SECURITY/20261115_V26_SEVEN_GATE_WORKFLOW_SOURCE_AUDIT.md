# V26 — seven requirements, source audit scope, test evidence and structured outputs

Date: 2026-11-15. Base head: `dd893861d89b32bcab50bd5c35108dce53fba32f`.
**Overall**: `TARGETED_NONLINEAR_FAILURE_EVIDENCE_REPAIRED_ALL_SEVEN_NATIVE_OR_GLOBAL_GATES_STILL_OPEN`.

## Inspected scope
GitHub recursive tracked tree at start of review: **2,991 blobs**; count is revision-specific and does not prove semantic review. Read `AGENTS.md`, engineering core rules, current GitHub Actions outcome, `components/nonlinear_time_history/failure_evidence.py`, its tests and module guide, `components/inputs/output_contract.py` atomic publisher and existing migration rules. This review inspected the exact functions `_solver_time_evidence`, `_validate_capture_limits`, `_focus_tags`, `snapshot_selected_state`, `snapshot_failed_step`; remaining files have not been asserted semantically reviewed.

## Seven requirements

| Requirement | Confirmed V26 code work | Acceptance condition / open status |
|---|---|---|
| G1 All files semantic audit | Source/function review of failure snapshot writer, exact Git blob/line register | **OPEN**: ~2,991 files require actual per-file review at each current source revision |
| G2 Complete legacy writer/reader migration | Adopted atomic JSON writer for two nonlinear failure-evidence outputs, preserved caller-selected paths | **OPEN**: every old producer/consumer/GUI/Excel/ZIP path still needs migration+reopen regression |
| G3 Windows GUI regression | Previous headless Windows 3.12 workflow stays available | **OPEN**: no actual Windows/Tk desktop or ETABS COM activity performed |
| G4 X-wall first-step instability | Nonfinite clock, damaged source mapping, tag coercion no longer erase or mislabel failure evidence | **OPEN**: native solver root cause and model-specific material/geometry validation missing |
| G5 32/76/97 physical supports | No physical supports changed | **OPEN**: compare native restraints, model DOFs, source mapping and signed six reaction components |
| G6 ETABS–OpenSees equivalence | No engineering calculations or source mass/stiffness changed | **OPEN**: matching geometry, gravity, modal, ESM/MRSM, drift and P-Delta on real model |
| G7 Full-duration nonlinear sensitivity | No run was marked completed; failed-step trace now more reliable | **OPEN**: execute all real matched full-duration cases, convergence, calibration, time-step tests |

## Review and result folders

- Engineering issue record: `REVIEW_MAIN/06_NONLINEAR_TH/20261115_V26_XWALL_FIRST_STEP_FAILURE_EVIDENCE_INTEGRITY.md`.
- Repo-wide software status: this file in `REVIEW_MAIN/08_SOFTWARE_SECURITY/`.
- Exact inspected source rev: `docs/review/ledger/REVIEW_LEDGER_V26_20261115_TARGETED.csv`.
- Editor provenance: `engineering/agent_edits/20261115_CHATGPT_V26_SOURCE_AUDIT.md`.
- New private local native run results remain under the selected ETABS export `07_NONLINEAR_TIME_HISTORY/RUNS/<STATE>/<CASE>/<RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`.

No original EDB, authoritative Excel Aw/T1, private accelerograms or model parameters were changed; no synthetic test is treated as a native case.
