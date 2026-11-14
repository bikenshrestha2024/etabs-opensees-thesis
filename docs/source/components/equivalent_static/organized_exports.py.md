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
