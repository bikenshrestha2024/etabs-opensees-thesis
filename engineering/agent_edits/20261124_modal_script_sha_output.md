# 2026-11-24 — Modal and time-history script fingerprint integration

**Editor/tool:** ChatGPT via the connected GitHub plugin; exact model revision unknown. **Base Git commit:** `540677187e287f371ad10adbc4e5aac94a2786aa` on `main`. **PR:** #191. **Scope:** EXTEND existing `components/inputs/output_contract.py` and `components/modal/gui_and_reports.py` without copying code into new version-numbered source files.

## Mandatory source preflight

Actually read: `AGENTS.md`; `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`; `.agents/skills/etabs-opensees-read-first/SKILL.md`; CORE_RULES, ENGINEERING_GATES and MODULE_BOUNDARIES; `docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md`; current output source guides, relevant existing run contract, Modal GUI and tests. Original EDB SHA, V10.7 workbook SHA, selected physical M0–M6 source model, native Windows OpenSees runtime: **UNAVAILABLE**.

**Preserved:** 32 physical foundation supports + 44 shear-wall mesh transfer joints; 1.0D+1.0L unfactored gravity comparison, separately NBC 105:2025 §5.2 Table 5-1 seismic weight; two 12 m X walls with openings and three 6 m solid Y walls. No support constraints, solver physics, stiffness, gravity, mass, load combinations, spectra, record components, material laws, device forces or EDB/XLSX files changed.

## Root-cause analysis and software change

The shared new-run contract compacted long case labels only if an `assembled model SHA` or `source EDB SHA` was provided. Modal `prepare_canonical_modal_run` already hashed the actual source model-builder script into `MODAL_INPUT_PROVENANCE.json`, but invoked the shared run creator without either digest. Result: **long 04_MODAL case labels persisted** and same human name mapped differently changed scripts to one case parent. LTHA/NLTHA also generated a compact script-bound label and separate HISTORY_INPUT_PROVENANCE, but did not record that script digest in the shared case manifest.

Added `source_script_sha256` as an independent source-basis field, **not an alias to `model_sha256` or `source_edb_sha256`**. New manifested case precedence for long labels: assembled-model digest, then source EDB, then source script. A source code hash is not complete model equivalence. The code detects tampered compact label/basis/hash, retains old manifests without the optional field, preserves short and historical names, and never moves prior files.

Modal computes script hash once and passes it to `create_case_run`. The LTHA/NLTHA `prepare_history_run` already computes the digest; it now adds it to the case manifest. No run-state sharing or OpenSees checkpoint reuse is introduced.

## TDD, tests, and native verification

Pre-code test commit `1c31ce12` on PR branch produced **9 expected failing tests, 1,884 passed, 5 skipped** in GitHub Actions; failures prove missing `source_script_sha256` and long names that did not change with modified scripts. Production changes followed RED. Further full GitHub CI is required before merge; do not treat earlier passing subtests as proof of the final head.

Native ETABS/OpenSees acceptance remains:
- `SOURCE_CHECKED`: **NOT_VERIFIED_FOR_ACTUAL_EDB**
- `NUMERICALLY_CONVERGED`: **NOT_VERIFIED_FOR_ACTIVE_CASE**
- `ETABS_OPENSEES_MATCHED`: **NOT_VERIFIED**
- `EXPERIMENT_VALIDATED`: **NOT_VERIFIED**
- `CODE_ACCEPTED`: **NOT_VERIFIED**

This PR does **not** fix the still-long direct `03_ESM/RUNS` cases created via `analysis_output_folder` and `write_outputs`; that requires verified writer, reader, Rayleigh, status, ZIP and GUI migration. It also does not resolve ESM repeated model/gravity/P-Delta construction (Issue #186), 32 physical-support native reaction residuals (Issue #140), site Vs30 or full nonlinear analysis.
