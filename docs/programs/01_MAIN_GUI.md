# 01 — Main GUI

Open `01_WORKFLOW_START.py` in Spyder or run `python 01.py` from the repository. `01_MAIN_GUI.py` remains available for existing shortcuts.

The numbered entries delegate to `01.py`, then `RUN_ETABS_TO_OPENSEES.py`, the V116 facade, and `components/ui/application.py`. The launcher uses the same Python interpreter in a fresh process. Importing a numbered entry leaves the workbench closed.

The latest startup log is recorded in the local `Startup_Logs/LATEST.txt` pointer. A process-start failure or a Tk callback exception records its original traceback in the log. Opening the workbench is separate from running ETABS import or verifying a structural model.

**Inputs:** Existing ETABS EDB, source workbook registration and output folder; no inputs are baked into this launcher. Do not mix old exported runtime modules with current repository code.

Import targets the original export root. Project-dependent tools use the selected export, including when the workbench also contains a previously opened case.

Run `python -m pytest -q tests/test_main_launcher_short_alias.py` to check aliases and startup failure handling. On Windows, set `OPENSEES_STARTUP_SMOKE=1` before running `01.py` to open the Tk window briefly and verify the startup chain.
