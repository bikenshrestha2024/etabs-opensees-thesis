# ESM combined inspection and non-destructive folder organizer

**What:** Copy-only exporter builds categorized ESM review trees in <ETABS export>/03_ESM/REVIEW_SNAPSHOTS/<UTC timestamp>. Separately names ETABS_Linked_Equivalent_Static and OpenSees_Direct_Equivalent_Static; each then has limit state, case and extension categories JSON, Excel, CSV, Plots, Scripts, Logs and PDF. Creates ESM_Combined_Inspection.xlsx, ESM_Export_Manifest.json, ZIP and LATEST_ESM_COMBINED_EXPORT.txt.

**Why:** The original six X/Y ESM scripts and per-case JSON, CSV, XLSX and PNG are scattered among unrelated gravity and seismic results. Earlier export controls were difficult to find and lacked one combined inspection workbook.

**When:** Export after computing ESM cases; this does NOT launch ETABS or OpenSees.

**Where:** components/equivalent_static/organized_exports.py and calculation_and_gui.py. Legacy producer and script paths remain unchanged.

**Who:** Research software maintainer validates Windows/UI and source fingerprint; qualified engineer independently validates structural response and code compliance.

**How:** Run python -m unittest discover -s tests -p test_esm_organized_export_gui.py -v. Every copied file has a SHA256/source-path record; no original results are moved, overwritten, renamed or deleted. Invalid JSON is marked INVALID SOURCE; absent calculations block the combined output.

**Source and acceptance status:** The user's ~95m high-rise ULS equivalent-static results remain COMPARISON ONLY under NBC 105:2025 §3.2.1. Vs30 evidence remains missing. Previous 6m-bay historical ETABS Aw-X=1.9582936 m² versus 12m grouped OpenSees Aw-X=2.0731745 m² is unresolved, not automatically reconciled. A linked Excel copy is not a solved native ETABS response.

**Engineering limitations:** A generated applied lateral Fi profile is not recovered story shear, drift or stiffness. Source EDB and model SHA identity plus actual ETABS cases/stories and dynamic basis are required before native ETABS comparison. For a true governing dynamic analysis use MRSM/NLTHA per applicable code and validated model.


## 2026-11-14 canonical shared layout and exact batch identity (mainline update)
The exporter calls `components.inputs.output_layout.review_snapshots_for(..., 'ESM')`, shared with gravity stage routing. It still creates immutable review **copies**, never moves active generated runners or edits the EDB. `Solver Batch Status` now includes individual solver cases, exit codes and elapsed seconds, the SHA256 of source `CASE_STATUS.json`, and lists of missing, duplicate and unexpected case identifiers. Completion requires an exact one-to-one match of the current generated runner script filenames with successful `CASE_STATUS` records (exit code 0); record count alone is no longer sufficient. A `COMPLETE_SOLVER_ONLY` label **never** means source-verified ETABS parity or NBC high-rise eligibility. Historical exports under `ESM_Organized` remain readable in their original location; only newly created snapshots use the canonical parent. The calculation JSON is not evidence that a corresponding solver case ran.

**Validation:** `python -m unittest tests.test_output_layout tests.test_organized_results tests.test_esm_organized_export_gui -v`. CI tests synthetic model/output metadata, not native structural response. User must restart the Windows launcher after updating `main`, then generate a new review ZIP; existing ZIPs will not be rewritten.


Relative `snapshot_path` values use forward slashes and match ZIP member names on both Windows and Linux.

**Pending batch identity gate.** A regenerated runner with the same filename can match a previously saved successful status row. Verify the SHA256 of each executed runner against the current script before using historical batch status as evidence of the current inputs. The status file SHA256 fingerprints the saved status, while executed-runner identity requires its own digest recorded at execution.


## ESM route identity and reviewed wall basis

Combined snapshots include the calculation comparison and ESM case-specific deformation, drift, irregularity and recorder-index sidecars. Legacy and route-prefixed runners for the same case are reconciled by the batch status.


## 2026-11-23 — Split legacy GUI path and canonical ESM case evidence

**Observed workflow:** ESM case calculations are written to the exact model/state
`03_ESM/RUNS/ULS/<case>` while a legacy selected GUI output remains under
`OpenSees_Analysis_Results/<case>`. Earlier `_exact_calculation_roots`
located JSON/CSV in the canonical sibling, but `_source_files` omitted the
canonical runner, plot, response CSV/Excel and recorder sidecars; likewise
`_latest_batch_status` compared legacy `CASE_STATUS.json` only with
legacy-local runners. This made valid canonical outputs disappear from a
combined ZIP or appear as missing solver cases.

**Correction:** Both the copy-only evidence enumerator and the
`COMPLETE_SOLVER_ONLY` process-status checker now take the exact
same-model, same-state calculation roots. No recursive search across other
model variants, states or older saved cases is introduced. The saved batch
still has to match every expected runner exactly, including duplicate,
missing and unexpected-case checks. Results are never inferred from a JSON
calculation or a zero solver exit alone. Historical source files are not moved.

**Regression:** `tests/test_esm_legacy_canonical_split.py` constructs
synthetic legacy and canonical roots, plus a same-level unrelated model,
checks all current-case artifacts in the combined manifest, and requires an
exact script/status match. Run alongside
`tests/test_esm_organized_export_gui.py` and
`tests/test_canonical_esm_output_routing.py`. This is a filesystem/software
correctness fix only; no native ETABS/OpenSees gravity, stiffness, mass,
source-wall or code compliance acceptance is implied.

**Outstanding:** Auto-generated seismic review ZIPs in the separate
`bundle_seismic_review` workflow need a source-aligned run-directory
manifest and an explicit distinction between pre-solver force packages and
post-solver response packages. A historical success row with an unchanged
runner filename still requires an executed-runner SHA256 before its solver
status is treated as belonging to newly generated inputs.
