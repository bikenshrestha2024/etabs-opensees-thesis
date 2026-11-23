V144 numbered workflow navigation now uses canonical program names. It searches top-level and nested model/state result candidates but NEVER treats file existence as solver completion, model equivalence or NBC acceptance. This is read-only, manually refreshed directory discovery. See tests/test_import01_audit_and_workflow.py for synthetic regression. Full native Windows search and source hash validation remain pending.

## 2026-11-15 canonical workflow candidate discovery

`workflow_status` now searches **stage-owned** `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY` trees and the preserved legacy `OpenSees_Analysis_Results` in parallel; it does not falsely infer absence because only the older legacy tree was searched. Stage source/inputs are read at the selected export root and `01_ETABS_EXPORT` categorized mirrors. Processing sidecars are not analysis files, and a file named Summary remains **CANDIDATE_FILE_FOUND_VALIDATION_REQUIRED**, not completed or conforming. The GUI Export inventory action writes immutable unique run reports under `01_ETABS_EXPORT/00_MANIFEST/INPUT_READINESS`, not another root-level `Available_Inputs_And_Steps_V144.json`. Existing root reports are not moved or deleted.

Unit regression: `tests/test_export_workflow_roles.py` and `tests/test_import01_audit_and_workflow.py`. This does not establish full motion duration, model SHA identity, source mass equivalence or native ETABS/OpenSees validation.

The record-pair checklist displays the same NBC gravity constant as the transient runtime. In a metre-based model, Acc(g) uses 9.81 m/s² per g once. Input already in m/s² uses 1. The numerical motion scale is a separate, dimensionless input. An inventory records the review instructions and leaves checklist approval to the reviewer.


## 2026-11-23 — direct available values in workflow inventory

`inventory(folder)` includes `direct_available_values` from `components.model.readiness_available_values.collect_available_project_values` when the current nonlinear model builder exists. The data are read only from the selected local export and installed, cited PEER specimen cards. Incomplete source values remain missing and the snapshot explicitly states `UNAPPROVED`. Existing steps and GUIDE remain intact; no source-input, approval, material or FSAM field is changed.


## 2026-11-23 — Evidence-aware status in the 1–9 GUI

The original `workflow_status()` remains a **filename discovery API**, returning nine candidate/no-file pairs unchanged for compatibility. The GUI uses `workflow_evidence_status()` to distinguish source-only and review-snapshot ESM files from canonical stage solver results. For a candidate under a true `<stage>/RUNS/<state>/<case>/<run-id>/02_RESULTS/` directory, it inspects `CASE_MANIFEST.json` through the central `inspect_case_manifest` and checks the full recorded model SHA against the selected current `OpenSees_Complete_Model_Data_V118.json`. Missing model source, changed SHA, malformed/misfiled manifest, or non-completed solver status are explicitly distinguished and remain unverified.

Even a matching model SHA and `COMPLETED_SOLVER_ONLY` status produce only **MANIFEST COMPLETED - NUMERICAL EVIDENCE UNVERIFIED**, not native structural equivalence or full physical record completion. A file under `REVIEW_SNAPSHOTS` is a review artifact, not a solved ESM analysis. Historical legacy results remain visible with no false approval. Non-discovery means **no file discovered in searched locations**, not proof no run exists. Linear TH remains optional for NLTHA. Synthetic tests: `tests/test_workflow_evidence_status.py`. No engineering models, recorded support fixes, or source EDB changed.
