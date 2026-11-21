# Gate Material Blockers, Run-Log Analysis and Output-Folder Standard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the NLTHA readiness gate raise on an approved manifest whose nonlinear parameters were never reviewed, add a deterministic run-log analyser (with the findings of the user's V115 preliminary LTHA log), and add one uniform output-folder standard with an audit tool.

**Architecture:** (1) extend `components/model/readiness.py` constants so `gate_binding_blockers` also returns `parameters_not_reviewed` for approved manifests; (2) new stdlib-only `tools/analyze_run_log.py` parsing the runner's bracket-tag log lines into a JSON/Markdown finding under `docs/validation/run_findings/`; (3) new stdlib-only `tools/audit_output_layout.py` that checks a run directory against the existing `RUN_SUBFOLDERS` contract in `components/inputs/output_contract.py` (read-only), plus `docs/OUTPUT_FOLDER_STANDARD.md`.

**Tech Stack:** Python 3.12 stdlib, pytest. No OpenSeesPy, ETABS or tkinter needed.

**Spec:** user request 2026-11-21 ("do all systematically, with proper documentation, organize output folder uniformly"); repo rules `AGENTS.md`, `engineering/rules/CORE_RULES.md`; earlier slice plan `docs/superpowers/plans/2026-11-20-nltha-readiness-gate.md`; fixture `tests/fixtures/ltha_v115_prelim_log_excerpt.txt` (trimmed real log, PROGRESS/PERFORMANCE lines thinned to 6).

## Global Constraints

- Preserve scientific source; no change to any solver, material, damping or device numerics. Do not modify `Saved_Project_V156/`, any source EDB, or existing research methods.
- Never label solver PASS or a truncated diagnostic as engineering acceptance; new outputs carry the status text `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.
- Windows/Spyder compatible: `pathlib`, UTF-8 with `errors="replace"` when reading logs, LF-normalised comparisons, no POSIX-only calls.
- New public functions carry a `[REF ...]` docstring tag (`tests/verify_ref_tags.py` must not grow its baseline); each new module gets a `docs/source/<path>.md` guide, a `CANONICAL_MODULES.csv` row (`NEW_WITH_JUSTIFICATION`) and one deterministic test.
- `binding_not_recorded` stays advisory (legacy approved manifests must keep opening); recorded-hash mismatches and approved-contradiction codes keep raising as today.
- Output folder names are exactly `RUN_SUBFOLDERS = ("00_INPUT_SOURCE","01_LOGS","02_RESULTS","03_EXCEL","04_FIGURES","05_COMPARISONS","06_REVIEW","07_EXPORT_ZIP")`, schema `ETABS_OPENSEES_OUTPUT_CASE_V1`.
- Full suite (`python -m pytest -q`) must stay at 0 failures.

## Review Focus

- Approved manifest with `nonlinear_parameters_reviewed` False/missing: gate must raise `parameters_not_reviewed`; an unapproved manifest keeps raising its older approval error first (order unchanged).
- Approved manifest with `nonlinear_parameters_reviewed` True and no other blocker: gate must still pass (no new false positive).
- Log with zero completed cases, a truncated final case, a log cut mid-case, or Windows CRLF line endings: analyser must report counts, not crash.
- Log containing `TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE`: analyser must mark the run `diagnostic_only` and refuse a projected-acceptance wording.
- Run directory with missing, extra, symlinked or misnamed subfolders: audit lists each as an issue, never modifies or creates anything.

---

### Task 1: Gate raises on unreviewed parameters for approved manifests

**Files:**
- Modify: `components/model/readiness.py:221` (constant), `components/model/readiness.py:~414` (`gate_binding_blockers`), docstring of `gate_binding_blockers`
- Modify: `docs/NLTHA_READINESS_WORKFLOW.md` (sections 2/4/5: state which blocker codes the gate raises on, and that `binding_not_recorded` remains advisory)
- Test: `tests/test_nltha_gate_parameters_reviewed.py`

**Interfaces:**
- Consumes: `diagnose_nonlinear_readiness(config) -> {ready, blockers:[{code,message,fix}]}`, `gate_binding_blockers(diagnosis, data) -> list[dict]`, `_require_nonlinear_readiness(config)` (extracted from `runner_and_gui.py` via AST as the existing readiness tests do — copy their loader pattern from `tests/test_nltha_readiness_binding.py`).
- Produces: `APPROVED_CONTRADICTION_CODES` now `("material_file_missing","material_file_not_found","wall_fsam_tags_empty","parameters_not_reviewed")`; `_NON_GATE_BLOCKER_CODES` drops `parameters_not_reviewed` (it is now a gate blocker for approved manifests, still advisory for unapproved ones).

- [ ] **Step 1: Write failing tests** in `tests/test_nltha_gate_parameters_reviewed.py`: `test_gate_blockers_include_parameters_not_reviewed_when_approved` (diagnosis with that blocker + data `approved_for_nltha=True` → code in result), `test_gate_blockers_exclude_it_when_unapproved`, `test_gate_raises_for_approved_manifest_without_reviewed_parameters` (full `_require_nonlinear_readiness` with approved, all 16 checks True, bound model hash, `nonlinear_parameters_reviewed` False → `RuntimeError` mentioning `parameters_not_reviewed`), `test_gate_passes_when_parameters_reviewed` (same manifest with True and a material file + FSAM tags present → no raise), `test_binding_not_recorded_still_advisory`.
- [ ] **Step 2: Run** `python -m pytest tests/test_nltha_gate_parameters_reviewed.py -q`; expect the first, third and fifth-adjacent assertions to FAIL.
- [ ] **Step 3: Implement** the constant/`gate_binding_blockers`/`_NON_GATE_BLOCKER_CODES` changes above; update the docstring and the `[REF docs/NLTHA_READINESS_WORKFLOW.md ...]` text; update the workflow doc.
- [ ] **Step 4: Run** the new test file plus `tests/test_nltha_readiness_*.py tests/test_nltha_stale_runtime.py`; all pass.
- [ ] **Step 5: Commit** `git add -A components/model/readiness.py docs/NLTHA_READINESS_WORKFLOW.md tests/test_nltha_gate_parameters_reviewed.py && git commit -m "Gate raises on unreviewed nonlinear parameters for approved manifests"` (trailers per `.claude/skills/token-saving/SKILL.md` and the attribution reminder).

### Task 2: Run-log analyser and findings for the V115 preliminary LTHA run

**Files:**
- Create: `tools/analyze_run_log.py`, `docs/source/tools/analyze_run_log.py.md`, `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.md`, `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.json`
- Modify: `engineering/registry/CANONICAL_MODULES.csv` (one row)
- Test: `tests/test_analyze_run_log.py`

**Interfaces:**
- Produces: `parse_run_log(text: str) -> dict` with keys `workload` (`{cases:int, requested_steps:int}` or None), `scope` (str or None), `cases` (list, one per `[CASE TIMING]` in log order: `{name:str, elapsed_s:float, stages:dict[str,float], steps:int|None, dt_s:float|None, peak_drift_x:float|None, peak_drift_y:float|None, full_record_s:float|None, truncated_diagnostic:bool}`), `started_unfinished` (names with `[START]` but no `[CASE TIMING]`), `solver_baseline_cases` (count of `[SOLVER BASELINE]`), `solver_experimental_cases`, `eigen_max_residual` (float|None), `diagnostic_only` (bool, True if any `TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE`).
- Produces: `project_full_run(parsed: dict, *, dt_by_case: dict[str,float] | None = None) -> dict` returning `{measured_native_s_per_step, per_case:[{name, full_record_s, dt_s, steps, projected_hours}], total_projected_hours, basis}`; `measured_native_s_per_step` = sum of `native_transient_solve` over cases / sum of `steps` over cases; `steps` for the full record = `ceil(full_record_s/dt_s)`; `basis` must contain the words `linear baseline, no factor reuse, lower bound for nonlinear`.
- Produces: `render_markdown(parsed, projection, source_name) -> str` and CLI `python tools/analyze_run_log.py LOG --out-dir docs/validation/run_findings --stem NAME` writing `NAME.md` and `NAME.json` (deterministic: sorted keys, LF, no timestamps) and printing the two paths. Status line in both: `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.

- [ ] **Step 1: Write failing tests** in `tests/test_analyze_run_log.py` using the fixture: `test_parse_counts_twelve_completed_of_sixteen` (workload cases 16, 12 cases, one `started_unfinished` = `RSN1787_HECTOR_XY`), `test_diagnostic_only_flag`, `test_stage_timings_present` (each case has `native_transient_solve` > 0), `test_baseline_solver_count_twelve`, `test_eigen_residual_is_5_36e_7` (approx), `test_projection_is_days_not_hours` (`total_projected_hours` > 100 using the fixture's full-record durations and each case's `dt_s`), `test_projection_basis_wording`, `test_crlf_input_parses_same` (replace `\n` with `\r\n`, equal result), `test_empty_log` (zero cases, no exception), `test_cli_writes_deterministic_files` (run twice into tmp dirs, bytes identical, wording contains the status line and never the word `ACCEPTED`).
- [ ] **Step 2: Run** `python -m pytest tests/test_analyze_run_log.py -q`; expect import failure.
- [ ] **Step 3: Implement** the three functions and CLI with regexes over the bracket tags; stdlib only; full-record seconds come from `full_record=<float>s` in the `[LINEAR TRIAL]` line of the same case; drifts and `steps`/`dt` from the `[OK]` line; JSON stage dict from the `stages={...}` payload of `[CASE TIMING]`.
- [ ] **Step 4: Generate** the findings: `python tools/analyze_run_log.py tests/fixtures/ltha_v115_prelim_log_excerpt.txt --out-dir docs/validation/run_findings --stem LTHA_V115_PRELIM_20261120`. In the generated `.md` add (by the renderer, not by hand) sections: what ran, timing table, projection, and "Not evidence of": engineering acceptance, drift performance (peak drifts are from 0.5 s of record), nonlinear cost. Also add by hand to `docs/source/tools/analyze_run_log.py.md` the recommendations: decouple model rebuild per case (~85-110 s each), consider factor reuse only after `elastic_constant_tangent_verified` and constant dt (existing `-factorOnce` path), and that nonlinear runs cannot reuse the factorisation.
- [ ] **Step 5: Run** the test file and `python tests/verify_ref_tags.py`; pass.
- [ ] **Step 6: Commit** the tool, tests, fixture, docs, registry row.

### Task 3: Uniform output-folder standard and read-only audit

**Files:**
- Create: `tools/audit_output_layout.py`, `docs/OUTPUT_FOLDER_STANDARD.md`, `docs/source/tools/audit_output_layout.py.md`
- Modify: `engineering/registry/CANONICAL_MODULES.csv` (one row), `docs/00_REPOSITORY_ORGANIZATION.md` (link), `README.md` (one-line pointer)
- Test: `tests/test_audit_output_layout.py`

**Interfaces:**
- Consumes: `components.inputs.output_contract.RUN_SUBFOLDERS`, `SCHEMA`, `inspect_case_manifest(run_dir, expected_stage=None)` (read-only; returns a dict containing issues — inspect its return shape in the file before use and pass its issues through unchanged).
- Produces: `audit_run_layout(run_dir) -> dict` `{run_dir:str, ok:bool, missing:list[str], unexpected:list[str], symlinks:list[str], manifest_issues:list, status:"LAYOUT_ONLY_NOT_ENGINEERING_ACCEPTANCE"}`. Never creates, moves or deletes anything. `unexpected` = entries in the run dir that are not `RUN_SUBFOLDERS` (files allowed: none besides `00_INPUT_SOURCE/CASE_MANIFEST.json`'s folder content); CLI `python tools/audit_output_layout.py RUN_DIR [--json]` exit code 0 if `ok` else 1.
- Standard document content: run tree `<export>/<stage folder>/RUNS/<state>/<case>/<UTC stamp>_<hash>/` with the eight subfolders and what goes in each (inputs/config/scripts → 00; logs → 01; JSON/CSV results → 02; workbooks → 03; figures → 04; comparisons → 05; review/acceptance notes → 06; zip → 07), the status vocabulary from `output_contract.STATUSES`, the repo-side location for findings (`docs/validation/run_findings/<STAGE>_<RUNID>.md|json`), agent edit evidence in `engineering/agent_edits/`, and a table of which producing modules already use the contract versus write ad hoc folders (list `components/nonlinear_time_history/building_exploratory.py`, `literature_demo.py`, `full_record_gate.py`, `energy_balance.py` as ad hoc; do not change them).

- [ ] **Step 1: Write failing tests** in `tests/test_audit_output_layout.py`: `test_conforming_run_ok` (tmp dir with the eight folders and a valid manifest created via `create_case_run` if usable offline, otherwise folders only with `manifest_issues` allowed to be non-empty and `missing`/`unexpected` empty), `test_missing_subfolder_reported`, `test_unexpected_entry_reported`, `test_symlink_reported` (skip if the platform cannot symlink), `test_audit_is_read_only` (directory listing identical before/after), `test_cli_exit_codes`.
- [ ] **Step 2: Run** the file; expect import failure.
- [ ] **Step 3: Implement** `audit_run_layout` and CLI, stdlib plus the `output_contract` import.
- [ ] **Step 4: Write** the standard doc and guide; add README / organization links.
- [ ] **Step 5: Run** the file, `python tests/verify_ref_tags.py`, and `python -m pytest tests/test_literature_code_map.py -q` (docs links map).
- [ ] **Step 6: Commit.**

### Task 4: Evidence notes, CI paths, full run, whole-branch review

**Files:**
- Create: `engineering/agent_edits/20261121_gate_parameters_and_run_analysis.md`
- Modify: `.github/workflows/tests.yml` (path filters include `tools/**`, `docs/validation/run_findings/**`), `docs/validation/DAMPED_OUTRIGGER_NLTHA_GAP_REGISTER.md` (add the run-log findings row: LTHA V115 is a preliminary linear 0.5 s diagnostic; no nonlinear device evidence)
- Test: none new

**Interfaces:** Consumes everything above; Produces the PR description inputs.

- [ ] **Step 1:** Write the agent_edits note (changed / verified / unverified / commit, model label `UNKNOWN`).
- [ ] **Step 2:** Run `python -m pytest -q`; expect 0 failures.
- [ ] **Step 3:** Whole-branch review by a fresh reviewer; one fix wave; re-run the suite.
- [ ] **Step 4:** Push `feat/gate-material-blockers-run-analysis`, open the PR via `gh api`.
