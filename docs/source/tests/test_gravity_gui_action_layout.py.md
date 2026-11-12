# Gravity GUI action organization and scroll contract

**What:** static Python tests verify that the gravity actions have one clear home, color-coded process status carries non-acceptance wording, and Run Log has explicit vertical/horizontal scrollbars and jump controls.

**When:** whenever action layout, process states, log rendering or analysis actions are edited.

**Why:** previously all buttons were stacked in three crowded rows and the native Text log had no explicit scrollbars. A green exporter completion must never be misread as ETABS source-model load-path acceptance.

**How:** `ast.parse` reads `components/gravity/gui_and_reports.py` without constructing Tk or invoking OpenSees. Tests check the named tabs, former command callbacks and widgets; they are **interface contract checks only**, not native UI visual acceptance. A Windows manual run must still check button placement, zoom/DPI, log scroll, action result and stop/cancel behavior.

**Where:** `tests/test_gravity_gui_action_layout.py`; [implementation source](../../../components/gravity/gui_and_reports.py), [engineering review](../../../REVIEW_MAIN/01_GRAVITY/20261112_GRAVITY_GUI_AND_LOAD_PATH_EVIDENCE_REVIEW.md).

**Which:** existing source code and no ETABS/EDB, data, solver, or real model.

**Who:** software maintainer tests CI and native Windows UI; qualified structural reviewer independently confirms what gravity outputs establish.

**Run:** `python -m unittest discover -s tests -p 'test_gravity_gui_action_layout.py' -v`.
