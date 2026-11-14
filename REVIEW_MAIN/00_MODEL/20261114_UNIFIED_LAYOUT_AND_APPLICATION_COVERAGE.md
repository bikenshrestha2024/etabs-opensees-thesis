# 2026-11-14 unified outputs and latest reviewed application status

**Scope:** review and documentation of live repo `main` plus PR #46 changes. Source: 2026-11-14 user screenshots, ESM `CASE_STATUS(1).json`, individual six case logs, source metadata, run index and repository `AGENTS.md`. Do **not** promote numerical success to ETABS equivalence or NBC code approval.

## Current software changes from PR #46
- Shared stage lookup in `components/inputs/output_layout.py` returns **only** the per-stage `REVIEW_SNAPSHOTS` parent. No original generated cases are moved/deleted.
- Gravity and ESM both resolve destination from the selected case's export root rather than duplicating hard-coded path logic.
- ESM `CASE_STATUS.json` must match the exact set of *current runner script filenames* one-to-one, with no unexpected, missing or duplicate cases, success status and exit code zero. A six-row success list that doesn't match the current six scripts is NOT a complete run.
- ESM workbook gets case-by-case `Solver Batch Status`, source status hash, warnings and uniform worksheet styling. Numerical calculation sheets retain their original semantics.
- Existing `09_ORGANIZE_ETABS_EXPORT.py` generates `01_ETABS_EXPORT/00_MANIFEST/analysis_stage_index.json`, a lightweight per-stage navigation index. It does not infer an absent legacy run or mark any physically accepted results.
- Previously published ESM and gravity ZIPs remain immutable. Old `OpenSees_Analysis_Results` producer and consumer paths retain compatibility.

## Verified user-provided ESM batch facts
- Uploaded six-case status manifest: X+ E+/E-/E0 and Y+ E+/E-/E0, all six `SUCCESS` with return code 0.
- Run timings (seconds): **889.734, 139.203, 140.094, 151.469, 154.890, 149.954**. The cold first case includes four signed initial IS 16700 P-Delta solves; warm cases explicitly log fingerprint-matched reuse, not imported solver-state transfer.
- Example X and Y design shears remain **25659.046 kN** and **26450.735 kN**, respectively; full six-case response fields require actual case output audit before any ETABS parity claim.
- Gravity `AS_CONFIGURED` uses D=1 and Live=0.3; its preload (~286419.758 kN) is *not* the same as the native ETABS 1D+1L gravity comparison (~311367.314 kN). Don't compare those as the same case or conflate seismic mass factors with gravity load combinations.
- ULS ESM for this high-rise is labeled **COMPARISON_ONLY** by the user's NBC 105:2025 §3.2.1 workflow, and Vs30 classification and actual input spectrum/code eligibility remain open.
- Direct historical ETABS-linked Excel X-wall Aw (**1.95829363 m²**) differs from the reviewed 12-m X-wall grouped model (**2.07317452 m²**); Y Aw **2.20308033 m²**; keep both with metadata, do not overwrite workbook or silently approve either.
- Completed six-case numerical statuses do not resolve 32/76/97 reaction redistribution, slab/wall-to-beam load path, pinned brace moment/torsion transfer, or 4/8/16 mesh convergence.

## Cross-module request coverage
| Requirement | Actual repo implementation | Remaining gate |
|---|---|---|
| ETABS import export folder | Existing `export_mirror.py` + optional new index | Canonical live file writer/read migration pending; no deletion of flat files |
| Gravity stage | Review snapshots under `02_GRAVITY` and original source case logs | 76-source DOF/ETABS per-node parity, mesh interfaces and original assignments |
| ESM stage | Review snapshots under `03_ESM`, exact solver status and workbook | ETABS structural parity, Vs30, nonlinear readiness, high-rise ESM code restriction |
| ID tags | Human display aliases N/B/C/BR/CO/BT/CT/SW/FL supported | Explicit source member classification + regenerate current HTML/Excel |
| 3D plots | Shared selection/camera and grouped legends partly implemented | Full Windows browser performance, all visual module parity |
| Material/section Excel | Separate export launcher supported | Actual ETABS input identity and project nonlinear material calibration |
| FVD/BRB guide | Selection and documented review gate | Device qualification and connection element benchmarks |
| PDelta | Four signed cases with content fingerprint cache | Source-identical ETABS tangent-state comparison, not inferred from solver converged status |
| Modal, MRSM, LTHA, NLTHA | Historical independent stage launchers retained | Comprehensive stage-local writer migration and native outputs pending |
| Source citations | Literature guides, OpenSees docs, code matrix and review registers | Verify individual papers/code clauses and project applicability |

## Operating procedure
1. Update local checkout from `main` and fully restart the launcher. The old V116 title may remain a legacy module name; use the active path/version diagnostic rather than assuming GitHub source is currently loaded.
2. For an existing export, run `python 09_ORGANIZE_ETABS_EXPORT.py "<selected export folder>"`. It copies categorized ETABS artifacts under `01_ETABS_EXPORT` and writes `analysis_stage_index.json` with *navigation-only* statuses.
3. Use Gravity and ESM review export actions to publish *new* ZIP/workbook snapshots under their matching stage folders; do not rerun completed six ESM cases just to update the ZIP organization.
4. Do **not** delete, rename or relocate the legacy source/solver output files. Compare SHA and actual source/solver case identity before engineering review.
5. The primary physical P0 tasks are an identical 76-support ETABS/OpenSees gravity comparison, source stiffness/mesh constraints, wall/slab load-path benchmark, and member-specific hinged brace verification before NLTHA design acceptance.

**Native validation:** Not run by this pull request. Unit/CI tests validate only software behavior. The absence of a stage folder and the existence of a successful numeric run are not design accept/reject decisions.
