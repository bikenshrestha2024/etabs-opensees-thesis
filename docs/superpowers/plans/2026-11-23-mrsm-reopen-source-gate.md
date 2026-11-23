# MRSM saved-batch identity and cross-module status handoff

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Write failing tests before any implementation; verify the original symptom and the full suite.

**Goal:** Prevent the MRSM GUI from displaying stale, legacy or different-model `COMPLETED` rows as completed current-model numerical cases on reopening, while retaining an interoperable opt-in source-provenance field in the shared CaseLedger for future LTHA/NLTHA use.

**Architecture:** Extend `components/shared/case_status.py` with backwards-compatible optional batch provenance, keeping existing LTHA/NLTHA behavior unchanged. MRSM owns one read-only saved-run status helper using existing `inspect_case_manifest` and `validate_mrsm_case_output`, and stores the source file SHA, selected analysis state, input-config digest, and run directory with each new saved ledger. Do not add a duplicate run parser, do not change seismic physics or delete old ledgers.

**Stack:** Python 3.12, unittest/pytest, project case/manifest contract and GitHub Actions.

**Spec:** `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `engineering/rules/ENGINEERING_GATES.md`, `docs/source/components/response_spectrum/model_analysis.py.md` and `docs/source/components/shared/case_status.py.md`.

## Global constraints
- 32 real foundations, 44 additional wall-mesh points, 76/97 are diagnostic profiles.
- Full gravity 1D+1L is separate from NBC 105:2025 Table 5-1 seismic weight.
- Native two X 12m walls and three Y 6m walls unchanged.
- ULS and SLS cannot be interchanged; support, mass and gravity policy are part of run input identity.
- Native EDB/workbook SHA and native ETABS/OpenSees Windows response unavailable. This is saved-evidence and UI integrity only, not project structural equivalence.
- No private EDB, Excel, JSON project models or Windows paths in GitHub tests; synthetic temp directories only.

## Task 1: Reproduce stale and missing MRSM identity

**Files:** `tests/test_mrsm_reopen_source_gate.py` (new), `components/shared/case_status.py` and `components/response_spectrum/model_analysis.py` (existing).

- [ ] Write RED tests: legacy ledger with six `COMPLETED` rows but no source identity shows `LEGACY_UNVERIFIED` and zero validated cases; mismatched selected model/state/config hash shows `SOURCE_OR_INPUT_MISMATCH`; missing saved numeric result or `CASE_MANIFEST` cannot be promoted to completed.
- [ ] Write a synthetic six-case valid saved result using existing `validate_mrsm_case_output`: matching state, model, input digest, canonical run manifest, and per-case saved results reports six *numerically checked saved cases only*.
- [ ] Run failing tests in GitHub Actions on an isolated PR branch; record actual RED assertion failures, not speculative behavior.

## Task 2: Add safe shared provenance + MRSM readback

**Files:** `components/shared/case_status.py`, `components/response_spectrum/model_analysis.py`, source guides.

- [ ] Preserve original `CaseLedger(path, ids)` with optional `provenance={...}`, and add `set_provenance(**values)` to atomically persist the executed run location.
- [ ] Add `mrsm_input_signature(fields)` and `review_saved_mrsm_batch(output_root, source_folder, selected_fields)` that reopens exact same-state six-case outputs, checks source SHA, selected source configuration, canonical case manifest, and full saved numeric `validate_mrsm_case_output` gate. No hidden fallback to neighboring runs.
- [ ] MRSM GUI uses the new helper on reopen; notes legacy/unverified statuses rather than `SAVED RUN` current-numeric claims. Its new ledger records source/config at run selection and a verified unique run root after creation.
- [ ] On child completion verify source model JSON unchanged before declaring saved case completeness, and preserve snapshot of the ledger beside its corresponding run review folder.
- [ ] Run focused plus full project CI; record elapsed performance and remaining native gates.

## Task 3: All-module workflow follow-up

**Files:** `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_HANDOFF_FOLLOWUP.md`, `engineering/agent_edits/20261123_MRSM_REOPEN_PROVENANCE.md`.

- [ ] Describe upstream ETABS model/sources, downstream gravity/modal/ESM/MRSM/LTHA/NLTHA metadata and acceptance separately, classify 84 legacy path references and 32 source exact-body duplicate groups as existing review work (not validated semantics).
- [ ] Recommend a shared full-run provenance extension for LTHA/NLTHA and verified timing/speed benchmarks, without guessing a native speedup.
- [ ] Require nine CI workflows and complete headless suite to pass. Leave physical 32-support reaction mismatch, first-step nonlinear wall convergence and complete 224 history runs open.

## Completion

- [ ] Report exact CI test counts, PR URL, merge decision and SHA; never call native numerical acceptance passed from synthetic fixtures.
