# 2026-11-14 source-matched Gravity / V142 / stiffness / folder review

## User-observed symptoms
1. Real 1D+1L gravity run **still writes directly** under `<export>/OpenSees_Analysis_Results/<ULS-case>/Gravity_Reaction_Diagnostic/<timestamp>` and only later creates **copies** beneath `<export>/02_GRAVITY/REVIEW_SNAPSHOTS/<timestamp>`. This is the current and incomplete *writer migration*. Do not describe snapshots as new solver case destination.
2. About 145 flat export-root files (JSON, CSV, Excel, Python, HTML and processing sidecars) remain visible despite categorized mirror under `01_ETABS_EXPORT`. Mirror is deliberately non-destructive because active consumers still depend on flat files. **NEVER recursively move/delete these or edit original EDB/Excel without consumer migration and hash verification.**
3. V116 launcher Step 13 source table showed conventional RC slab 0.25/0.35 as “supplemental comparison” despite adopted project source/requirements in root AGENTS.md. Updated GUI to say **REQUIRED PROJECT ANALYSIS BASIS**, retain IS 16700:2023 Table 5 source, avoid mislabelling this as an NBC slab provision, preserve membrane/weight and nonlinear laws. This is a displayed policy update, **not yet physical solver stiffness confirmation**.
4. V142 blank ULS/SLS drift and deflection screenshot explicitly reported **0 saved drift rows, 0 saved deflection rows**. V142 originally scanned only one fixed legacy path and quietly drew empty Matplotlib axes. Updated scan searches legacy and staged result directories and emits `NO_SAVED_SEISMIC_DRIFT` / `NO_SAVED_LATERAL_DEFLECTION` evidence with searched paths. Gravity or initial P-Delta runs do **not** automatically produce ULS/SLS seismic drift time histories. If the selected export has no saved compatible seismic response this remains expected; no fake plot.

## Actual native evidence from current model
- Original user run uses `Verified_Clear_Beam_20261114_153722_428087`, diagnostic **32 support nodes**, 10 load steps, 1.0D+1.0L, downward force/reaction **311367.31387955 kN**, equilibrium relative error **1.86942e-14%**, largest gravity Uz **-0.02101765 m**. It is numerical equilibrium, not ETABS parity.
- ETABS reported vertical reaction **311367.313600 kN**; difference **0.000280 kN**. Source-to-source total already agrees to roundoff.
- Native ETABS to OpenSees **per-support reactions do not**: ETABS point 263 / OpenSees node 36 differs by about **3041.266 kN**, and 44 additional ETABS support entries are unmatched in the 32-case. Source model has several mismatched supports and shell-wall interfaces. Case is `NOT_STRUCTURALLY_VALIDATED`. Investigate base restraint equivalent nodes/DOFs and wall/beam/slab stiffness/connectivity; **do not shift gravity totals or apply corrections to force a match**.
- The current review log reports native assignment beam count 750 and source structural weights, but joint-overlap candidates 19358.527 kN and beam-offset candidates 8652.444 kN are **mutually exclusive unvalidated hypotheses**, not automatic adjustments.
- Uploaded V03/V04/evidence ZIP archives require exact byte/hashes and deeper native file comparison; screenshots plus textual logs do not establish every archived entry's contents.

## Canonical new gravity write root (implemented at GUI input boundary; other stages still pending)
```text
<export>/01_ETABS_EXPORT/{00_MANIFEST,01_SOURCE,02_MAPPING,03_LOADS,04_VISUALIZATION,05_AUDITS,06_CONFIG,07_LOGS,08_PROCESSING,09_REVIEW}/
<export>/02_GRAVITY/
  RUNS/<timestamp>/{SOURCE_SNAPSHOT,MODEL_INPUT,LOGS,RESULTS,FIGURES,AUDITS,COMPARISONS,ZIP_EXPORTS}/
  REVIEW_SNAPSHOTS/<timestamp>/{Gravity,Comparisons,ZIP_Exports,manifest}/
  LATEST_GRAVITY_RUN.json
<export>/03_ESM/... etc.
```
Need migrate **every gravity producer AND consumer** (GUI output_var initialization, `_selected_result_path`, subprocess runner, PDF/plots, registry, direct ETABS comparison, support audit, ZIP writer and latest-pointer logic), with dual-read legacy fallback and native Windows tests before changing actual writer. Do not simply move outputs after save: stale paths inside manifests/ZIP/registry are an engineering evidence hazard. No source files moved in PR.

## Source-guided next tests
- Run a source-matched 76-node case with ETABS restraint DOF, wall auto-edge constraints and reaction vector comparison; preserve 32 and 97 as explicit diagnostics.
- Compare wall/slab shell stiffness and connection actions, conventional slab `0.25 Ig/0.35 Ig` ULS/SLS, mass and physical thickness independently.
- Execute a finished ULS/SLS ESM or MRSM and confirm *saved case-specific* `Drift_Check_`, `Floor_Edge_Drift_`, `MRSM_Results_V132.json` or `Deformation_*.json` is present, accurately identified and decoded by V142. Initial P-Delta verification has separate load cases and does not automatically populate seismic drift.
- Verify loaded local runtime path and newest commit. The launcher title `V116` may be legacy even when GitHub source updates.

**No code/physical pass claimed:** This patch fixes source basis wording and V142 evidence discovery/empty-state, not individual reaction redistribution or a complete gravity-writer migration.


## Current code behavior — 02_GRAVITY routing (new runs)
`components.inputs.output_layout.canonical_gravity_run_root()` redirects **only** selected output paths beneath `<export>/OpenSees_Analysis_Results/<case>` to `<export>/02_GRAVITY/RUNS/<case>`. The gravity GUI's `_inputs` stores that canonical path back into its shared `output_var` before creating a new case/registry; its subsequent solver thread, diagnostic plots, direct comparison and evidence packager all reference this runtime variable. Legacy paths remain unchanged on disk. Custom external output paths and already canonical gravity stage roots are preserved; no copying/removal or rehash of existing results occurs.

This is a **new-run writer-path change**, not a completed repository-wide consumer migration. Always smoke-test 32, 76 and 97 scenarios, direct ETABS comparison, subsequent OpenSees result selection and ZIP paths on Windows with a source-identical model; a verified native run has not been completed in this PR. The stage index is navigation-only. For old runs, manually choose the old folder in result browsers rather than running another analysis to create categorized copies.
