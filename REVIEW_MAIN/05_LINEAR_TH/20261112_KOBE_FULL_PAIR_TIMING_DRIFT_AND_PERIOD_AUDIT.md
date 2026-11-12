> **Load-purpose clarification (2026-11-12):** The different `GRAVITY_1.0D_1.0L` (~311,367 kN) and Kobe seismic `AS_CONFIGURED` (~286,420 kN) total loads are **intentionally different** because 100% live plus roof live is used for the gravity-only comparison, while NBC 105:2025 §5.2 Table 5-1 specifies seismic load participation D=1.0, storage live=0.6, other live=0.3, roof live=0.0. Do not flag the cross-purpose total difference as an error. Independent ETABS/OpenSees matching is required for **each corresponding load profile**. See [load-purpose guidance](../../07_REVIEW_MAIN/NBC105_2025_LOAD_CASE_PURPOSE_GUIDE.md).

# 2026-11-12 — Kobe complete XY/YX pair and native transient performance review

**Issue:** RV-LTH-003 (P0 performance bottleneck; P1 period provenance)  
**Research case:** `LTH_ULS_Trial_20261112_155716_817601`; record `RSN1120_KOBE_TAK000`; ULS; 3D paired orientations XY and YX.  
**Status:** `NUMERICALLY_COMPLETED_PAIR_PRELIMINARY` — **NOT** a completed eight-pair NBC accepted suite; no ETABS physical equivalence claimed.

**Supersedes:** [the same-day partial snapshot](../07_TIME_HISTORY/20261112_KOBE_LINEAR_PARTIAL_BATCH_AND_PERFORMANCE_REVIEW.md) that previously stated YX was still running. The new package contains complete YX evidence through 20:30:01 +05:45. Keep the historical partial review unmodified except for a supersession notice.

## Evidence inspected (private inputs are not committed)

- Two user-uploaded `Linear_Time_History_20261112_203217_192128.zip` and `Linear_Time_History_20261112_203246_895475.zip`, 36 members each. Both archives contain **identical uncompressed file contents** despite differing ZIP container hashes.
- Embedded `REVIEW_EVIDENCE_MANIFEST.json`: all **35 files** listed in its manifest were found and their **SHA-256 digests match**. One additional file is the manifest itself.
- `NBC105_Linear_Time_History_Summary_V115.json`, two `*_Performance_V133.json`, `Time_History_Case_Status_V151.json`, `Transient_Workload_V133.json`, motion input audit, full history CSVs, separate drift checks and edge drifts.
- Independent `Modal_Review_UPLOAD.zip`, `Comparisons_Review_UPLOAD(4).zip` and `Gravity_Review_UPLOAD(4).zip` were checked only for **targeted corroborating** modal/comparison gates. This is not a full certification of those modules.
- Archive member text includes private Windows source locations. Paths, user identifiers and source ground-motion bytes are **not copied** to this public issue.

## Measured timing and case completeness

| Metric | XY | YX |
|---|---:|---:|
| Case elapsed wall time (s) | 8040.212170 | 8323.841697 |
| Model/gravity (s) | 94.994843 | 97.366531 |
| Damping eigenanalysis (s) | 25.741712 | 26.146798 |
| Transient including recorder (s) | 7916.905298 | 8198.276596 |
| Measured recorder section (s) | 245.287957 | 252.942719 |
| Exports/drift (s) | 1.777711 | 1.187716 |
| Steps accepted/requested | 4094/4094 | 4094/4094 |
| First/last recorded time (s) | 0.01 / 40.94 | 0.01 / 40.94 |
| History fields / data rows | 184 / 4094 | 184 / 4094 |
| Nonfinite history entries | 0 | 0 |

**Combined pair elapsed:** 16,364.054 seconds = **4 h 32 min 44 s**, ~0.5004 accepted steps per wall second. The combined transient-with-recorder share is **98.479%**. Measured recording accounts for **3.045% of total wall time**; the difference between transient and the recorder timer is **15,616.951 seconds (~95.434%)**. This difference is a solver-plus-loop/step overhead approximation; the V133 output does **not** independently time native OpenSees `ops.analyze()`. Do not assign all difference to UMFPACK without the newer independent solve timer.

The gravity balance observed in the selected LTH log is 286,419.758231 kN applied versus support reactions and 76 source support nodes; this is a configured **D+0.3L-like** preload, **not** proof that the independent `GRAVITY_1.0D_1.0L` 311,367.313879 kN cases are equivalent. The sources represent different load combinations.

## Results: one pair, complete numerical record, ULS screening only

| Peak | XY | YX |
|---|---:|---:|
| Relative roof Ux (m) | 0.412960174 | 0.396808975 |
| Relative roof Uy (m) | 0.541469003 | 0.530284069 |
| Governing X floor-edge drift | 0.005660229 (0.5660%) | 0.005444168 (0.5444%) |
| Governing Y floor-edge drift | 0.007787399 (0.7787%) | 0.007428872 (0.7429%) |

ULS drift screen in these files is 0.025, and both values screen below that threshold. This **does not** establish a complete torsional edge drift, all-member force, ductility, load scaling or code acceptance. Do not apply the SLS 0.006 screen to this ULS-only response or claim these maxima are simultaneous in time. The screenshot's results browser includes exploratory-frame NL files; those 0.1-s assumed-material results are a **different diagnostic case** and must not enter the 40.94-s linear history aggregation.

Motion input verification: X min/max -0.26518/+0.23311 g; Y min/max -0.27669/+0.28105 g; each record 4,095 input samples at 0.01 s; motion scale 1.0 and g→m/s² conversion factor 9.80665. The input audit and saved selected path are mutually consistent **within this case**. Original SeismoMatch logs, Soil C Vs30 evidence and multi-pair scaling validation remain outstanding.

## Periods and model identity — material mismatch requiring review

- Configured LTH directional `T1_x=1.98128088503 s`, `T1_y=1.92197977671 s`.
- Independent 40-mode modal archive for the ULS model reports **mode 1 `2.38391397368 s` predominantly translation Y (UY effective mass 66.96%)** and **mode 2 `1.66393389569 s` predominantly translation X (UX effective mass 67.40%)**. Mode 3, `1.181815 s`, is torsion-dominated by the report's heuristic.
- Configured directional T1 values differ from those candidate mode periods by ~+19.1% (X) and ~−19.4% (Y), respectively. **Not a proven source-model mismatch yet**: confirm eigenvector character, EDB/model SHA, ULS stiffness state, and whether the T1 numbers are intentionally *adopted NBC code periods* rather than native eigen periods. Record both and stop silently substituting.
- The 40-mode modal archive reaches 91.245% cumulative UX and 90.775% UY, with threshold reached by modes 11 and 13. That is modal coverage evidence, not ETABS equivalence or nonlinear acceptance.
- The case's `Tn_x=0.16521657s` and `Tn_y=0.15393821s` align with the modal periods at 90% participation. The final integration step 0.01 s is controlled by digitization and the 0.01-s absolute cap in saved `Transient_Workload_V133.json`; a provenance correction to T1 alone does not explain the four-hour runtime.

## Cross-workstream evidence blockers

- Uploaded ETABS comparison package includes `NO_COMPARABLE_RESULTS.txt` with `ZERO_SOURCE_MATCHED_ROWS`. This confirms the direct code-to-code comparison is **not yet validated**, not that OpenSees response is zero.
- The 32/76/97 gravity comparison source flags `SOLVER_EQUILIBRIUM_ONLY_NOT_ETABS_EQUIVALENCE`. Its `GRAVITY_1.0D_1.0L` 311,367.314 kN load must not be compared directly to the LTH's 286,419.758 kN D+0.3L-like preload.
- Earlier X-direction core-wall first-step NLTHA remains an independent P0 blocker. A separate exploratory 0.1-s assumed-material frame history is **not** full building NLTHA validation.

## Optimization strategy — keep true physical equivalence

1. **Do not rerun full 4.5-hour pair as the first test.** Benchmark same single model and Kobe wave on a short but adequate chosen window; save run-to-run hashes and retain unchanged integration dt and full-resolution outputs in final acceptance tests.
2. Existing opt-in `linear_factor_once_experimental` uses OpenSees `algorithm('Linear','-factorOnce')`. Use **only if** independent element and damping inspection establishes a constant effective matrix, fixed Newmark time step and *physically elastic* elements. `Linear` by itself does not enforce elastic constitutive behavior, and without a test command OpenSees Linear does not perform a convergence criterion check.
3. Existing opt-in vector reaction path may reduce calls per sampled support, but only ~3% wall time is measured for recorder processing; expect no guaranteed large speedup from this alone. Verify signs and all six DOFs at every sample.
4. Newer instrumentation logs `native_solve_seconds` separately from recorder and transient; benchmark `baseline`, `recorder_vector_only`, `factorOnce_only`, then `both` **only after elasticity verification**. Compare all roof/floor, edge drift and base-shear histories at equal time and model SHA; fail closed if discrepancies exceed prespecified absolute/relative tolerances.
5. Do not delete or coarsen accepted history rows to improve speed; plotting may use extrema-preserving decimation but original data must remain.
6. Never assume a fixed linear→nonlinear multiplier: nonlinear subiterations and wall convergence vary by case. A 224-run *planned* matrix is not a completed suite.

## GUI reproducibility action

The current `components/ui/history_inspection.py` recursively scans all nearby folders, so linear histories, exploratory NL records and old logs can be presented in one selector. This review adds an explicit run-scope filter that selects the appropriate latest LTH subfolder by default when available, labels mixed scopes and reuses a single file inventory per manual refresh. **Native Windows UI behavior pending local test.** This change affects evidence navigation only.

## Primary sources

- OpenSees Linear algorithm, no convergence test, and `-factorOnce` requirement: https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html
- OpenSees Rayleigh committed stiffness terms: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html
- OpenSees reactions: https://openseespydoc.readthedocs.io/en/latest/src/reactions.html
- OpenSeesPy nodal reactions: https://openseespydoc.readthedocs.io/en/latest/src/nodeReaction.html

**Owner:** Thesis operator supplies unchanged source inputs and native tests; structural/earthquake reviewer signs off on accepted demand and NBC provisions; software maintainer verifies UI, timing reports and CI. No automatic approval has been added.
