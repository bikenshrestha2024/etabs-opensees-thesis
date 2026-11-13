# 01 — Main GUI

**Launch:** `01_MAIN_GUI.py` from Spyder, or run `python 01_MAIN_GUI.py` from the repository root.

This is the short, descriptive **user entry point** for the full ETABS → OpenSeesPy research launcher. It delegates to `01.py` → `RUN_ETABS_TO_OPENSEES.py` → the original V116 compatibility module → `components/ui/application.py`. The existing fresh-child process, Python interpreter, startup log, error dialog and import behavior remain unchanged.

**Naming policy:** The stage number `01` means main GUI entry; it does not rename the 01–21 canonical engineering steps, and users should not infer that running the GUI completes model input validation. Retain `01.py`, `01_WORKFLOW_START.py` and `ETABS_to_OpenSeesPy_Section_Review_V116_NBC105_Area_NLTHA.py` for old launchers/imports and reproducible historical outputs. The shorter alias is the recommended filename in user-facing instructions.

**Inputs:** Existing ETABS EDB, source workbook registration and output folder; no inputs are baked into this launcher. Do not mix old exported runtime modules with current repository code.

**Verification:** `python -m unittest discover -s tests -p 'test_main_launcher_short_alias.py' -v`. This is static chain verification; actual Spyder/Windows ETABS startup and analysis execution still require a native check. No engineering acceptance is implied.
