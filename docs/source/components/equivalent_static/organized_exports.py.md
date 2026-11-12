# ESM combined inspection and non-destructive folder organizer

**What:** Copy-only exporter builds categorized ESM review trees in ESM_Organized/<UTC timestamp>. Separately names ETABS_Linked_Equivalent_Static and OpenSees_Direct_Equivalent_Static; each then has limit state, case and extension categories JSON, Excel, CSV, Plots, Scripts, Logs and PDF. Creates ESM_Combined_Inspection.xlsx, ESM_Export_Manifest.json, ZIP and LATEST_ESM_COMBINED_EXPORT.txt.

**Why:** The original six X/Y ESM scripts and per-case JSON, CSV, XLSX and PNG are scattered among unrelated gravity and seismic results. Earlier export controls were difficult to find and lacked one combined inspection workbook.

**When:** Export after computing ESM cases; this does NOT launch ETABS or OpenSees.

**Where:** components/equivalent_static/organized_exports.py and calculation_and_gui.py. Legacy producer and script paths remain unchanged.

**Who:** Research software maintainer validates Windows/UI and source fingerprint; qualified engineer independently validates structural response and code compliance.

**How:** Run python -m unittest discover -s tests -p test_esm_organized_export_gui.py -v. Every copied file has a SHA256/source-path record; no original results are moved, overwritten, renamed or deleted. Invalid JSON is marked INVALID SOURCE; absent calculations block the combined output.

**Source and acceptance status:** The user's ~95m high-rise ULS equivalent-static results remain COMPARISON ONLY under NBC 105:2025 §3.2.1. Vs30 evidence remains missing. Previous 6m-bay historical ETABS Aw-X=1.9582936 m² versus 12m grouped OpenSees Aw-X=2.0731745 m² is unresolved, not automatically reconciled. A linked Excel copy is not a solved native ETABS response.

**Engineering limitations:** A generated applied lateral Fi profile is not recovered story shear, drift or stiffness. Source EDB and model SHA identity plus actual ETABS cases/stories and dynamic basis are required before native ETABS comparison. For a true governing dynamic analysis use MRSM/NLTHA per applicable code and validated model.
