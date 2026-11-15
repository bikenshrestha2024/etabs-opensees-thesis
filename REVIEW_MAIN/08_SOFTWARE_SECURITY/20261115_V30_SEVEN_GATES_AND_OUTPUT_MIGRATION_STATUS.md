# V30 — actual source review scope, output consistency and seven engineering gates

Date: 2026-11-15. Base SHA `32bfc5956b6c358d32c3d1cfb87ccb63fe30fdae`. Starting tracked Git tree: **3,006 blobs** (inventory only; not 3,006 semantic audits).
Review baseline: inspected `AGENTS.md`, canonical engineering rules, `engineering/migration/README.md`, active numbered launcher index, V135 guide and source functions, output contract and the corresponding existing tests. Changed only active source implementations and existing tests; no historical frozen runtime clone was moved.

## Software corrections actually committed

- Numeric superposition output can no longer silently publish Inf from individually finite signed first-order components.
- Finite demand and finite capacity do not automatically imply finite computed utilization. Overflow records `NOT EVALUATED`, clears its nonfinite utilization and prevents poisoned JSON/CSV reports.
- Nonfinite *computed* saved CSV or MRSM design drift ratios now reject an entire source file even if raw drift numbers were finite.
- V135 selected serialized model fingerprint and parsed JSON now use the exact same file byte snapshot.
- V135 user-edited canonical/legacy criteria files are refused when symlinked; those inputs remain untouched. Historic CSV and output readers are preserved.

## Seven requirements — unchanged acceptance boundaries

| Requirement | V30 work | Still needed |
|---|---|---|
| 1. Every tracked file semantic audit | Exact active source function review, test and Git blob ledger | **OPEN**: systematic code/caller review of remaining 3,006 baseline blobs |
| 2. Full writer/reader migration | Hardened V135 numeric writer/reader and input provenance, maintained V29 index | **OPEN**: all other legacy producers, Excel/ZIP writers, GUI consumers and atomic multi-file publication |
| 3. Windows interactive GUI | No native UI session used | **OPEN**: scroll/cancel/copy/export/open and ETABS OAPI interaction |
| 4. X-wall nonlinear first-step | Unchanged source solver/material parameters | **OPEN**: native element 110280, last accepted state, first-step evidence and diagnosis |
| 5. 32/76/97 supports | No physical supports modified | **OPEN**: native source six-DOF constraints, reactions and wall mesh mapping |
| 6. ETABS–OpenSees equivalence | Source hash and numeric report integrity improved | **OPEN**: actual geometry/mass/stiffness/gravity/modal/drift benchmark |
| 7. Full-duration sensitivity | No native M0–M6 XY/YX analyses run | **OPEN**: all 224 full-record runs and calibrated sensitivity cases |

## Folder hierarchy

Original source EDB and authoritative Excel workbooks belong to the selected local export, not this public GitHub review. Maintain stages `00_SOURCE_MANIFEST`, `01_ETABS_EXPORT`, `02_MODEL`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`, `REVIEW_MAIN`. Newly migrated cases use `RUNS/<STATE>/<CASE>/<RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`. Existing `OpenSees_Analysis_Results` readers stay compatible until coordinated migration.

The source-level Python checks cannot establish structural adequacy, seismic code acceptance or actual native solver convergence.
