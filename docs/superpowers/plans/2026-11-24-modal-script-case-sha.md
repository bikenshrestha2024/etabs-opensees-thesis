# Manifested Modal script SHA identity — 2026-11-24

**Source preflight:** main `540677187e287f371ad10adbc4e5aac94a2786aa`; read `AGENTS.md`, physical-model contract, agent SKILL, CORE_RULES, ENGINEERING_GATES, MODULE_BOUNDARIES, canonical stage naming and source guides.

**Verified defect:** `prepare_canonical_modal_run` records the source script SHA in a separate MODAL_INPUT_PROVENANCE but invokes `create_case_run` with neither model SHA nor source EDB SHA. Long Modal case labels are therefore not compacted and the shared CASE_MANIFEST cannot check script-digest identity. `prepare_history_run` also hashes a source script but leaves CASE_MANIFEST script SHA blank. Full original ETABS EDB SHA/workbook identity and native solver execution are **UNAVAILABLE** here.

**Physics invariants:** 32 physical supports + 44 mesh transfer joints unchanged; 1.0D+1.0L gravity distinct from NBC §5.2 Table 5-1 seismic mass; two 12m X walls unchanged. Source script SHA is **not** assembled model or source EDB SHA and cannot establish numerical equivalence.

## Test-first tasks
- [ ] Add deterministic `tests/test_modal_script_case_provenance_20261124.py` covering long case compaction, two distinct script contents, state independence, source SHA manifest, tamper-invalid case, historical manifest fallback and unchanged source scripts.
- [ ] Confirm focused test fails on main under CI (TDD RED).
- [ ] Extend existing `components/inputs/output_contract.py` `create_case_run` with optional `source_script_sha256`; validate SHA, compact only new source-hashed long case names, add explicit `SOURCE_SCRIPT_SHA256` basis and manifest checks while leaving model/EDB basis precedence and older manifests intact.
- [ ] Update `components/modal/gui_and_reports.py` to calculate script digest once and pass as `source_script_sha256`; do not substitute for assembled-model hash. Update `prepare_history_run` to record identical script digest in shared manifest without changing prior case IDs.
- [ ] Update existing module source docs and engineering edit ledger; run focused and full CI. Merge via PR if all software checks pass. Keep native engineering gates NOT_VERIFIED.

**Non-goals:** ESM old direct-case naming, native ETABS/solver changes, output file moves, restoring historical report copies, complete repository semantic certification.
