# Cross-module production output audit and migration status

**Scope:** Source-controlled Python stage output ownership, written 2026-11-21. This report must not be interpreted as a native Windows run or comprehensive semantic certification.

## Owner matrix

| Stage | Existing production pattern | Fix / remaining gate |
|---|---|---|
| 01 ETABS export | root-source flat files; `export_mirror` copy-only categorized exports | Existing root provenance and project manifest retained. A full writer+reader migration of root data is **open**, because generated Python/model JSON/Excel paths are source-linked |
| 02_MODEL | stage directories created, model JSON and scripts still at export root | Review root-producing conversion workers with native ETABS model hash; do not move source files |
| 02_GRAVITY | GUI default formerly `Path.cwd()/OpenSees_Analysis_Results/Gravity_Results`, sometimes distinct from chosen model | Automatic path now derived from model source into `02_GRAVITY/RUNS/<model-stem>`. Explicit external override allowed; wrong-stage and legacy in-project selections remap to gravity stage |
| 03_ESM | previous shared `OpenSees_Analysis_Results` destination | PR #134 introduced new stage path and legacy import fallback; this branch inherits that work |
| 04_MODAL | `prepare_canonical_modal_run` creates `04_MODAL/RUNS/<state>/<case>/<run-id>/02_RESULTS` | Preserve; custom output pathways still require review and Windows regression |
| 05_MRSM | `create_case_run(...,'MRSM',...)` writes state/case/run path | Preserve; validate reader-side discovered cases |
| 06_LINEAR_TIME_HISTORY | automatic `prepare_history_run`; custom selected output may be project root or wrong stage | Custom in-project selections now remap to `06_LINEAR_TIME_HISTORY/RUNS/<case>`; external explicit override preserved |
| 07_NONLINEAR_TIME_HISTORY | automatic `prepare_history_run`; custom selected output may be project root or wrong stage | Custom in-project selections now remap to `07_NONLINEAR_TIME_HISTORY/RUNS/<case>`; external explicit override preserved |
| 08_ETABS_COMPARISONS | dedicated comparison tools and local case reports | Mixed producers require broader source-identity review; no automatic source migration |
| 09_SOFTWARE_DIAGNOSTICS | separate reports and native diagnostics | Preserve evidence, do not put diagnostic files in solver result case folders |
| 90_UPLOAD_PACKAGES | upload bundles and redacted manifests | Upload only approved/sanitized content; never automatically publish native source assets |

## Changes

- `components/inputs/output_layout.py` provides `owned_run_destination`: a pure, no-mkdir resolver for any named canonical stage. If a user selects the case root or a wrong/legacy *in-project* directory, new outputs resolve into the requested owner's `RUNS` subtree. Existing correct-stage paths remain unchanged; an explicit location outside the project remains a custom override. Linked destinations and traversal case names are rejected.
- The gravity GUI no longer defaults to an arbitrary current working directory. Its output derives from the selected model, with custom override tracking.
- LTHA/NLTHA custom-output branches use the same safety guard. Their existing automatic, source-identified `create_case_run` paths are unchanged.
- `tools/audit_output_stage_ownership.py` scans all active Python, classifies potential writer references by owner and records the legacy-path review queue; CI protects known high-risk stage routes against regressions.

## Open acceptance gates

1. Verify all saved input and output GUI controls, case status and plot/export/reload paths against actual Windows sessions for each stage and both ULS/SLS.
2. Reconcile root-level generated model scripts, JSON/CSV and Excel files with `01_ETABS_EXPORT` mirrors and `02_MODEL` consumers *before* any move/delete.
3. Inspect **every** remaining static legacy-path candidate by function: classify writer, reader, intentional compatibility or uncertain dynamic path; document resolution and tests. Existing `integrated` static audit may still be BLOCKED.
4. Compare model hashes in every cross-stage import. A valid folder path alone cannot prove physical equivalence or a completed NLTHA run.
5. Native ETABS/OpenSees equivalence and nonlinear first-step X wall remain independent P0 gates.

No automatic merge to main is authorized until full regression and native workflow gates are satisfied.

## Second-pass active legacy writer findings and repairs

The full active Python AST scan examined **380 active source files** and found **1,134 possible writer calls**. Thirty-four files contained both legacy path references and possible writes. These are *candidates*, not 34 confirmed bugs; paths can appear in legitimate fallback reads. The source survey intentionally excludes historical `Saved_Project_V156`, code examples, generated exports and tests from the active source inventory, while repository-wide CI checks those separately. Every remaining candidate requires a call-site and native producer/consumer review.

Confirmed new-file destinations corrected in the second pass:
- `components/model/readiness_dashboard_gui.py`: readiness JSON/Markdown, independent tool logs, nonlinear wall probes and native device benchmark outputs now route into separate `09_SOFTWARE_DIAGNOSTICS/RUNS/<case>` locations.
- `components/validation/response_checks.py`: the historical irregularity-view GUI creates a source-owned `09_SOFTWARE_DIAGNOSTICS/RUNS/AS_CONFIGURED/<case>/<run-id>/02_RESULTS` output, and now discovers existing irregularity source records from both `03_ESM` and the legacy shared tree.
- `components/validation/irregularity_review.py`: the active Clause 5.4 GUI saves new results under `09_SOFTWARE_DIAGNOSTICS/RUNS/IRREGULARITY_REVIEW_V134`, not `OpenSees_Analysis_Results`.
- `components/model/readiness_gui.py`: research material draft output goes under the diagnostic stage, not the shared results tree.
- `components/ui/building_exploratory_gui.py`: auto/default and in-project custom exploratory NLTHA output routes under `07_NONLINEAR_TIME_HISTORY/RUNS`.
- `components/model/readiness_dashboard.py`: evidence discovery additionally inspects known canonical stage subfolder shapes while retaining historical paths. No folder presence alone is treated as a successful solver execution.

The existing root model JSON/PY/XLSX files are deliberately unchanged because the model builders and saved manifests still consume those exact paths. The mirror script in PR #134 provides an auditable, copy-only arrangement, not a destructive move. A repository-wide mandate to delete all flat root files is unsafe without dependency migration and native reruns.

### Review queue / acceptance

The full 34-candidate file-and-line register is emitted as `legacy_reference_review_queue.csv` by `tools/audit_output_stage_ownership.py --report-dir` and attached to the cross-module CI workflow; it should be classified line-by-line into LEGACY_READ, LIVE_WRITER, GUI_OVERRIDE, DYNAMIC_CALLER, HISTORICAL or UNRESOLVED. Remaining wider gates include `components/ui/organized_results.py`, `components/validation/design_checks.py`, `components/validation/etabs_comparison.py`, `components/inputs/project_workbooks.py`, and historical launcher scripts. Native Windows reruns must demonstrate every stage's exact source hash, output paths, GUI reload and no duplicate live analysis writes before approval.
