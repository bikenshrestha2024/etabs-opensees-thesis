# 2026-11-21 Gravity folder duplication: root-cause and code corrections

**Evidence:** Four user-supplied Windows Explorer screenshots (local evidence, not downloaded into GitHub). ETABS export case `D:\Thesis Opensees\ETABS 11-21-2026\1`.

## Screenshot-by-screenshot root cause

1. `OpenSees_Analysis_Results/ULS_Floor_3_...`: a historical shared output case containing `Gravity_Case_Comparison`, `Gravity_Evidence_Upload`, `Gravity_Native_Equivalence_Preflight`, `Gravity_Reaction_Diagnostic`, `Gravity_Wall_Base_Comparison`, and flat `Gravity_GUI_Actions.log`, `Gravity_Output_Index.txt`, `LATEST_GRAVITY_UPLOAD.txt`. This location wrongly mixes runtime files, reviews and packaging.
2. `02_GRAVITY/`: contains support-strategy folders in addition to `RUNS` and `REVIEW_SNAPSHOTS`. The old `publish_gravity_case_index` created one extra preview folder per case and copied PNGs, despite full results already existing elsewhere.
3. `02_GRAVITY/REVIEW_SNAPSHOTS/<timestamp>/`: previously generated extracted `Gravity`, `Comparisons` plus `ZIP_Exports`. This deliberately duplicated the evidence in the ZIP as unpacked files and created multiple overlapping archive bundles.
4. `Gravity_Reaction_Diagnostic/<timestamp>/`: about 50 mixed outputs under a timestamped 32-node diagnostic, including reports, workbooks, plots and source metadata. This is an independent 32-support case, NOT a duplicate of the original 76-restraint or 97-restraint sensitivity models.

## New future write policy

```text
<ETABS selected export>/
  02_GRAVITY/
    RUNS/
      <selected gravity builder name>/
        00_INDEXES/
          Gravity_Case_Reaction_Index.json
          Gravity_Output_Index.txt
          LATEST_GRAVITY_UPLOAD.txt
        01_LOGS/
          Gravity_GUI_Actions.log
        02_RESULTS/
          ETABS_NONZERO_REACTION_DIAGNOSTIC/
            <gravity profile>/<unique timestamp>/
              Gravity_Result_V110.json
              Gravity_Run_V110.log
              Gravity_Results_V110.xlsx
              <case-specific plots and audits>
          ETABS_SOURCE_SUPPORTS/
            <gravity profile>/<unique timestamp>/<full solver case>
          CONTINUOUS_WALL_BASE_FIXED/
            <gravity profile>/<unique timestamp>/<full solver case>
        05_COMPARISONS/
          Gravity_Wall_Base_Comparison/<unique timestamp>/
          Gravity_Case_Comparison/<unique timestamp>/
        06_REVIEW/
          Gravity_Native_Equivalence_Preflight/<unique timestamp>/
        07_EXPORT_ZIP/
          Gravity_Evidence_Upload/<versioned package>/
    00_INDEXES/
      CASES/<support strategy>/<result-path-hash>.json
      LATEST_GRAVITY_CASES.json
    REVIEW_SNAPSHOTS/
      <timestamp>/
        EVIDENCE_MANIFEST.json
        README_FIRST.txt
        ZIP_Exports/GRAVITY_REVIEW_Review_UPLOAD.zip
```

**Two index levels are intentional:** `RUNS/<builder>/00_INDEXES` is the model/workspace authoritative registry; `02_GRAVITY/00_INDEXES/CASES` holds tiny cross-run navigation pointers for discovery, *without* duplicating PNGs, Excel or solver JSON. Registry and pointer are metadata; neither is a second solved model.

## Changes / provenance

- All new 32/76/97 single gravity runs get unique, unoverwritten folders.
- New model selection binds its output workspace immediately, including before an analysis is started; CWD is no longer an accidental evidence root.
- Comparison, diagnostic, GUI log, and ZIP destinations are physically separated.
- Saved-case registry remains SHA256-model/result checked. New metadata indexes are tiny; original PNGs are no longer copied into per-support index folders.
- Organize gravity review now writes **one** manifest + **one** hash-verified ZIP and does not produce extracted duplicate trees/per-module ZIPs. Review ZIP necessarily contains compressed copies for export.
- Bundle/latest-run selection rejects saved runs from an unrelated model when a model script is specified; older explicit selections are preserved.
- Read-only `tools/audit_gravity_workspace.py` provides an on-PC content hash inventory. It does not silently discard historical files.

## Acceptance gates

- Current changes are in a stacked review branch; do not infer they are in a locally checked-out `main`.
- Native Windows tests must exercise auto/browse source selection, each 32/76/97 support case and each profile, two-case sensitivity, three-case comparison, offline ETABS table, GUI reload, review ZIP, and evidence archive.
- The full result writer still stores its within-case PNG/PDF/XLSX at that case run's root for existing plot/export consumers. Subcategorizing those by media type requires reader migration and native evidence verification. Do **not** automatically move them.
- `02_GRAVITY/<support strategy>` and historical shared directories in existing exports remain untouched and may show older previews. A current code change cannot retroactively delete these user files.
- ETABS–OpenSees physical equivalence and first-step nonlinear wall convergence remain separate engineering P0 gates.
