# Cross-module ETABS→OpenSees handoff integrity — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Apply systematic-debugging and red/green TDD before code. This is a bounded integration correction, not a native structural validation.

**Goal:** Prevent a previous ESM runner execution from being accepted after the same named script changes, while documenting source/solver/output acceptance for all active analysis stages.

**Architecture:** Preserve existing shared stage layouts and 32/76/97 support contract. Extend the current ESM batch status writer and its existing copy-only combined-export reader with SHA256 matching for the exact executed source script. Extend the *existing* cross-module audit documentation using actual active source and CI inventory; do not create a duplicate scanner, change structural physics or relocate any native model files.

**Tech stack:** Python 3.12, GitHub Actions, unittest and pytest, existing tkinter/OpenSees runtime.

**Spec:** `docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md` and `REVIEW_MAIN/02_MODEL/20261122_NATIVE_ETABS_OPENSEES_CONVERSION_AUDIT.md`.

## Global constraints
- 32 actual foundation supports; 44 extra shear-wall mesh points are not independent physical foundations.
- Gravity benchmark is full 1.0D+1.0L; seismic weights are separate NBC 105:2025 Table 5-1 categorized values.
- Do not alter source-native 2×12m X walls/3×6m Y walls, ULS/SLS source state, stiffness, loads, masses, seismic force formulas, records or output data.
- Source EDB and workbook SHA, private Windows result archives and native ETABS/OpenSees solver verification are unavailable. No engineering acceptance claim.
- Do not rewrite/delete historical logs, Excel, EDB, paths or result CSVs; keep all changes branch-isolated until CI and review.
- Maintain source comments/guides and committed author/editor evidence. Do not publish private model data.

## Review focus
- Same runner filename but different script bytes after a recalculation.
- Legacy CASE_STATUS without a runner SHA (must not count as freshly verified).
- Matching runner SHA but recorded runner_path outside exact selected roots (reject).
- Both canonical 03_ESM and legacy OpenSees_Analysis_Results roots, with different scripts of the same name.
- Missing/cancelled/partial solver cases; no completed batch from force export alone.

---

### Task 1: Reproduce stale ESM success in regression tests

**Files:**
- Modify: `tests/test_esm_organized_export_gui.py`
- Modify: `tests/test_esm_legacy_canonical_split.py`

**Interface:** `_latest_batch_status(root, calculation_roots=()) -> dict`; CASE_STATUS per-row `runner_sha256`, `runner_path`.

- [ ] Write tests: same name changed SHA must yield `PARTIAL_OR_FAILED`; old success with no `runner_sha256` must be reported `PARTIAL_OR_FAILED` plus `runner_identity_issues`.
- [ ] Run `pytest -q tests/test_esm_organized_export_gui.py tests/test_esm_legacy_canonical_split.py` on the **unmodified production source** and record the expected failing assertions.
- [ ] Build tests for canonical/legacy identical-name collision and success with matching path+sha.
- [ ] Confirm earlier incomplete/duplicate/unexpected tests stay valid.

### Task 2: Bind ESM execution status to immutable runner bytes

**Files:**
- Modify: `components/equivalent_static/calculation_and_gui.py`
- Modify: `components/equivalent_static/organized_exports.py`
- Modify: `docs/source/components/equivalent_static/organized_exports.py.md`
- Modify: `docs/source/components/equivalent_static/calculation_and_gui.py.md`

**Interface:** a successful saved case must record the executed runner path + valid SHA256; the exporter computes current SHA on exact-case rooted runner and rejects missing/conflicting evidence.

- [ ] Add `runner_sha256` calculated immediately before Popen and verify file still has that digest after subprocess completes; if it changes, status becomes `INCOMPLETE`.
- [ ] Saved CASE_STATUS rows include `runner_sha256`, and failed/no-run entries do not fabricate one.
- [ ] Reader checks both canonical and legacy exact-case runner directories and requires recorded path to match a discovered runner with matching file digest. Do not assume that equal basenames imply equal content.
- [ ] Run focused tests plus full GitHub headless pytest and audit workflows; record actual run SHA and numerical/engineering caveat.

### Task 3: Document the whole-pipeline module acceptance and efficiency matrix

**Files:**
- Create: `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_ETABS_OPENSEES_HANDOFF_AUDIT.md`
- Create: `engineering/agent_edits/20261123_CROSS_MODULE_HANDOFF_REVIEW.md`

- [ ] Inspect active source owners for inputs, model, sections, gravity, modal/Rayleigh, ESM, MRSM, LTHA, NLTHA, NBC, validation, UI and shared/exporters.
- [ ] Record explicit input/output contracts, discrepancies, scope of code inspected, source-file references, verification gates, efficiency recommendations and priorities.
- [ ] Use latest GitHub CI AST counts and dedup findings as software review candidates, not entire-repo semantic completion.
- [ ] Keep status as `SOURCE_REVIEWED_PARTIAL` and `NATIVE_NOT_VERIFIED` without actual EDB and run archives.

### Task 4: Review and merge

- [ ] Inspect branch diff and CI reports for false positives, missing source readers and test regressions.
- [ ] Open an isolated PR, require all applicable GitHub checks to pass.
- [ ] Merge to `main` only after source-level verification, without declaring 32-support physical equivalence or NBC code acceptance.
- [ ] Report Changed / Tests actually executed / Native acceptance state / Outstanding blocker / Commit SHA.
