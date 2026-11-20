# NLTHA readiness-gate slice — implementation plan

**Spec/authority:** AGENTS.md, engineering/rules/CORE_RULES.md, docs/00_RESEARCH_REFERENCES.md (R01–R13), docs/00_THESIS_ACCEPTANCE_GATES.md. No separate spec file; rulings are provisional.

**Goal:** A user who hits the "Input needs review … uncompleted readiness TEMPLATE" dialog can reach an *unapproved, model-bound* draft with a precise list of what is still missing, and the ETABS ingestion path stops failing silently. The gate itself is never weakened.

## Global Constraints (copy verbatim to implementers and reviewers)
- Never set `approved_for_nltha` or any `checks[*]` to True in code. Generated drafts are UNAPPROVED; every check False.
- Literature defaults only via the existing `components/nonlinear_time_history/material_draft.py` / `material_source_sets.py` path; label `RESEARCH DRAFT; NOT PROJECT CALIBRATED OR APPROVED`; cite R-IDs from docs/00_RESEARCH_REFERENCES.md; do not invent reinforcement, damper or material numbers.
- Do not create `*_latest.py`, `*_fixed.py` or version-numbered source files. Extend existing modules (`components/model/readiness.py`, `components/nonlinear_time_history/runner_and_gui.py`, `components/ui/application.py`, `components/model/assembly.py`).
- Python 3.12, Windows/Spyder compatible; no top-level `tkinter` import in any new/changed non-GUI module; units kN-m-s.
- Never modify a source EDB. Keep existing exception types/messages of `_require_nonlinear_readiness` as a superset (existing tests must pass).
- Each task: failing deterministic test first (tests/test_*.py, runs headless with `PYTHONPATH=$PWD python -m pytest`), then code. Report only tests actually run; native ETABS/Windows checks are PENDING.

## Task 1: Structured readiness diagnosis (non-GUI)
Add `diagnose_nonlinear_readiness(config) -> dict` to `components/model/readiness.py` returning `{ready: bool, blockers: [{code, message, fix}]}` covering: manifest missing, template/unbound `model_script`, bound-to-other-model, SHA mismatch, `approved_for_nltha` not True, each of the 16 check keys not True, `nonlinear_materials_file` missing/not found, `nonlinear_wall_fsam_tags` empty, `nonlinear_parameters_reviewed` not True. Make `_require_nonlinear_readiness` raise one RuntimeError whose text is the existing message plus the blocker list (still raises in every case it raised before). Tests: template, bound-unapproved, missing material file, all-clear (ready only when everything True in a fixture).

## Task 2: Model-bound unapproved draft writer (non-GUI)
Add `bind_readiness_draft(template_path, model_script, out_path=None) -> Path` to `components/model/readiness.py`: copies template, sets absolute `model_script`, `model_script_sha256`, all `checks` False, `approved_for_nltha` False, `status` "UNAPPROVED DRAFT", never overwrites an existing approved file. Wire the existing readiness GUI button (`components/model/readiness_gui.py`) to call it without adding module-level tkinter imports elsewhere. Tests: hash correctness, idempotence, refuses to clobber an approved file, result still fails the gate with "not approved".

## Task 3: ETABS ingestion hardening (fake-COM tests)
In `components/ui/application.py` (~lines 150–215): (a) open a temporary working copy of the EDB, not the original; (b) after `SetPresentUnits(6)` read back `GetPresentUnits` and raise if not 6 (no swallowed exception); (c) in `_point_coords` and the similar loop, collect names of points whose COM call fails, log them, and raise when any are dropped. Put the pure logic (copy helper, units check, dropped-point accounting) in a GUI-free module `components/etabs_ingest_guards.py`... EXTEND an existing non-GUI module instead if one fits (check `components/model/` and `src/etabs_adapter/`). Tests with fake `sap` objects. In `components/model/assembly.py` (~120–145) record unparseable material rows and nonzero API returns in `assembly_errors` instead of silently skipping.

## Task 4: Documentation and evidence
Add `docs/NLTHA_READINESS_WORKFLOW.md` (step-by-step: template → bound draft → research material draft → evidence → approval by human; what is PENDING), update README/AGENTS pointers minimally, add `engineering/agent_edits/20261120_nltha_readiness_gate.md` (model label per CORE_RULES; base SHA; changed paths; tests run; PENDING native checks), and a row in `engineering/registry/CANONICAL_MODULES.csv` only if a new module was created.
