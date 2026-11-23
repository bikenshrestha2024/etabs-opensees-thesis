# 2026-11-23 initial signed P-Delta provenance and support-selection correction

**Editor:** ChatGPT via GitHub connector (current conversation). **Base main SHA:** `caaf0aef9f5400f0bd6fd87c2c396bc7b5e2518c`. **PR:** #187. **Issue:** #186 (performance follow-up). **Native ETABS/OpenSees:** UNAVAILABLE in this session; no claim of numerical approval.

## Checked source contracts and scoped changes

Read root `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `engineering/rules/ENGINEERING_GATES.md`, active `components/model/initial_pdelta.py` and source guide; inspected `components/model/support_case_contract.py`, `components/model/assembly.py` and ESM callers.

- Primary physical foundations **32**. Source-mapped 76 IDs contain **44 wall mesh-transfer points**, not independent physical supports; 76/97 remain explicitly diagnostic.
- Full gravity **1.0D+1.0L** is distinct from NBC 105:2025 §5.2 Table 5-1 seismic weight. This patch does not alter either load ledger.
- Physical X walls **2×12 m with openings**, Y walls **3×6 m**, per user-adopted source basis. No geometry or sections changed.
- Original source EDB SHA: **UNAVAILABLE**; current source-matched NBC workbook SHA: **UNAVAILABLE**; live ETABS OAPI: **UNAVAILABLE**. The supplied staged MESH_04 source ZIP is not a substitute for the original native source reaction/MPC comparison.

## Confirmed software inconsistency

`ensure_initial_checks` passed raw `data['supports']` tags to gravity and to signed horizontal reaction recovery even after `build_complete_model` selected a different runtime case. Cached signed responses were keyed on input files and three implementation source files, but not on selected support/mass policy, and concatenated file bytes lacked an unambiguous boundary.

## Changes and limits

- Runtime assembled `gravity_base_support_tags` now provide the reaction support inventory via the existing shared helper, not the raw export dictionary.
- Cache key is versioned and separately fingerprints each named dependency, support case, mass policy and initial-case stiffness state. Legacy cache rows no longer satisfy the new version; all four fresh signed cases must be solved before atomic publication.
- Record per-case model build, gravity and lateral timing, selected tag count and hash; default ULS initial reference is independent of later SLS analyses.
- Existing OpenSees model builder, stiffness, mass, load applications, solver tolerances, foundations and source geometry are untouched. This correction cannot certify the missing 44 mesh-point MPC transfer.
- **No shared preloaded solver reuse or parallel case writes** introduced. Cold initial checks may remain expensive; native benchmark required under #186.

## Verification and next gate

Synthetic regression `tests/test_initial_pdelta_profile_cache_20261123.py` was first committed against unmodified code and observed **three expected RED failures** in GitHub Actions (missing new fingerprint helper and old source restraint accounting). After implementation, require green headless CI and module navigation. Then rerun locally using regenerated `OpenSees_Runtime_V118`, actual ULS/SLS source and physical32 support case to compare 6-DOF reactions and source-matched ETABS cuts.

Engineering acceptance flags remain independent: `SOURCE_CHECKED=NOT_VERIFIED`, `NUMERICALLY_CONVERGED=NOT_VERIFIED_FOR_NEW_RUN`, `ETABS_OPENSEES_MATCHED=NOT_VERIFIED`, `EXPERIMENT_VALIDATED=NOT_VERIFIED`, `CODE_ACCEPTED=NOT_VERIFIED`.
