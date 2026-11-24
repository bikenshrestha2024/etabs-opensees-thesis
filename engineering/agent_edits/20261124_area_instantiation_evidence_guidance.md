# 2026-11-24 — Area V116 missing instantiation evidence guidance

**Editor:** ChatGPT via connected GitHub plugin. **PR:** #194. **Base `main`:** `feddf47be56a16a90065d98ea40ec0dd6eec98ab`.
**Change class:** EXTEND existing `components/sections/area_elements.py` and its current tests/source guide; no duplicate active module, file migration or native model change.

## Read-first and physical contract

Actually read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, CORE_RULES / ENGINEERING_GATES / MODULE_BOUNDARIES, `docs/source/components/sections/area_elements.py.md`, the active area adapter and two existing tests, `docs/00_RESEARCH_REFERENCES.md`, `docs/00_THESIS_ACCEPTANCE_GATES.md`, `engineering/migration/README.md`, `docs/programs/00_PROGRAM_INDEX.md` and the Stage 02 model-area note. Source EDB bytes and current native ETABS live model: **UNAVAILABLE**; user workstation dirty tree: **UNAVAILABLE**.

Preserved without alteration: 32 actual physical foundation joints + 44 connected wall-mesh transfer points (76 mapped IDs are NOT 76 physical foundations); full 100% Dead + 100% Live gravity benchmark versus separate NBC 105:2025 §5.2 seismic weight; two continuous 12 m X walls with recorded openings and 3×6 m Y walls; isolated ULS/SLS and M0–M6; all native element, load, constraint, mass, material and P-Delta commands.

## Source evidence and exact cause

The supplied ZIP includes a valid source-only area inventory, not an optional saved `OpenSees_Area_Element_Integration_Audit_V116.json`. The source configuration remains unapproved with null wall FSAM tag. The separate MESH_04 package represents an elastic shell/model build, not the additive E-SFI wall helper or approved nonlinear material construction. `package_area_instantiation_audit` correctly raises a FileNotFoundError for a missing report and must **not** manufacture it or misrepresent the existing elastic mesh as independently instantiated nonlinear wall evidence. The prior Tk popup exposed only the missing filename and did not explain the blockers.

## Change and scope

Added a read-only config inspection helper returning report presence/status and missing FSAM/review status. Integrated its explanatory warning with the V116 instantiated-evidence ZIP action. Existing source-only inventory export, on-demand Excel, file ownership, source hash/manifest checks and fail-closed saved-report validation remain unchanged. The review status never becomes an engineering acceptance PASS on file presence alone. Do not make the optional additive V116 call on a domain already containing the floor/wall shells.

## TDD and verification

Test-first commit on PR branch `b7b3878e`: GitHub headless pytest collection **RED**, expected missing helper import in extended `tests/test_area_instantiation_evidence_zip_20261123.py`. Implementation `2a4b0b1a` followed RED. Final branch CI must complete before any merge. Project source EDB/workbooks, uploaded private ZIPs, concrete/rebar/FSAM parameters, numerical source values and local user paths were not committed.

**Source/software review statuses** are not numerical approval: `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED` remain **NOT_VERIFIED** for the selected actual building and optional nonlinear area instantiation.
