# ESM Aw and adopted-period code review checkpoint — 2026-11-04

Starting `main` commit: `82080acc44c9b66cc2d2ec6b26e1f283d1dcd831`. Proposed implementation: branch `fix/esm-aw-period-provenance-20261104`, PR #8.

This is a bounded engineering/software inspection, **not** a complete project ETABS equivalence review or NBC design certification. Historical CSV snapshots are not overwritten.

| Source at starting commit | Original blob | Code actually read | Finding and correction | Verification in this session | Remaining |
|---|---|---|---|---|---|
| `components/inputs/project_workbooks.py` | `4255d430e7edce1d0903947de02b89c8257cdc54` | Entire 340-line file, particularly `source_workbooks`, `_wall_aw_from_lines`, `import_project_inputs`, `populate` | Nonportable `Path(...).stem` for stored Windows EDB, workbook filename fallback bypassing identity, shell projections merged over distinct z-elevations; added identity gate and vertical-slice geometry guard | New synthetic tests written; CI execution pending | Independent first-storey wall opening/effective-length mapping vs ETABS; wall local axes and exclusions |
| `components/equivalent_static/calculation_and_gui.py` | `c1908cefad61428535f1372b9114d36837896771` | Function index and source blocks 1-95, 330-365, 475-576, 639-674, 735-811 | Workbook reference enabled by default; no explicit ULS/SLS Rayleigh split in `Both`; selected period metadata was shared GUI field | New synthetic tests written; CI execution pending | Validate GUI/manual workbook/reference behavior on real Windows model |
| `components/modal/analysis.py` | `364f8060812a9dd156cf423fa3369e22d137a0d3` | `nbc105_period_estimate` (approx. lines 29-95) | Basic `0.075H^.75 / sqrt(Aw)` with `1.25` and min(Rayleigh) already present; not altered | Existing tests inspected; not executed here | Confirm H/base selection and separate effective wall areas in ETABS |
| `components/inputs/etabs_periods.py` | `349d966fc587d6f7285875a91533ff34484106b6` | Entire file (workbook modal sources and cache) | ETABS modal comparison periods are not NBC §5.1 Rayleigh periods | Not executed | Verify selected modal mode and actual ETABS analysis case |
| `tests/verify_nbc105_periods.py` | `fc14bcd305d1e441c5b7c4d4cb6dd24ab701ee5c` | Entire test source retrieved | Existing checks exercise geometry segmentation and case/hash bound Rayleigh cache | Not executed | Extend native ETABS and real wall openings |
| `tests/verify_esm_source_selection.py` and `tests/verify_esm_partial_input.py` | Source fetched | Entire retrieved sources | Existing no-stale-ledger/blank-Aw GUI tests retained | Not executed | Run alongside new tests |

## NBC 105:2025 cross-check

The official DUDBC NBC 105:2025 **§5.1.1–5.1.3** document was opened and the printed formula page inspected. `Aw=Σ Awi(0.2+(Lwi/H)²)` with `Lwi/H<=0.9`, empirical period `0.075 H^.75/sqrt(Aw)` for shear-wall buildings, amplification `1.25`, and adoption of the smaller amplified empirical / Rayleigh periods are the expected mathematical relationship. This **does not prove** that the actual ETABS first-storey wall areas, effective lengths or height definition were correctly exported.

## Test/evidence status

- GitHub commits: **PASS** (branch writes confirmed through GitHub connector).
- Code review: **PARTIAL** (named files/lines above only; see details).
- New synthetic tests: **NOT RUN locally**; GitHub Actions workflow configured and execution must be checked.
- Native ETABS/OpenSees ESM rerun: **NOT RUN**.
- Real ULS/SLS modal stiffness reconciliation: **REQUIRES PROJECT EVIDENCE**.
- Correct physical interpretation of wall openings and basement height: **REQUIRES PROJECT EVIDENCE**.
- High-rise ULS equivalent-static eligibility: **NOT EVALUATED**; ESM is diagnostic where §3.2.1 conditions do not permit it.

Do not merge a failing CI or label this change as independently validated against an ETABS model.

## 2026-11-05 independent failure-log follow-up and external basis

**Actual GitHub Actions failure discovered:** branch commit `439d8bcf` had a failed new synthetic test `test_windows_edb_identity_selects_correct_scaling_workbook`: `source_workbooks` returned `None` instead of the correct workbook because the source floor name was recognized only by a regex against a combined string, and the Windows EDB path used a backslash before the floor number. This was an **actual failing regression**, not a hypothetical defect.

**Correction:** `components/inputs/project_workbooks.py:source_workbooks.score` now obtains floor identity from the parsed EDB source stem using `_model_floor`, with a filename fallback only when source metadata cannot supply the floor. Exact source identity still rejects known wrong EDBs. The CI run at commit `01a4997dfcc64092396412b5ee5baefe2add1414` completed successfully: [GitHub Actions run](https://github.com/bikenshrestha2024/opensees-nbc105-research/actions/runs/41943908613). This **does not** validate actual ETABS wall area or base shear.

**Cross-project reading scope:** earlier project `02_MODELLING_BASIS.md` (assumed material hierarchy, nominal Concrete02/ConcreteCM and Fe500/SteelMPF, FVD unit conversion and outrigger connection limitations); wall fork `SFI-MVLEM-3D/README.md` (original 3D four-node FSAM formulation, not the enhanced E-SFI); active main `docs/review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md` and `docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md` (known P0 gates). No whole-source line review of those other repositories was performed.

**Verified external sources checked:** official NBC 105:2025 §§5.1,5.2,6.1–6.5,7.3,7.5,9.3, DUDBC catalog; OpenSees E-SFI wall element input/recorders; CTBUH *Outrigger Design for High-Rise Buildings* (2nd ed., 2017); PEER 2017/06 performance guidelines; Malik and Kolay (2023), DOI 10.1002/tal.2003. See [complete engineering parameter manual](../20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md) and [machine-readable parameter register](../20261105_PARAMETER_PROVENANCE_REGISTER.csv).

**Open checks:** root-to-tip effective-wall area and height acceptance; project rebar and confinement; full native Zero/X/Y/XY diagnosis; eight-pair original SeismoMatch scaling provenance; actual ULS/SLS model-specific Rayleigh/ETABS comparison and 224 intended M0–M6 histories. Review remains **PARTIAL**. 
