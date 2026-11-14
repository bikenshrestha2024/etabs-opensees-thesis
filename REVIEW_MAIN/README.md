> **Numbered top-level navigation:** [07 — Thesis review backbone](../07_REVIEW_MAIN/README.md). This existing `REVIEW_MAIN/` folder retains the authoritative issues and source links; no files or evidence were duplicated or moved.

**Canonical output organization and migration audit:** [2026-11-14 folder-stage review](08_SOFTWARE_SECURITY/20261114_CANONICAL_STAGE_FOLDER_AND_MIGRATION_AUDIT.md). Local source/copy inventory is generated with `22_AUDIT_EXPORT_FOLDERS.py` and kept outside GitHub.

# REVIEW MAIN — Engineering discrepancy and validation register

**Project:** ETABS → OpenSeesPy, NBC 105:2025 asymmetric RCC high-rise/outtrigger thesis. **Opened:** 2026-11-11. **Status:** ACTIVE; not a structural-design certificate.

This is a non-destructive, public-safe REVIEW directory. Do not upload the original EDB, drawings, XLSX, ground motions, access tokens, or unredacted result ZIPs to GitHub. Preserve source hashes and exact project states. A passing Python test, internal force equilibrium, or converged transient is not proof of ETABS–OpenSees equivalence or code compliance.

**Cross-stage operating procedure:** [KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK](../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/README.md) — canonical numbered launchers, source/mass/mesh/stiffness gates, repeatable evidence and ownership; [IS 16700 amendment tracker](../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md).

**Current cross-module review (2026-11-14):** [Full folder layout, result-reader, stiffness, gravity, drift and nonlinear readiness audit](08_SOFTWARE_SECURITY/20261114_1709_FULL_CROSS_MODULE_REVIEW.md). P0 issues remain open; a folder audit pass is not native structural verification.

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
