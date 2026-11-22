# Direct Existing OpenSees NLTHA — implementation and verification plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans with test-driven-development and verification-before-completion. This is the task ledger retained with the implementation; it documents the actual sequence and remaining native dependencies rather than pretending a solver was run.

**Goal:** Enable reproducible explicit one-case native OpenSees NLTHA from the existing 25-storey model and expose literature-oriented methodology without overriding engineering acceptance.

**Architecture:** Reuse the canonical existing `building_exploratory.py` for nonlinear physics, gravity, domain assembly and accepted-step recording. Add `soil_c_case_execution.py` strictly as a source SHA-checked one-config subprocess launcher plus local results status. Reuse source audit from `soil_c_nltha_suite` and numeric configuration audit from `soil_c_physics_preflight`. No changes to solver algorithms, materials or source geometry.

**Tech stack:** Windows Python 3.12 / OpenSeesPy native for user execution; stdlib subprocess+hashlib/json; existing project unittest/pytest CI for headless gates.

**Spec/authority:** `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md`, `docs/00_THESIS_ACCEPTANCE_GATES.md`, `docs/programs/36_SOIL_C_M0_M6_RUN_MATRIX.md`.

## Global constraints

- Foundation: exactly 32 physical supports and 44 wall-mesh points, not 76 independent foundations.
- Source X wall: two 12 m lines with actual openings; no arbitrary source-model changes.
- Full comparison gravity: `GRAVITY_1.0D_1.0L`; seismic mass separate per NBC 105:2025 §5.2.
- Acc(g) matched Soil C files unchanged, additional factor 1.0, OpenSees acceleration 9.81 m/s² per g.
- One case = XY and YX in independently built domains; do not infer 224 native runs from 112 generated configs.
- Native wall failure, reinforcement, device calibration, support reaction discrepancy and current modal factors remain unverified until actual source data/solver replay.
- No private source workbooks, EDB, waveforms, full paper PDFs, or confidential local outputs committed.

## Work packages and evidence

- [x] Inspect mandatory repository contract and current run matrix vs native `building_exploratory.py`.
- [x] Add test-first cases for diagnostic opt-in, source SHA gate, required exports, output collision, incomplete paired result, two accepted software screens, failed child return.
- [x] Observe RED on test-only branch head via GitHub headless pytest (`ImportError: soil_c_case_execution`, job 137202903139).
- [x] Implement minimum orchestration wrapper and immutable local status/config preservation.
- [x] Write Stage 38 CLI facade and per-source module guide, update active module inventory/program index and canonical registry.
- [x] Draft thesis methodology chapter aligned with literature/source register without inventing laboratory data.
- [ ] Confirm fresh full GitHub Actions suite on final branch head; record exact run IDs and counts. Never rely on a previous head.
- [ ] Reproduce native ZERO/X/Y/XY wall controls on matched 25-storey model in user's Windows environment.
- [ ] Confirm source-based wall/web/boundary reinforcement, 32-support ETABS equilibrium and material/device calibration.
- [ ] Complete one full-duration, finite XY+YX native case with dt sensitivity and independent source/body-force review.
- [ ] Complete 224 planned runs and aggregate only qualified accepted cases.

## Review focus

1. False acceptance from child exit 0 with one missing orientation; result gate must reject.
2. Accidental reuse/overwrite of a previous case folder; must fail before subprocess.
3. Matched ground motion changed since Stage 36; SHA-based event gate must fail.
4. Unqualified Stage 36 exploratory template promoted by command flag; explicit opt-in remains diagnostic.
5. Native solver fails after creating partial results; preserve failure status and logs and do not average.

## Ruling and limitations

The executable cannot create calibrated RC/FVD material data that was not present in the source model or review manifests. The appropriate production contract is **direct native execution when the prerequisites exist**, not software pretending structural convergence. The ChatGPT connector environment had no installed OpenSeesPy or private user EDB/waveforms and could not clone the repository through the container; native execution remains pending. GitHub Actions evaluates headless software only. We keep the user-provided shared ChatGPT link as context but did not reconstruct any inaccessible private conversation contents.
