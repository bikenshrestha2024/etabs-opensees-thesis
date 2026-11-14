# 2026-11-14 — Independent review of DeepSeek ETABS-to-OpenSees architecture proposals

**Scope:** recommendation assessment only. Does not change OpenSees physics, ETABS data, constitutive assumptions, safety gates or accepted thesis results. **Status:** proposed, not experimentally or natively validated.

## Existing features: don't duplicate
- `src/thesis_core/neutral_model.py`: schema_version 0.1.0, fail-closed minimal standalone **single elastic 3D beam-column**, not a full source-to-solver exchange schema.
- `src/etabs_adapter/`, `src/opensees_engine/` and `engineering/rules/MODULE_BOUNDARIES.md`: designed modular architecture; full production converter not yet migrated.
- `tools/run_standalone_benchmark.py`: analytical axial cantilever comparison, not full RC core wall, slab, cap truss, FVD/BRB or building benchmark.
- `KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv`: stages, source, roles and acceptance gates already tracked.
- `components/model/assembly.py`, `components/gravity/`, `components/validation/`: existing primary numerical and independent ETABS comparison code. Preserve canonical imports, object ID provenance, saved run compatibility, and launches.
- `LITERATURE/MASTER_LITERATURE_INDEX.csv` and `LITERATURE/CODE_CITATION_OCCURRENCES.csv`: bibliographic register and automated citation scan already present. Do not invent DOI or citation count.

## Adopt, ordered by dependencies
**P0 — Freeze the current case and document mapping:** canonical `CONVERSION_SPEC.md` should reference existing guides, then map ETABS OAPI property / source field -> neutral field -> OpenSees command -> expected units -> validation -> evidence file. Include native ETABS unique object IDs, topology tags, assembled solver tags and display-only aliases. Missing/unsupported releases, offsets, self-weight, mass, rigid diaphragms, shell joints or walls fail closed.

**P0 — Existing physical checks before numerical migration:** current slab ShellMITC4 interface joint balance and element-end forces, 32 vs 76 vs 97 support roles, beam weight and overlapping volume, exact original ULS source workbook and SHA, hinged outrigger/belt/cap connection types, broken X-wall first-step failure. No neutral schema or external converter can be used to label these as fixed.

**P1 — Versioned rich neutral schema in a new, opt-in feature gate:** support node DOFs, source ID maps, releases/springs, offsets, shell polygons and opening geometry, local axes, ETABS native mesh, material/rebar provenance, FVD/BRB states, masses and loads by source case, diaphragm constraints, purpose (elastic/nonlinear) and NBC/IS assumption source. Validate roundtrip and fail on unsupported entities. **Never replace** existing schema_version 0.1.0 with an incompatible schema without explicit migration. Build a parallel comparison against existing `components/model/assembly.py`, inspect results, then progressively redirect callers after tests.

**P1 — Benchmarks by physics:** two-node axial cantilever (already implemented); one beam flexure and released end; independent axial diagonal brace; shell patch and load integration; frame–slab interface bending and vertical reactions; meshed wall with opening; core and coupling beam; diaphragm constraints; mass and first 3 modes; outrigger/belt/cap connection; initial P-Delta; FVD Maxwell force-velocity and BRB cyclic qualification. Run scripts without user ETABS data in CI. Gate project-specific source comparisons behind native/local execution, and record `NOT_RUN`, `FAIL`, `PASS_SCREEN`, `ENGINEER_REVIEW` distinctly.

**P1 — Reproducibility outputs:** machine-readable per-run status/metric/unit/value/tolerance/source model SHA/tool version/solver version/limit state/record orientation/time step/provenance; immutable outputs, no overwrite; `CONVERSION_SPEC.md`, `VALIDATION_REPORT.md` pointing to case evidence; machine-generated source coverage index. Existing organization and stage guides remain canonical; avoid second parallel READMEs with divergent acceptance.

**P2 — Reproducible environment:** minimal conda-forge locked dependency manifest for the supported Windows Python 3.12 environment; distinguish runtime from developer/test and optional visual libraries. Do not silently upgrade OpenSeesPy or numerical linear solver. `CITATION.cff` with only verified project author/license/version, BibTeX generated from catalog with verified DOI/date; optional Zenodo **only after** public-data/privacy/license review.

**P2 — Research external tools:** OpenSees/CEO conversion design useful as reference; prototype `opstool` postprocessing as a separately version-pinned optional backend, verifying plotting/responses against current Plotly and signed/OpenSees recorder outputs. DO NOT import its automatic mass distribution or adaptive numerical algorithm into production by default.

**P3 — Experimental:** IFC import/export and LLM-guided natural language operations may aid inspection, but neither has demonstrated physical equivalence of the current model. Require read-only mode, human approval and reproducible generated changes.

## Critical corrections to the DeepSeek report
1. A 2025 Scientific Reports case study reported 3.3% and 1.74% period differences for examined buildings; **not** a universal regulatory 5% gate. Matching mode shapes, modal participation, units, physical model and torsion are required before period errors are interpreted. Reference: https://doi.org/10.1038/s41598-025-94328-z.
2. Mass 0.1% and gravity equilibrium 0.01% are **candidate project screening goals**, not confirmed NBC 105:2025 code tolerances. Acceptance needs signed free-body and per-support/member checks plus exact matching load combinations.
3. `opstool` published by Yexiang Yan and Yazhou Xie in *SoftwareX* 30 (May 2025), article 102126, DOI https://doi.org/10.1016/j.softx.2025.102126 — real source supporting pre/post-processing, xarray, PyVista, visualization and some mass/unit support; **not proof** of interchangeability with the custom load/mass ledger.
4. CEO project documentation and PEER 2019 poster verify a Python ETABS+Excel -> OpenSees example architecture, not exact matching of this 25-storey asymmetric building. https://peer.berkeley.edu/sites/default/files/carlos_garcia_-_poster_-_peer_2019_-_final.pdf and https://www.ceostructural.com/features.html.
5. E2O-SEAOC2020, Portico_3D version claims, 2026 LLM framework, IFC-lite, and MATRIX_CALC Zenodo metadata are **UNVERIFIED / secondary until first-party records inspected**. A press release about MATRIX_CALC is not peer review. Do not copy its claimed DOI as validated research evidence without inspecting the Zenodo record.
6. A GitHub repository being public does NOT authorize publishing the original EDB, private XLSX data, sensitive result ZIPs, copyrighted PDFs, private links or source path lists.
7. Keep NBC 105:2025 as governing seismic basis; the project's specifically adopted IS 16700 initial-P-Delta and slab flexural modifiers stay explicitly scoped in AGENTS.md and the governing-code matrix.

## Recommended directory ownership
`src/thesis_core/` for neutral schema and validation; `src/etabs_adapter/` for optional ETABS import; `src/opensees_engine/` for future standalone production engine; existing `components/` remains authoritative until proven replaced; `tests/benchmarks/` for synthetic reproducible structural cases; `REVIEW_MAIN/` for project exceptions; `LITERATURE/` for authenticated source records; each model export's `01_ETABS_EXPORT/` for per-case inputs, maps, audits, hashes and visualization, NOT source code duplicated on each run.

## Candidate acceptance report fields
`test_id, source_edb_sha256, export_manifest_sha256, converter_git_sha, solver_version, schema_version, analysis_state, source_units, target_units, etabs_value, opensees_value, signed_residual, relative_error, screening_target, screening_basis, status, reviewer, evidence_paths, timestamp_utc`. Do not default to pass because an output file exists.

## Review status
- Source-code architecture assessment: **performed by repository file inspection**.
- Selected literature: **partially verified from primary articles and developer documentation**.
- ETABS native Windows solver, complete shell/brace nonlinear analyses: **NOT RUN**.
- Production converter/module migration: **NOT IMPLEMENTED**.
- Design and research acceptance: **NOT GRANTED**.
