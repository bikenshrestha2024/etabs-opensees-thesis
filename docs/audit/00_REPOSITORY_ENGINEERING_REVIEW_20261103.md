# 00 — Repository-wide engineering audit and thesis improvement plan

**Baseline branch:** `main` at `d00770cb33f2d40ad00fcec2ea59bcb6d8a05687` (2026-11-03). **Enumerated files:** 1628. **Approx. tracked blob bytes:** 490,787,260 (includes duplicate Git blobs and old generated outputs).

## Scope and honesty of evidence

Every tracked file in the baseline tree has one row in [`00_ALL_FILES_AUDIT.tsv`](00_ALL_FILES_AUDIT.tsv), including its original path, Git blob SHA, size, functional category, engineering priority and recommended next action. **This is not a claim that the contents of all 1628 files have been individually opened or numerically tested.** The 84 active `components/**/*.py` modules were retrieved and static-screened; a smaller set of nonlinear/assembly/performance modules received targeted implementation review. Other files were inventoried by path, SHA and size. Native ETABS/OpenSees execution and numerical validation have not been performed here.

## Engineering findings, severity ranked

### P0 — Thesis blockers

1. **Incomplete nonlinear RC calibration:** `components/nonlinear_time_history/research_building_materials.py` uses research nominal frame cover/core Concrete01 parameters, nominal Fe500 Steel02 and pre-existing section bar-layout templates, which the code explicitly says are not verified against the project bar schedules. Wall FSAM material properties are assigned per wall property, currently with the same material laws and a two-curtain bar pattern, not actual axial load/boundary reinforcement regions. Reconcile geometry, transverse confinement, hoop spacing, section taper, wall boundary cages, and actual ETABS bar schedules before physical claims.
2. **Known first-step wall instability:** V168 tests showed ZERO excitation pass but Kobe X-only fail at the first 0.005-s increment. Nonfinite post-failure force was observed in solver tags 110280 (`AREA:354`) and 112778 (`AREA:482`), slender X-Z wall panels in the first-story height range. The affected element tags are not proven root causes. Audit DOF constraints, wall node winding, FSAM local axes/relative axes, model mass, tangent stiffness, material input units and pre-failure response; run a single-panel forced-displacement test before the full building.
3. **Wall opening / core mechanics:** `components/model/assembly.py` builds E_SFI_MVLEM_3D per mapped wall quad, with constant FSAM property across each panel and elastic ShellMITC4 floors. Verify openings, coupling beams, junction compatibility, wall-to-outrigger forces and core 3D torsional response. Do not treat planar wall benchmarks as sufficient evidence for a nonlinear 3D asymmetric core.
4. **Device completeness:** `components/sections/devices.py` provides axial Maxwell ViscousDamper links and simple Steel02 corotTruss BRB core elements, with guarded activation. Actual damper spring K, viscous coefficient Cd and alpha, connection stiffness, orientation, stroke and force limits must be calibrated; BRB core and connections need compressive overstrength and cyclic cumulative ductility/fatigue criteria. Nonlinear normal ordinary braces are simplified Steel01 corotTruss, which do **not** capture buckling, connection flexure or low-cycle fatigue.
5. **Performance-data interoperability:** `components/nonlinear_time_history/building_exploratory.py` generates `COMPLETED_EXPLORATORY_RECORD`, while `components/validation/nonlinear_performance.py` accepts only `COMPLETED_FULL_RECORD`. This status-schema discrepancy blocks direct assessment, even for a physically complete exploratory run. Do not simply relax the gate: define a trusted evidence-promotion process after numerical, physical and completeness checks.
6. **Structural research variants:** The full M0–M6 matrix (no outrigger; conventional; damped; belt; cap), 3/5/7/9/11 elevation candidates, ULS/SLS, both ground-motion orientations and ±5% eccentricities needs a versioned model-change matrix with identical mass, geometry, material profiles and performance output names. Do not compare options until each complete case passes the same verification gates.

### P1 — Analysis reliability and standards

7. **Modal and RSA:** `components/shared/eigen_solver.py` protects against large dense solves and uses PythonSparse fallback but native `ops.eigen()` may remain a blocking call. Use a separate subprocess to enable termination and preserve `stderr`, case provenance and modal residual/participation checks.
8. **Gravity and export:** Audit `components/model/assembly.py`, `components/gravity/solver_stack.py`, `components/model/load_and_diaphragm_audit.py` and modal/RSA runtime fingerprints against ETABS. Avoid running stale V156 assembly copies. Verify reaction/load balance, lateral modes, mass sources, rigid diaphragms, support constraints, accidental torsion and equivalent section stiffness.
9. **NBC 105:2025 interpretation:** Section 5.5.3 establishes 0.025 ULS and 0.006 SLS drift ratios; 9.3.3.1 refers to 5.6, which describes accidental eccentricity rather than drift. `components/validation/nonlinear_performance.py` notes the cross-reference problem and correctly requires separately reviewed member/device limits; preserve that warning and obtain an authoritative code interpretation before regulatory claims.
10. **Time-history evidence:** Record digitization dt, applied integration dt, physical duration, scale and target spectrum compatibility; do not use a truncated trial or successful short probe as a full earthquake. Distinguish SLS and ULS ground motions and analyze XY/YX. Every failed, cancelled or nonfinite case must be excluded from comparisons, with full logs and fresh domains.
11. **Material transfer:** `components/nonlinear_time_history/research_building_materials.py` contains a PEER wall profile with selectably different SteelMPF transition factors; sensitivity is not validation. Run measured cyclic benchmarks for ConcreteCM/SteelMPF/FSAM, confined/unconfined Concrete01/02, Steel02, FVD and BRB separately; retain calibrated versus nominal profiles and uncertainties.
12. **Software structure:** `components/ui/application.py` is over 3,000 lines; split into controllers and tab-specific modules behind regression tests. `components/equivalent_static/calculation_and_gui.py` contains explicit working-directory changes and suppressed exceptions; make paths explicit and log exceptions. `components/validation/wall_validation.py` uses restricted `exec(compile(...))`; audit all sources and avoid dynamic execution of untrusted model configurations.
13. **Cross-program regression:** Existing `tests/` has 27 tracked test/fixture files, but only the new NLTHA quality test has an explicit narrow GitHub Actions workflow. Run full offline tests on Python 3.12/Spyder/conda-forge and separate native OpenSeesPy/XARA wall/solver smoke tests; never silently skip unavailable native features.

### P2 — Repository hygiene and reproducibility

14. Root still holds both new numbered launchers and old compatibility aliases. Clearly mark old names deprecated; do not rename importable modules mechanically. `Saved_Project_V156/` contributes 530 tracked files and should be frozen as a historical baseline rather than confused with active source.
15. Many `Worked_Example_*`, `Verification_*`, saved HTML previews, plots, histories and manifest versions remain in Git. Keep published evidence but move future heavy generated runs to immutable results archives with commit SHA, input hashes, model ID, record ID and exact solver version. Large current blobs include: Saved_Project_V156/OpenSees_Complete_Model_Data_V118.json (42.7 MiB); Worked_Example_V132/MRSM_SLS/SLS_X_E0_Element_Force_Envelopes_V132.csv (18.7 MiB); Worked_Example_V132/MRSM_ULS/ULS_X_E0_Element_Force_Envelopes_V132.csv (18.6 MiB); Worked_Example_V132/MRSM_SLS/SLS_X_Eplus_Element_Force_Envelopes_V132.csv (18.6 MiB); Worked_Example_V132/MRSM_SLS/SLS_X_Eminus_Element_Force_Envelopes_V132.csv (18.6 MiB).
16. The project needs one authoritative `model_manifest.json` covering M0–M6, geometry, load mass, nonlinear section cards, source ETABS export, steel brace/damper devices, ground motions and analysis case matrix. Version source paper DOI, actual specimen, tested axial loading and calibrated parameters separately.
17. Every launcher needs input schema, output schema, failure reports, reproducibility instructions, a validation level, and a passing test. Documentation-only changes must not be labeled numerical verification.

## Evidence from user-supplied papers — suggested benchmark registry (not reproduced experiments)

- **Kolozvari, Orakcal & Wallace (2018):** MVLEM, SFI-MVLEM, FSAM, ConcreteCM and SteelMPF formulation and specimen-based checks for shear-flexure coupling.
- **Ji et al. (2023), DOI 10.1002/eqe.4060:** T-shaped walls at axial compression ratio ~0.19 with experimental cyclic data; three model families compared. Geometry and axial load must be reconstructed before use.
- **Ji, Cheng & Xu (2018):** coupled axial tension–shear tests show major strength/stiffness effects under tension; compare with story-wise wall axial-load histories.
- **Rezapour et al. (2026), DOI 10.1007/s10518-025-02353-0:** macro-modeling for coupled RC walls with asymmetric openings; methodological candidate for core openings/coupling beams.
- **Tura et al. (2026), DOI 10.1007/s10518-025-02165-2:** LFSAFE layered shell experimental validation for U/H shape walls under lateral and torsional loading; investigate as a *separate model-form alternative*, not an interchangeable E-SFI material card.
- **Guerrero Bobadilla et al. (2025), SDEE 199, 109700:** BRB cumulative ductility/fatigue protocol and cyclic energy.
- **Cao et al. (2024):** out-of-plane eccentricity in BRB experimental tests—relevant for offset outrigger connections.
- **Özkaya & Gürbüz (2026), DOI 10.1007/s10518-026-02428-6:** irregular composite building FVD placement; placement comparison informs the study design but numerical improvements cannot be transferred to this RC model.
- **Yousefi & Tehrani (2026):** RC frame-wall IDA and SFSI sensitivity; optional later sensitivity after fixed-base baseline converges.

## Recommended implementation queue

| Queue | Gate | Required test |
|---|---|---|
| 01 | Fix failed X-only wall transient | ZERO/X/Y/XY isolated probes + clean wall panel cycle |
| 02 | Verify actual ETABS model inputs | geometry/load/mass/section/rebar/core opening reconciliation |
| 03 | Experimentally benchmark material and wall components | overlay loops, peak strength, stiffness, energy, strain, sensitivity |
| 04 | Verify full M0 frame/core baseline | full Kobe record X/Y and XY/YX, dt halving, energy balance |
| 05 | Add outrigger variants M1–M6 | reproducible geometry/device ID and response equivalence checks |
| 06 | Validate FVD/BRB | force-velocity-stroke-energy, low-cycle fatigue, axial demand |
| 07 | Full hazard suite | >=3 paired motions minimum for torsional sensitivity, ideally larger justified suite |
| 08 | Performance and thesis evidence | peak/edge drifts, roof torsion, acceleration, energy, axial/flexural/shear demands, residuals |

### Inventory classification counts

- HISTORICAL_SNAPSHOT: 530
- EVIDENCE_OUTPUT: 503
- DOCUMENTATION: 122
- COMPONENT_RESEARCH: 109
- ACTIVE_PYTHON_SOURCE: 84
- MANIFEST_OR_CONFIG: 65
- LEGACY_OR_FACADE_PYTHON: 65
- WORKFLOW_LAUNCHER: 41
- TEST_OR_FIXTURE: 27
- STEEL02_CALIBRATION: 18
- MATERIAL_CARD: 18
- GROUND_MOTION_RECORD: 16
- DATA_OR_TABLE: 13
- OTHER_ASSET: 7
- PLOT_REPORT_OR_LOG: 7
- INPUT_WORKBOOK: 3

**Exact Git blob-duplicate groups identified by metadata:** 431. Exact duplicates are not automatically safe to delete: multiple paths may be needed by archived model scripts and reproduced results.

## Limitations

No native OpenSeesPy/ETABS full model run, independent wall specimen replication, numerical regression suite or complete reading of every historical data file was conducted during this audit. The TSV explicitly distinguishes active Python files statically screened from other files only inventoried. The attached PDF papers were reviewed for research direction and benchmark relevance, not exhaustively digitized/calibrated. Never mark model results experimentally validated solely based on this report.
