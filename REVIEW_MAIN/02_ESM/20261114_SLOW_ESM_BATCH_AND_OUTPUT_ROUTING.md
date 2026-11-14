# ESM November 14, 2026: batch timing, folder ownership, partial export

**Status:** PARTIAL SOFTWARE FIX, ENGINEERING VALIDATION NOT ESTABLISHED.
Source evidence: uploaded `GUI_Run_OpenSees_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E+_V111.log`, two stage processing JSON, `CASE_STATUS.json`, `ESM_Export_Manifest.json`, workbook names, and 11:23–11:25 UI screenshots.

## Evidence and diagnosis
- Six X/Y ±eccentricity/centered runner files were generated, with separately calculated ULS X base shear 25659.046 kN, Y 26450.735 kN. Code flags ULS ESM **COMPARISON ONLY** for this high-rise under NBC §3.2.1; site Vs30 for >40 m remains NOT VERIFIED.
- First `ULS_X+_E+` runner returned code 0 in **889.734 s** (~14.83 min). **753.444 s** spent on four independent signed initial IS 16700 P-Delta checks; model+gravity after checks **84.343 s**; ESM solver total ~888.763 s. It is misleading to label whole 889 s as a single ESM solve. The second `ULS_X+_E-` was reported SUCCESS at 139.203 s in GUI; do not infer all six complete from that.
- Initial signed checks `PD_INIT_EL_X_PLUS/MINUS`, `PD_INIT_EL_Y_PLUS/MINUS` converged; each repeats gravity 350423.709877 kN with 76 `ETABS_SOURCE_SUPPORTS` nodes, but ESM final sustained `AS_CONFIGURED` gravity was 286419.758231 kN. These different loading states must **not** be conflated; signed-case convergence is not ETABS tangent-stiffness equivalence.
- User-uploaded `CASE_STATUS.json` holds only one `SUCCESS` record; batch was still in progress when combined ZIP/Excel was exported. Manifest contains calculated `NBC105_ESM_Calculation_*.json`, plots, CSV, XLSX and script artefacts for multiple cases even if those cases were not solved. This is a **partial review snapshot**, not an empty ESM folder nor six validated solver results.
- The old exporter copied `*.processing.json` sidecars as ordinary ESM JSON, then wrote review ZIP under nested `OpenSees_Analysis_Results/<model>/ESM_Organized`. It did not correlate the snapshot with a `CASE_STATUS.json`.

## Software change on PR #45
- Retain the legacy active result paths and generated scripts. New combined **review copies** are written to `<ETABS export>/03_ESM/REVIEW_SNAPSHOTS/<timestamp>/`. The full ZIP, Excel, manifest and direct versus ETABS-linked names remain separate.
- Exclude `*.processing.json` from evidence snapshot; retain stage timing in original log/JSON.
- Parse the latest batch `ESM_Runner_Status/*/CASE_STATUS.json` and include `Solver Batch Status` sheet and manifest `solver_batch/snapshot_status`. If not all expected runner scripts have `SUCCESS, return_code=0`, status is **PARTIAL_OR_UNVERIFIED**.
- Explicitly explain incomplete snapshots in GUI. No engineering acceptance is asserted. Previous snapshot paths are unchanged, and the current running batch is not interrupted.

## Existing initial-check cache and remaining runtime optimization
1. Instrument each signed initial static check by model construction, gravity steps, solver matrix symbolic/numeric factorization, and lateral convergence; keep native EDB / model / stiffness hashes and per-case logs. Distinguish **cold-cache first case** from **warm-cache subsequent cases** when benchmarking.
2. **ALREADY IMPLEMENTED:** `components/model/initial_pdelta.py::ensure_initial_checks()` hashes complete model data/config, initial P-Delta input and relevant implementation source bytes and reuses `OpenSees_IS16700_Initial_PDelta_Results.json` only when all four signed cases are present, converged, and carry the matching input digest. This plausibly explains why the first case took 889.734 s and the second only 139.203 s; verify the second log explicitly contains `IS 16700: reusing four converged cases with matching input fingerprints.` The cache is numerical evidence reuse **not a copied nonlinear OpenSees domain or stiffness state**. Its source-identity coverage and atomic writes should be separately audited before engineering qualification.
3. Each actual ESM response still requires its own correct gravity state and signed lateral run; cannot bypass P-Delta or stitch analysis state across processes by copying a JSON result. OpenSees `wipeAnalysis` clears solver objects but retains model states and current loads; `loadConst` freezes defined load patterns only. A fresh independently isolated solver domain is required unless state management is explicitly proven.
4. Cache common *read-only inputs* (periods, spectrum, story weights, source tables) keyed by content hash and avoid redundant Excel/ZIP work during live batch; persist status and support cancellation. Do not parallelize six expensive processes by default because sparse factorization is memory-intensive.
5. Perform native Windows timing benchmark and verify equivalence of resulting base shear, reactions, drifts, energy/forces and code flags against unoptimized baseline.

## Required canonical layout (future full migration)
```text
<ETABS export>/
  01_ETABS_EXPORT/
  02_GRAVITY/
  03_ESM/
    INPUTS_AND_PROVENANCE/
    PRELIMINARY_RAYLEIGH/
    RUNS/ULS/{Xplus_Eplus,Xplus_Eminus,Xplus_E0,Yplus_Eplus,Yplus_Eminus,Yplus_E0}/
    RESULTS/{CSV,EXCEL,JSON,PLOTS}/
    ETABS_COMPARISON/
    REVIEW_SNAPSHOTS/<timestamp>/{ETABS_Linked_Equivalent_Static,OpenSees_Direct_Equivalent_Static,ZIP,...}
    LOGS_AND_STATUS/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  REVIEW_MAIN/
```
This patch establishes only the **ESM snapshot** path; migration of generated scripts and solver output producers/readers to the canonical model is not complete. Preserve `OpenSees_Analysis_Results` old paths until all references and hash-provenance tests pass.

**OpenSees references:** https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/wipeAnalysis.html and https://openseespydoc.readthedocs.io/en/stable/src/loadConst.html.
