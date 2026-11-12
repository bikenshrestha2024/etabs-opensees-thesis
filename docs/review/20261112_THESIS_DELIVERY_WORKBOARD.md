# Thesis delivery workboard — audited 2026-11-12

**Review branch:** `review/20261112-thesis-readiness-and-organization`  
**Baseline `main`:** `dcb0727a507ca23443c122a55082260fea954e2e`  
**User objective:** reproducible, computationally efficient, organized and scientifically defensible ETABS→OpenSeesPy study of a 25-storey asymmetric-plan RCC high rise with conventional/damped outrigger configurations M0–M6.

This file is a **work plan and source review**, not a pass certificate.

## What was actually inspected

- Repository recursive `main` tree: **3,298 entries**, **2,797 files**, **238 distinct top-level names**, **565 entries under the historical V156 copy**. Tree is not truncated. These are inventory counts, not an assertion that each file was semantically reviewed.
- Existing canonical launcher index: `docs/programs/00_PROGRAM_INDEX.md` (stable root 01–37 navigation IDs, gaps intentionally preserved).
- Existing migration and governance: `engineering/migration/README.md`, `engineering/rules/CORE_RULES.md`, `engineering/rules/ENGINEERING_GATES.md`, `AGENTS.md`.
- Exact active implementation inspected: `components/model/readiness_dashboard.py`, `readiness_dashboard_gui.py`, `nonlinear_preflight.py`, `components/model/readiness_gui.py`, `components/nonlinear_time_history/material_source_sets.py`, `tests/verify_readiness_dashboard.py`.
- Screenshot/report facts supplied 2026-11-12: dependency scanner finds five core export files and all listed Python packages, `nonlinear_materials_file` unset, empty `nonlinear_wall_fsam_tags`, reviewer approval false; dashboard had `NO_MODEL_SELECTED`.
- ETABS export log: 25 stories, 95 m, 1367 frames (55 no nonempty assigned section read from API), 725 areas, 76 supports; source ETABS closed without saving. These object counts do not establish validated nonlinear reinforcement.
- Kobe prior LTH evidence: XY complete / YX incomplete; native solve performance and CSV recording remain to be benchmarked separately.

## Immediate fixes in review branch

1. **Project model discovery for GUI**: the standard `OpenSees_Complete_Nonlinear_Model.py` is selected automatically *only for inspection*, if it exists immediately within the chosen project directory. Explicit selection remains available. A gravity-only model is never substituted. Never auto-sign.
2. **Nonlinear material preflight clarity**: reports project external-file configuration separately from reference material cards; a stocked material catalog does not silently satisfy project-specific material review. JSON inventory retains `approval: false`.
3. **Fail-closed tests**: unique builder discovery, no gravity-model substitution, source model SHA binding and material reference/production separation; add tests to repository integrity CI.
4. **No physical model change**: original EDB, wall elements, gravity loads, FVD/BRB parameters, spectrum scaling, diaphragm and rigid body constraints, source frame sections, link orientation, and output archives remain untouched.

## Thesis-critical backlog with strict acceptance gates

| Priority | Workstream | Evidence required | Present status |
|---|---|---|---|
| P0 | Model identity and readiness | Source EDB+generated model SHA, active config, external material source, actual frame reinforcement, explicit FSAM wall region map | Missing/review required |
| P0 | Wall failure | Minimal ZERO / X / Y / XY first-step finite stresses, element tag→ETABS mapping, connectivity, orientation, material sign, mass and constraint diagnostics | X first step unresolved |
| P0 | Gravity/load-path equivalence | Original 32 ETABS support reactions, matching support set/ULS-SLS gravity, 3D slab self-weight and frame/wall joint overlap, independently recovered story force | Not validated |
| P0 | Material/section behavior | Source-specific ConcreteCM/Concrete01/02, Steel02/MPF, FSAM benchmark overlays, section moment-curvature, actual reinforcement mapping, units | Source cards exist; not project-approved |
| P1 | Linear/modal/RSA and P-Delta | T1-X/Y from verified modes, Tn90 coverage, ETABS vs OpenSees stiffness/mass and modal shapes, base/shear/drift, signed +/− eccentricity | Partial evidence |
| P1 | LTH performance | Baseline/factorOnce/vector recorder controlled XY/YX short sample, all-step equivalence, solve vs recorder time, Windows CPU/RAM, persisted completed cases | Native benchmark pending |
| P1 | Device models | FVD exponential law units C, α, series stiffness/stroke/dissipation; BRB yield/strain/hysteresis and failure calibration | Native recorders reference tests; not project-validated |
| P1 | Ground motions NBC 105 | All eight matched Soil C pairs, 16 source SHA, no double scaling, component factor proof 0.33–3, original SeismoMatch logs, Gorkha/Loma discrepancies resolved, both XY/YX, vertical §4.3 applicability | Conditional matching; unresolved provenance |
| P2 | M0–M6 full analysis | 7 variants × ULS/SLS × 8 paired records × XY/YX = 224 intended analyses; controlled source hashes, full duration, accepted convergence and equivalent outputs | PLANNED, not solved |
| P2 | Thesis sensitivity | Source values and ranges, one-at-a-time/factorial design, physical bounds, response quantities, ranking with uncertainty; no certified optimum without convergence | Planned |
| P2 | Thesis delivery | Reproducible parameter table, tables/plots, cited literature DOI and licensing, solver versions, independent comparisons, limitations | Research outputs pending |

## Systematic repository organization — preserve compatibility

**Keep active paths**: root launchers and aliases; `components/` solver/domain packages; `tests/` regressions; `Material_Catalog/` source cards; `LITERATURE/` DOI/URL bibliography and code-reference indexes; `docs/source/` per-module guides; `REVIEW_MAIN/` unresolved discrepancies; `engineering/` canonical registry and governance.

**Do not move** existing `Saved_Project_V156/`, model results, Excel/EDB files or third-party PDFs without an owner/consumer graph and SHA manifest. The user runs Windows paths/Spyder and saved scripts may depend on those names. Root has many historical aliases: the launcher index, **not lexicographical filename order**, is authoritative.

**Suggested outputs on the user's machine** (not generated by repository migration):
- `OpenSees_Analysis_Results/<state>/<case>/00_MANIFEST/`
- `01_INPUTS_READONLY/`, `02_GRAVITY/`, `03_MODAL/`, `04_LINEAR/`, `05_NLTHA/`
- `06_COMPARE_ETABS/`, `07_REVIEW/`, `08_FIGURES/`, `09_EXPORT_ZIP/`.
Any adoption requires updating existing output readers in a separately tested migration; **this proposal does not rename current output paths**.

## Definition of completion

A successful GUI or GitHub Actions run is **software evidence only**. A successful first linear orientation is **not a complete paired earthquake**, a paper-based material demo is **not a project calibration**, and a static source import audit is **not ETABS physical equivalence**. Mark each independently as SOURCE_VERIFIED / NUMERICALLY_CONVERGED / ETABS_EQUIVALENT / COMPONENT_VALIDATED / CODE_ACCEPTED only when the corresponding evidence has actually been reviewed.

Before merging any future large physical changes, require unit tests, full source imports, native Windows test and independent engineering review. Keep history and failures immutable; never fabricate or overwrite native analysis results.
