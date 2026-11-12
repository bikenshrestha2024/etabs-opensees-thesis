# 2026-11-12 gravity GUI and load-path forensic audit

**Editor:** ChatGPT / GPT-6 via authenticated GitHub integration.  
**Base:** `298df056e9e2510ade14d13a9e59eb6911f57114` (main immediately before edits).  
**Source data:** privately uploaded Gravity/Comparisons/All Modules evidence ZIPs 2026-11-12; only engineering findings written to public review; raw private data not uploaded.

## What and why

- Reorganize crowded gravity actions into purpose-specific tabs while preserving all existing user-visible callback functions and output locations.
- Color label `RUNNING` blue, `FINISHED` green, `BLOCKED` red, `IDLE` neutral with literal state text. Process completion does not establish code/model acceptance.
- Add explicit vertical and horizontal scrolling, copy full log, scroll-to-start/latest, retain original time-stamped saved log.
- Cross-verify current 32/76/97 support-case evidence and independent software manuals. Current global gravity load matches source but reaction mapping and shell-to-frame load transfer are NOT independently matched.

## When, where, how, which

- Timestamp: November 12, 2026.
- Source changed: `components/gravity/gui_and_reports.py` only for UI hierarchy, action grouping/status visual cues and Run Log scrolling.
- Review record: `REVIEW_MAIN/01_GRAVITY/20261112_GRAVITY_GUI_AND_LOAD_PATH_EVIDENCE_REVIEW.md`; links in numbered review gateway.
- Regression: `tests/test_gravity_gui_action_layout.py` and source guide; CI workflow hook. No native solver re-run.
- Quantities preserved: full-gravity 311367.31387955 kN and distinct 32/76/97 boundary conditions; no gravity/mass/time-step/material physics altered.

## Who and limitations

- Tool/editor: ChatGPT / GPT-6. Software reviewer must still verify actual Windows/Tk responsiveness, labels, keyboard/focus and each callback.
- Civil/earthquake engineer must reconcile original ETABS 76-source supports, shell auto mesh, analysis end zones and independent per-joint six-DOF reactions. **Do not promote 32-support diagnostic to native ETABS equivalence.**
- No source EDB, structural model, original Excel, private PDF, earthquake or real result-file binaries changed.
