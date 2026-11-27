# ETABS → OpenSees All-Module Handoff Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all active ETABS-to-OpenSees module families exchange source-bound, purpose-bound, verified evidence without unsafe stale-data fallback or unnecessary repeated work.

**Architecture:** Extend the existing canonical owner contracts (`components/inputs/output_contract.py`, `project_workbooks.py`, existing CaseLedger, and current AST audit tools). Do not create a second workflow orchestrator, second output folder policy, or second engineering source of truth. Each task is a small independently reviewable change, with writer/reader migrations and synthetic red/green tests. Native structural acceptance is a separate gate.

**Tech Stack:** Python 3.12, OpenSeesPy, ETABS 23 COM adapter on Windows, Tk, pytest, JSON/CSV/XLSX, GitHub Actions; conda-forge-only user installation.

**Spec:** `AGENTS.md`; `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`; `engineering/rules/CORE_RULES.md`; `engineering/rules/ENGINEERING_GATES.md`; `docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md`; `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_ETABS_OPENSEES_HANDOFF_AUDIT.md`; `REVIEW_MAIN/09_SOFTWARE_SECURITY/20261123_ALL_MODULE_HANDOFF_FOLLOWUP.md`.

## Global constraints

- Preflight: read `AGENTS.md`, physical-model contract, `.agents/skills/etabs-opensees-read-first/SKILL.md`, current source guides, code-purpose matrix; record actual Git SHA and source hashes.
- Primary foundation is 32 physical supports. Other 44 of the 76 mapped base points are shear-wall mesh points, NOT 44 additional foundation supports. Preserve verified edge/MPC topology; 76/97 are sensitivity studies.
- Full gravity comparison is exactly `GRAVITY_1.0D_1.0L`. Seismic weight is separate NBC 105:2025 §5.2/Table 5-1 source-category ledger; P-Delta and transient preload are distinct purposes.
- Current source geometry is two 12 m X walls with openings and three 6 m Y walls. Match EDB/workbook/config SHA; do not adopt stale V10.6 by filename.
- Structural outputs may be `NUMERICALLY_CONVERGED` without being `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, or `CODE_ACCEPTED`. Missing native evidence is `NOT_VERIFIED`.
- No private EDB/workbook/ground-motion uploads to public repository; published ZIP manifests exclude host paths and ZIP content requires privacy review.
- Keep active facades/launchers; migrate source writers and readers together. No blanket rename of historical archives, random `*_latest.py` copies or unmeasured optimization.
- Concurrent branches/PRs may modify stage sources: refresh HEAD, check relevant open PR diff and avoid reimplementing merged work before each task.

## Review focus / negative cases

1. Wrong source EDB or V10.7 workbook pair: reject identical filenames with different SHA in SOURCE_INPUTS and all case readers.
2. Source support list contains 76/97 while actual runtime is selected primary32: keep native edge connectivity and reject mismatched output classification.
3. Full gravity case receives seismic `0.3LL`: fail load-purpose test, including roof live and storage patterns.
4. Old completed JSON/runner `CASE_STATUS` presented after editing source/mass/stiffness: reject stale saved evidence.
5. A generated or incomplete ZIP incorrectly appears as an accepted solver result: manifest explicitly distinguishes source-only, force-only, solved, and engineering-reviewed.

## Implementation sequence (one reviewed PR per task or tightly linked task pair)

### Task 1 — SOURCE_INPUTS: immutable source registry and exact input selection

**Files:** `components/inputs/project_workbooks.py`, `components/inputs/output_contract.py`; existing related tests in `tests/`.

- [ ] Add failing fixture where EDB/workbook share names but differ in SHA or model case; assert source selection rejects it.
- [ ] Verify RED by running the affected pytest file.
- [ ] Extend existing source registry/manifest only as necessary, carrying source-role, SHA256, state, and workbook cell provenance.
- [ ] Verify GREEN and cross-stage readers; do not auto-promote old calculator/scaling default filenames.
- [ ] Run repository headless suite and commit bounded changes.

### Task 2 — MODEL: source ID, topology, end zones, stiffness handoff

**Files:** `components/model/assembly.py`, `source_node_identity.py`, `elastic_conversion_settings.py`; `components/sections/mapping_gui.py`.

- [ ] Test duplicate source XYZ, separate FRAME:1 / AREA:1, topology-only object with no assembled solver tags, shell/beam joint identity.
- [ ] Verify native frame end-zone assignments and shell modifiers with same-source exported tables; do not invent tie constraints or native shell shear equivalence.
- [ ] Preserve one-to-many source object to solver element map, explicit missing element count, source and solver tag namespaces.
- [ ] Benchmark MESH 04/08/16 parsing/assembly separately and capture geometry/conformity before optimizing the mesher.

### Task 3 — SECTIONS: material/device/area registration

**Files:** `components/sections/area_elements.py`, `mapping_audit.py`, `components/nonlinear_time_history/research_building_materials.py`.

- [ ] Exercise source-only inventory and archive, no empty-success ZIP and SHA-bound optional evidence.
- [ ] Verify area geometry, openings, local winding, wall macro-fiber subdivisions, floor mesh transfer, and no duplicate solver element assembly.
- [ ] Track rebar/FSAM/SteelMPF/ConcreteCM/FVD/BRB provenance and transfer literature status; no synthetic experimental approval.

### Task 4 — GRAVITY and initial-state MODEL

**Files:** `components/gravity/solver_stack.py`, `comparison_bundle.py`, `components/model/eq_pdelta_initial_tangent.py`.

- [ ] Test separate D/L ledgers, full 1D+1L versus NBC mass, 32 primary supports versus 76/97 diagnostic metadata.
- [ ] Compare same-source 32-support Fx/Fy/Fz/Mx/My/Mz and common wall-base cuts; investigate 768.045 kN archived max joint residual without force fitting.
- [ ] Verify native edge transfer and rigid end zone policies, signed static EQ initial states and no double-counted subsequent transient EQ.
- [ ] Keep `GLOBAL_EQUILIBRIUM_PASS` separate from joint-equivalence and project code acceptance.

### Task 5 — MODAL and NBC105 source authority

**Files:** `components/modal/analysis.py`, `rayleigh.py`, `components/nbc105/`.

- [ ] Test mass operator, actual 32-support constraints, state-specific ULS/SLS stiffness, floor COM/inertia and Rayleigh/empirical period provenance.
- [ ] Independently verify the 10-clause NBC 105:2025 source references, printed page/table/footnote and project-specific IS 16700 exceptions.
- [ ] Surface Vs30 and high-rise ULS ESM applicability as independent blockers; no claim of full clause compliance from static equations.

### Task 6 — ESM: calculation / runner / output owner parity

**Files:** `components/equivalent_static/calculation_and_gui.py`, `organized_exports.py`.

- [ ] Test source-bound input and calculation case identity for X/Y, ULS/SLS, E0/E+/E-, signed force polarity and orthogonal eccentricity.
- [ ] Reject stale runner with same filename but changed bytes; distinguish 12 script generation from 12 actual completed solves.
- [ ] Ensure canonical `03_ESM/RUNS` calculation, reader, case status, Excel and ZIP capture matching SHA and report purpose.
- [ ] Compute each axis base force only once per source/model configuration, but independently run solver responses.

### Task 7 — MRSM: actual runtime source consistency

**Files:** `components/response_spectrum/model_analysis.py`, `components/model/support_case_contract.py`.

- [ ] Test `solver_reaction_support_tags` results against actual model-built restraints; no raw 76-node fallback for primary32 reactions.
- [ ] Cross-check modal generalized masses with selected actual runtime mass policy and native support cut, not just saved input JSON.
- [ ] Verify CQC spectra/scaling, six X/Y E0/E+/E- cases and distinguish scaled force from unscaled drift.
- [ ] Reopen saved results only when all case/config/source/result hashes match and outputs pass numeric completeness.

### Task 8 — LTHA: full-duration, fresh domain, motion provenance

**Files:** `components/linear_time_history/runner_and_gui.py`, `components/shared/response_recorders.py`.

- [ ] Fail incorrect XYZ motion axes, g/dt conversion, paired-component hashes, missing records and truncated history marked full.
- [ ] Rebuild a fresh solver domain per orientation, with source-bound preload and absolute/relative acceleration evidence.
- [ ] Publish completed result and recorder hashes, not merely process exit messages; preserve cancellation and traceback.

### Task 9 — NLTHA: X-wall first-step and accepted full history

**Files:** `components/nonlinear_time_history/runner_and_gui.py`, `direct_existing_model.py`, `source_model_handoff.py`.

- [ ] Reproduce source-localized failure at wall element 110280 with ZERO/X/Y/XY isolated cases and timestep/status/last finite state records.
- [ ] Verify same-source materials, reinforcement, wall opening mesh, confinement, devices, preload and P-Delta before changing constitutive physics.
- [ ] Check original matched Soil-C record pairs, XY/YX orientations, scale 1.0 and complete duration with finite/energy/response output.
- [ ] Only count full-duration converged M0–M6 runs; the planned 224 cases are not solved evidence.

### Task 10 — VALIDATION: native ETABS/OpenSees comparators

**Files:** `components/validation/`, `components/gravity/comparison_bundle.py`.

- [ ] Require same source EDB, physical support crosswalk, stiffness/mass purpose, gravity case, units and load combinations.
- [ ] Compare independent section-cut Fx/Fy/Fz/Mx/My/Mz, support-by-support residual norm, modal period/mass, MRSM shear/drift and transient response.
- [ ] Publish data-provenance hashes and clear missing native evidence states; no force normalization to conceal mismatch.

### Task 11 — GUI: no stale evidence or blocking exports

**Files:** `components/ui/application.py`, stage-specific GUIs, `components/inputs/output_contract.py`.

- [ ] Test saved-case selection after source changes, async readback with Tk main-thread updates, nonblocking progress/cancellation, exact frame/area/solver ID highlighting.
- [ ] Keep Generate Excel, large 3D viewer and ZIP optional and initiated only on user request; do not write full workbook on window open.
- [ ] Show separate INPUTS, ASSEMBLED, GENERATED, SOLVER_RUNNING, COMPLETED_SOLVER_ONLY, ETABS_MATCH_PENDING and CODE_ACCEPTED statuses.

### Task 12 — SHARED / CORE_OR_ADAPTER / TOOLING / root launchers

**Files:** `components/shared/`, `src/`, `tools/audit_cross_module_consistency.py`, `tools/audit_output_writer_reader_pairs.py`; `01_WORKFLOW_START.py` and documented numbered launchers.

- [ ] Run AST parse, duplicate-body candidate inventory, import-edge graph, source-guide completeness, writer/reader inventory and output ownership checks.
- [ ] Review 32 exact-body clone groups and 84 executable legacy-path marker occurrences individually (historical static values from prior audit; current count requires rerun); do not delete automatically.
- [ ] Add a tested matrix showing which stage consumes which exact manifest and its valid status; CI must reject a newly introduced unowned output writer.
- [ ] Confirm launcher facades route to actual active modules, no imports of preserved Saved_Project_V156 runtime for production.
- [ ] Verify synthetic end-to-end case: source → assembly → gravity → modal → ESM/MRSM → review ZIP with explicit absent native evidence status.

## Execution & reporting

Run read-only audits before and after each task:

```powershell
python tools/audit_cross_module_consistency.py --repo . --report-dir audit/module_consistency --fail-on-parse
python tools/audit_output_writer_reader_pairs.py --repo . --report-dir audit/output_pairs --fail-on-parse
python -m pytest -q
```

Native acceptance additionally requires same-source Windows ETABS v23, OpenSeesPy and model/ground-motion run logs. Record changed paths, source SHA, regression RED/GREEN evidence, total test summary, native checks that actually ran, errors, unresolved issue and PR/commit SHA. Never replace current source acceptance with previously recorded successful CI from a different commit.

**2026-11-23 baseline:** `main@c93dd7646c39`; 3,502 tracked files, 212 Python files in `components/`. Existing reviewed source already includes explicit MRSM runtime support and saved-case identity improvements. Area evidence ZIP lives in separate draft PR #166. This plan is a dependency/verification program, **not evidence that 212 Python files were semantically reviewed or that native engineering acceptance has passed**.
