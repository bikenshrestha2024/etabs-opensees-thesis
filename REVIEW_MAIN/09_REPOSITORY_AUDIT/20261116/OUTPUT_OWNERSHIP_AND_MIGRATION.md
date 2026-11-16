# Canonical output ownership and migration gates

Source of truth: `components/inputs/output_layout.py` and `components/inputs/output_contract.py`. This document **does not move any existing output file**. Moving a result is unsafe until every writer, manifest, reader, ZIP exporter and source-hash link has been verified.

## User-selected private project case layout

```text
<PRIVATE_CASE_ROOT>/
  00_SOURCE_MANIFEST/                # EDB hash, original source identity
  01_ETABS_EXPORT/                   # ETABS audit source + organized copies
    00_MANIFEST/
    REVIEW_SNAPSHOTS/
  02_MODEL/
    SLAB_LOAD_PATH/
      MESH_04/{CONFIGS,ASSEMBLED,EXCEL,JSON,...}
      MESH_08/{CONFIGS,ASSEMBLED,EXCEL,JSON,...}
      MESH_16/{CONFIGS,ASSEMBLED,EXCEL,JSON,...}
  02_GRAVITY/
  03_ESM/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
    VERIFICATION_STUDIO/
    <case-specific discrepancies and evidence>
```

For **new** stage cases, use `components.inputs.output_contract.create_case_run`: unique run ID, source SHA, model SHA, exact units and subfolders `00_INPUT_SOURCE/01_LOGS/02_RESULTS/03_EXCEL/04_FIGURES/05_COMPARISONS/06_REVIEW/07_EXPORT_ZIP`. Result status starts at CREATED/RUNNING and cannot become verified merely because files exist.

## Migration control ledger

| Producer / consumer | Current concern | Required gate before path changes |
| --- | --- | --- |
| ETABS source audit and visualization | Legacy flat CSV/JSON/HTML names still read by UI and conversion; 4-page viewers are large | Preserve flat authoritative output and SHA-verified categorized **copy** until every consumer follows the new index |
| Geometry and loads | `OpenSees_Complete_Model_Data_V118.json`, config SHA, manifest, section audit | All consumers use matching source/config hash; rerun native load equilibrium; never rely on filename alone |
| Slab mesh 04/08/16 | Independent full models; Excel formula export can be expensive | Distinct case folder and config SHA; no relabeling 04 as 08; full independent gravity & mesh convergence |
| Gravity 32/76/97 | Multiple support strategies and reaction mappings | Never cross-use support strategy results; compare full reaction vectors and solve status |
| ESM / MRSM | Generated NBC code inputs and Rayleigh/Aw sheets | Source-code version, source EDB and code table provenance; compare ETABS |
| LTH / NLTH | Trial vs complete history, XY/YX and state | No trial-to-full promotion; preserve solver log/traceback and results under unique case |
| Source literature | CSI/standards PDFs and papers may be restricted/private | Metadata/DOI/official links in public Git, files only where redistribution permitted |

## No-loss cleanup policy

The repository has **403 duplicate Git blob groups** (484 additional identical tracked files in the pinned discovery). This is a SHA-backed *inventory*, not authorization to delete archived examples or snapshots. If removal is proposed, provide the import/caller graph, manifest/ZIP readers, source hash, archive retention judgment and regression tests. The public code repository should not contain private project geometry, reaction exports or full copyrighted CSI manuals.

## Acceptance

`FOLDER_ORGANIZED` is a navigation status only. Never use it in place of `NATIVE_OPEN_SEES_PASS`, `ETABS_OPENSEES_EQUIVALENCE_VERIFIED`, `NBC_ACCEPTED` or `FULL_NLTHA_VALIDATED`.
