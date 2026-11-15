**Current researcher-adopted outrigger member idealization (2026-11-15):** [DB-OUT-2026-11-15-01 — provisional pin-ended steel diagonals](00_MODEL/20261115_PROVISIONAL_HINGED_OUTRIGGER_BRACE_DESIGN_BASIS.md). **YES** as a working two-force truss diagonal model; **NOT** a blanket chord/core/column/interface hinge or nonlinear brace calibration. The 112 source ETABS release warnings remain traceable and the reviewed nonlinear failure gate remains unchanged. See [native release audit](00_MODEL/20261115_AREA_HINGED_BRACE_AND_MESH_EVIDENCE.md).

> **Numbered top-level navigation:** [07 — Thesis review backbone](../07_REVIEW_MAIN/README.md). This existing `REVIEW_MAIN/` folder retains the authoritative issues and source links; no files or evidence were duplicated or moved.

**Canonical output organization and migration audit:** [2026-11-14 folder-stage review](08_SOFTWARE_SECURITY/20261114_CANONICAL_STAGE_FOLDER_AND_MIGRATION_AUDIT.md). Local source/copy inventory is generated with `22_AUDIT_EXPORT_FOLDERS.py` and kept outside GitHub.

# REVIEW MAIN — Engineering discrepancy and validation register

**Project:** ETABS → OpenSeesPy, NBC 105:2025 asymmetric RCC high-rise/outtrigger thesis. **Opened:** 2026-11-11. **Status:** ACTIVE; not a structural-design certificate.

This is a non-destructive, public-safe REVIEW directory. Do not upload the original EDB, drawings, XLSX, ground motions, access tokens, or unredacted result ZIPs to GitHub. Preserve source hashes and exact project states. A passing Python test, internal force equilibrium, or converged transient is not proof of ETABS–OpenSees equivalence or code compliance.

**Cross-stage operating procedure:** [KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK](../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/README.md) — canonical numbered launchers, source/mass/mesh/stiffness gates, repeatable evidence and ownership; [IS 16700 amendment tracker](../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md).

**Current cross-module review (2026-11-14):** [Full folder layout, result-reader, stiffness, gravity, drift and nonlinear readiness audit](08_SOFTWARE_SECURITY/20261114_1709_FULL_CROSS_MODULE_REVIEW.md). P0 issues remain open; a folder audit pass is not native structural verification.

**V142 mixed-source response correction:** [Source model SHA screening and plot mismatch exclusions](08_SOFTWARE_SECURITY/20261114_V142_SOURCE_MODEL_FILTER_AND_PLOT_GATE.md).

**ESM post-run numerical integrity V5:** [Required saved ESM story/reaction/source identity before solver SUCCESS](02_ESM/20261114_SAVED_ESM_RESPONSE_INTEGRITY_V5.md).

**MRSM six-case batch correction V4:** [Canonical MRSM run writer, source-identity-safe result discovery and Windows verification gates](04_MRSM/20261114_CANONICAL_BATCH_OUTPUT_AND_SOURCE_GATES_V4.md).

**LTHA/NLTHA automatic stage migration V3:** [Canonical time-history outputs, unchanged numerical runners and required Windows native acceptance](08_SOFTWARE_SECURITY/20261114_LINEAR_NONLINEAR_HISTORY_OUTPUT_MIGRATION_V3.md).

**Live module migration V2:** [V135 diagnostic reports, canonical modal production + viewer and Windows verification sequence](08_SOFTWARE_SECURITY/20261114_LIVE_OUTPUT_STAGE_MIGRATION_V2.md). This is code- and CI-level verification; native structural acceptance remains open.

**Uniform output contract implementation (2026-11-14):** [Shared canonical stage names, derived Excel/JSON/CSV style, reader compatibility and migration gates](08_SOFTWARE_SECURITY/20261114_UNIFIED_OUTPUT_CONTRACT_IMPLEMENTATION.md). Native Windows ETABS/OpenSees validation remains open.

**All-module uniform output inventory V6:** [Common run-manifest checks, seven-stage and auxiliary inventory, shared diagnostic Excel/JSON format and remaining native evidence gates](08_SOFTWARE_SECURITY/20261114_ALL_MODULE_OUTPUT_INVENTORY_V6.md).

**Post-V6 missed-items audit and V7 correction:** [History completion gate, unresolved numerical/physical validation and canonical output checks](08_SOFTWARE_SECURITY/20261114_POST_V6_MISSED_ITEMS_V7.md).

**Legacy-only saved-model reader fixes V8:** [Irregularity stiffness screens, source-matched modal autofill and nonlinear preflight diagnostics](08_SOFTWARE_SECURITY/20261114_LEGACY_ONLY_READERS_AND_PREFLIGHT_V8.md).

**Additional V9 audit — missing stiffness coverage and truncated histories:** [Source-level fixes and remaining native validation](08_SOFTWARE_SECURITY/20261114_POST_V8_FAIL_CLOSED_STIFFNESS_AND_HISTORY_V9.md).

**MRSM nonfinite-response evidence correction V10:** [Reject NaN/missing design drift or nonhexadecimal model identity before six-case solver completion](04_MRSM/20261114_NONFINITE_SAVED_RESULT_GATE_V10.md).

**V11 numerical response/model manifest conflict:** [Exclude saved responses whose embedded source SHA disagrees with the run manifest](08_SOFTWARE_SECURITY/20261114_SOURCE_MANIFEST_VS_NUMERICAL_RESULT_V11.md).

**NBC 105 settings/V135 reference GUI V12:** [Six-tab source-aware code/project basis, local settings audit and legacy report path diagnostics](08_SOFTWARE_SECURITY/20261114_NBC_SETTINGS_REFERENCE_GUI_V12.md).

**V135 source-safe drift classification V13:** [Numerical drift PASS requires a source-matched model and completed saved run](08_SOFTWARE_SECURITY/20261114_V135_DRIFT_EVIDENCE_RECHECK_V13.md).

**Selected settings evidence source truth V14:** [Remove unconditional wall stiffness claim, validate recorded conventional slab factors, report missing/invalid settings](08_SOFTWARE_SECURITY/20261114_SETTINGS_AUDIT_SOURCE_TRUTH_V14.md).

## Case index
| Analysis | Folder | Critical checks |
|---|---|---|
| Input/source identity | [00_INPUT_PROVENANCE](00_INPUT_PROVENANCE/REVIEW.md) | EDB / workbook SHA256, load-state and Git LFS identity |
| **01 Import — export 02** | [2026-11-13 export 02](01_ETABS_IMPORT/20261113_EXPORT_02/01_IMPORT_AND_NONLINEAR_READINESS.md) | Source-identical re-export, topology, load/mass and actual nonlinear readiness |
| Gravity | [01_GRAVITY](01_GRAVITY/REVIEW.md) | 32/76/97 nodes, native support reactions, source weight |
| Equivalent static | [02_ESM](02_ESM/REVIEW.md) | opening-aware Aw, adopted T1, ESM eligibility |
| Modal | [03_MODAL](03_MODAL/REVIEW.md) | X/Y eigenmodes, mass and effective stiffness |
| MRSM | [04_MRSM](04_MRSM/REVIEW.md) | CQC, force scaling, story shear, edge drift |
| Linear time history | [05_LINEAR_TH](05_LINEAR_TH/REVIEW.md) | record completion and damping |
| Nonlinear time history | [06_NONLINEAR_TH](06_NONLINEAR_TH/REVIEW.md) | wall first-step failure, material validation |
| Cross-model ETABS comparisons | [07_ETABS_OPENSEES](07_ETABS_OPENSEES/REVIEW.md) | apples-to-apples force/displacement comparisons |
| Software and security | [08_SOFTWARE_SECURITY](08_SOFTWARE_SECURITY/REVIEW.md) | ZIP audit, GUI, credential safety |
| **Engineering Q&A** | [09_ENGINEERING_QA](09_ENGINEERING_QA/README.md) | NBC / IS code hierarchy, signed initial EL, physical NLTHA gravity, ETABS and OpenSees interpretation |
| Standard issue format | [90_TEMPLATES](90_TEMPLATES/ISSUE_TEMPLATE.md) | evidence and engineering judgment |

## Required nested folder structure for each local case
```text
REVIEW_MAIN/
  00_INPUT_PROVENANCE/ ... 08_SOFTWARE_SECURITY/
  90_TEMPLATES/
    ISSUE_TEMPLATE.md
  [analysis]/[case-id]/
    00_ISSUE/
    01_INPUT_MANIFEST/
    02_ETABS_NATIVE/
    03_OPENSEES_NATIVE/
    04_COMPARISON_TABLES/
    05_PLOTS/
    06_ENGINEERING_JUDGEMENT/
    07_CORRECTIVE_ACTIONS/
    08_REGRESSION_TESTS/
    09_REVIEW_SIGNOFF/
    10_PRIVATE_EVIDENCE/
```
**Private evidence directories should be created outside the public repository or securely excluded from Git.** This repository contains the review register and issue templates, not raw private evidence. Preserve existing active output paths; copy only redacted review artifacts, never move solver results by assumption.

**Mandatory source hierarchy:** [NBC 105 governing / IS 16700 exceptions matrix](../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md). All seismic methods and design cases use NBC. IS 16700 provides the **COMPULSORY, source-documented signed initial EQ P-Delta cases** and **REQUIRED conventional-slab flexural modifier**, plus clearly supplementary checks.

**P0 initial-state transfer:** [NBC §8.1.1.3/§9.3.1.3 + IS 16700 §7.2(d) source and analysis review](00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md). EQ with P-Delta must use verified initial P-Delta states without double-counted static EQ; EQ without P-Delta is a diagnostic control, not NBC compliant. All remaining IS checks are supplementary.

## Review methodology
1. Freeze a reproducible source manifest: SHA256 of EDB, workbook, export, code revision, ETABS/OpenSees versions, ULS/SLS, load combination, mass and stiffness selection.
2. Separate OBSERVED numerical data from engineering HYPOTHESIS and TESTABLE CAUSE.
3. Compare native ETABS and OpenSees definitions before comparing results; never compare 1.0D+1.0L gravity against D+0.3L preload.
4. Independently verify geometry, wall openings, diaphragm and support DOFs, rigid offsets, slab load transfer, mass and effective EI.
5. Compare gravity joint and group reactions; modal periods and matched mode participation; recovered story shear vs applied floor-force sums; drift at identical physical corners; base-shear scaling; and signed-history versus CQC envelope correctly.
6. Record governing code section with edition and explicit interpretation, reviewer and evidence paths. Cite NBC 105:2025 as governing Nepal seismic code; IS 13920:2016 details ductile RCC but does not by itself replace NBC empirical Aw or seismic response rules.
7. Keep each issue OPEN until native independent evidence and reviewer approval exist. Never self-certify a physical mismatch as solved.

## Review statuses
OPEN_BLOCKER, OPEN_HIGH, INVESTIGATE, SOURCE_VERIFIED, NUMERICAL_ONLY, ETABS_OPENSEES_MATCHED, EXPERIMENT_VALIDATED, CODE_ACCEPTED, CLOSED_VERIFIED. These are separate evidence categories, not an automatic progression.

## Existing authoritative documents
[AGENTS.md](../AGENTS.md) · [Engineering gates](../engineering/rules/ENGINEERING_GATES.md) · [Thesis gates](../docs/00_THESIS_ACCEPTANCE_GATES.md) · [Active engineering review](../docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md) · [Research citations](../docs/00_RESEARCH_REFERENCES.md).

## Primary source checks
- Official Nepal NBC 105:2025 edition: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
- OpenSees rigid diaphragm: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html
- OpenSees response spectrum analysis: https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/responseSpectrumAnalysis.html
- Indian IS 13920:2016: consult the legally applicable BIS edition/amendments; check actual boundary element, coupling beam, confinement and wall opening details before using in constitutive models.

**Scope limitation:** This initial register is based on user-provided November 11 screenshots/logs and existing GitHub engineering rules; no native ETABS run or complete result ZIP was executed or independently inspected as part of creating this register.
