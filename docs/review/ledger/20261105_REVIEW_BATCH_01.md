# Review batch 01 — bounded line-level inspection, 2026-11-05

**Source commit pinned:** `3977340abb79b307f376227605561f3868231f60`. Source list: [289-file exact Git blob ledger](CURRENT_MAIN_3977340_20261105_REVIEW_LEDGER.csv). Source lines below were actually retrieved and inspected from the main repository. Unlisted lines are **NOT_REVIEWED**. This is not a completed 289-file semantic or structural correctness review.

| Module | Actual source range read this turn | Inspected engineering or software issue | Status |
|---|---|---|---|
| `components/equivalent_static/calculation_and_gui.py` | ~30–95, 115–180, 330–365, 475–576, 639–674, 735–870 across review turns | Source model path validation, static load export/sidecar, ULS/SLS period provenance, worksheet output and combined case flow. Blank model path writing into cwd and mislabeled SLS Rayleigh metadata corrected via PR #9, CI passed | **PARTIAL SOURCE REVIEW**, no real model execution |
| `components/inputs/project_workbooks.py` | 1–370 across review turns | Scaling workbook EDB identity, matching limit state, first-storey wall projected segments, z-varying openings, Rayleigh cache and source-hash checks. Previous PR #8 fixes confirmed by regression | **PARTIAL SOURCE REVIEW**, physical wall-area grouping unverified |
| `components/model/assembly.py` | 1–100 | `_validate_insertion_point` and beginning of `_wall_panel_nodes`; structural offsets and E-SFI local panel ordering. These guards need model-specific ETABS geometry proof | **PARTIAL SOURCE REVIEW**, no native wall test |
| `components/nonlinear_time_history/building_exploratory.py` | 1–100 | solver selections, `diagnostic_record_inputs` XY/YX mapping, output separation and incomplete-case exception logging | **PARTIAL SOURCE REVIEW**, no complete earthquake |
| `components/nonlinear_time_history/research_building_materials.py` | 1–100 | Research-only provenance, parameter uncertainty bounds and first Steel01 brace reference; do not promote nominal or literature parameters | **PARTIAL SOURCE REVIEW**, no specimen calibration |
| `components/nonlinear_time_history/soil_c_run_matrix.py` | 1–100 | 7 variants, 2 states, 8 pairs planned, input SHA matching, independent case directory, XY/YX configurations. 224 cases **planned, not executed** | **PARTIAL SOURCE REVIEW**, native suite unrun |

## Verified repairs and preserved functions

1. PR #8 (merge `c3ac43de036d4b4b2e4e0da7668430fa15c7bafc`) corrected wrong-scaling workbook model identity, incomplete effective area projected through vertical openings, shared ULS/SLS Rayleigh period use and default adoption of unverified workbook periods. Passing CI does not establish ETABS geometric equivalence.
2. PR #7 (merge `4df8396ea5ac39ba3f20bbccd3e6ab29554eda3c`) added frozen review metadata and corrected stale PR status.
3. PR #9 (merge `3977340abb79b307f376227605561f3868231f60`) corrected a potential ESM P-Delta sidecar write into cwd on an absent model selection and misleading SLS Rayleigh evidence fields. Seven synthetic regressions passed in [CI run 41945662556](https://github.com/bikenshrestha2024/opensees-nbc105-research/actions/runs/41945662556). Existing explicit-model sidecar path and numeric ESM formulas were preserved.

## Next priority review queue

- **P0 (physical data):** `components/model/assembly.py` beyond 100; `components/model/load_and_diaphragm_audit.py`; `components/inputs/project_workbooks.py` wall grouping and story height. Independently reconcile each ETABS area/line load, master node, mass and reaction with source EDB and actual first-storey re-entrant/void geometry.
- **P0 (failure):** `building_exploratory.py` full transient and `wall_diagnostics.py`; source wall tag 110280; native ZERO/X/Y/XY at t=0.005 s with frozen input files and last accepted state.
- **P0 (materials):** actual wall confinement/reinforcement, E-SFI FSAM mapping and ConcreteCM/SteelMPF; section/building source hashes. Experimental calibration remains unavailable.
- **P1 (devices):** FVD Maxwell `K,Cd,alpha` with fractional exponent units; BRB cyclic energy, local link axes, output signs and no Rayleigh double damping.
- **P1 (motions):** eight Soil C pairs; matched Acc(g), separate XY/YX, actual SeismoMatch original component factors and period matching; actual Tn90 modal evidence.
- **P2:** UI responsiveness, documentation details, archived alias migration and graphical result comparators. Never rename existing legacy launchers without tested migration.

## Sources consulted and precise roles

- [Official DUDBC building code index](https://dudbc.gov.np/pages/building-code/) and [NBC 105:2025 Government document](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf) — governing Nepal code, especially §§3.2, 5.1–5.6, 7.3 and 9.3.
- [CTBUH Outrigger Design for High-Rise Buildings (2017), second edition preview](https://store.ctbuh.org/PDF_Previews/Books/2017_CTBUHOutriggerGuide_Preview.pdf) — outriggers, construction/shortening and damping design guidance, not Nepal statutory code or an optimum location.
- [PEER Guidelines for Performance-Based Seismic Design of Tall Buildings, 2017/06](https://peer.berkeley.edu/publications/2017-06) — performance-based research guidance, not a replacement for NBC.
- [OpenSees E-SFI MVLEM 3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html) and [ViscousDamper](https://openseespydoc.readthedocs.io/en/latest/src/ViscousDamper.html) — implemented element semantics, **not** automatic specimen validation.

**Remaining obligations:** actual ETABS source exports, structural analysis under matching loads and stiffness, source material calibration, full native converged record runs, member acceptance and independent licensed Nepal engineer review. No assertion of structural design approval, a completed full-code line audit, or optimum M0–M6 variant.
