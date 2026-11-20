# tests/test_no_toplevel_tkinter_in_core.py — source guide

**What/when:** static AST guard run in the headless pytest suite; it fails when a core, non-GUI module gains a module-level tkinter import.

**Why/how:** `conftest.py` converts a missing-module `tkinter` failure into a skip, so a new top-level `import tkinter` would silently skip the headless tests of that module. This test parses the source only (no imports, so no ModuleNotFoundError and no skip). Function-local imports are allowed. It also checks that the conftest skip is limited to missing `tkinter`, `plotly` and ETABS COM modules.

**Where:** `tests/test_no_toplevel_tkinter_in_core.py`; modules checked: `components/model/readiness.py`, `components/validation/gravity_etabs_direct.py`, `components/model/assembly.py`, `components/model/nonlinear_preflight.py`, `tools/audit_literature_code_map.py`.

**Which:** source text only; no model, ETABS or GUI is started.

**Who:** maintainer owns regression; add a module to `CORE_MODULES` when it becomes a non-GUI core module.

**Run:** `python -m pytest -q -p no:cacheprovider tests/test_no_toplevel_tkinter_in_core.py`.

**Status:** structural guard only; not engineering validation.
