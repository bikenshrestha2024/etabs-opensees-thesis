# 2026-11-22: 12 m X-wall clear-beam model variant and source workbook ownership

## Current source evidence

User screenshot shows sibling `Verified_Clear_Beam_20261121_110844_376039` next to ETABS export `1`. The prior rebuild intentionally refused any descendant target in order to protect the original export; its GUI therefore created a sibling folder. The variant contains 65 or more model root artifacts plus a copied `excel/source` containing three historical NBC calculator/scaling workbooks. **File presence does not establish that their Aw, period or source EDB refer to today's 2 x 12 m wall model.**

User supplied filenames in conversation:
- `NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7(3).xlsx` — proposed CURRENT model-specific calculation reference; this is a *candidate*, not a checked source hash or complete code acceptance.
- `Analysis Export ULS 3 storey latest_compressed(2).xlsx` — proposed source ETABS analysis tables.
- `Beam Forces Element 1 latest(2).xlsx`, `Beam Forces Element 2 latest(1).xlsx`, `Beam Forces Element 3 latest(1).xlsx` — proposed ETABS beam force outputs.

The external files are NOT committed to GitHub and were not inspected or ingested as solver calculations by this code change. A filename cannot establish sheet contents or native EDB identity. Preserve these in the user's private, source-hash-verified ETABS export registration before use.

## New folder policy

```text
ETABS 11-21-2026/
  1/                             <-- original source export, unchanged
    00_SOURCE_MANIFEST/          <-- EDB context and source identity
    01_ETABS_EXPORT/             <-- original exported native evidence
    02_MODEL/
      REBUILDS/
        VERIFIED_CLEAR_BEAM/
          <UTC unique timestamp>/
            00_SOURCE_MANIFEST/  <-- immutable rebuilt source EDB SHA reference
            00_PROCESSING_METADATA/
            02_MODEL/
            OpenSees_Complete_Gravity_Model.py  <-- compatibility builder entry
            OpenSees_Complete_Model_Config_V118.json
            CLEAR_BEAM_REBUILD_STATUS.json
            <other source-dependent compatibility artifacts>
    02_GRAVITY/                  <-- native gravity runs and comparisons
    03_ESM/                      <-- ESM derived from verified source model
    04_MODAL/
    05_MRSM/
    06_LINEAR_TIME_HISTORY/
    07_NONLINEAR_TIME_HISTORY/
    08_ETABS_COMPARISONS/
    09_SOFTWARE_DIAGNOSTICS/
```

Only the reserved `02_MODEL/REBUILDS/VERIFIED_CLEAR_BEAM/<unique>` descendant is permitted. Arbitrary writes into the ETABS source root or `excel/source` are blocked. A compatible builder still needs its original `*.json` lookup locations; moving those bytes prematurely would break model consumers. No legacy `Verified_Clear_Beam_...` directory is deleted or silently merged.

## Mandatory 12 m source geometry gate

The corrected model is **not accepted for reference use** until `verify_thesis_two_12m_wall_geometry` verifies rebuilt first-storey *actual shell/node geometry*: height 95 m, first storey 3.8 m, exactly two 12 m X wall planes with two 2 m ground-floor openings each and reconnection above 2.3 m, three 6 m solid Y wall planes, and 0.6 m thickness. It records export-geometry evidence and labels the status `EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY`, explicitly not a native ETABS EDB or NBC acceptance.

A rebuilt variant's `require_model_aligned_workbooks` config prevents old repository-global `CALCULATOR`/`SCALING`/`SERVICE_SCALING` source names from being automatically copied or resolved. Legacy Aw is not used as fallback when current geometry verification fails. Its historical files can remain for comparison in the original export; `excel/source` existence is not a verified current model.

**Important:** this branch does not yet register or parse the newly uploaded V10.7 workbook. It must be checked for actual content, formula caches, source EDB SHA, state, case, wall areas, and wall opening handling. Beam-force tables also require source load-case, element mapping and units checks.

## Engineering and release gates

Native Windows rebuild, current source EDB hashing, actual user-uploaded workbook inspection, ULS/SLS 12 m Ao/period replay, 32/76/97 ETABS/OpenSees six-DOF support reactions, and nonlinear X-wall convergence are outstanding. No files on the user's D: drive are moved by these GitHub changes, and no native calculation is claimed complete.
