# Gravity evidence upload workflow

**Code:** \`components/gravity/evidence_workflow.py\` and
\`components/gravity/comparison_bundle.py\`.

The existing \`10_GRAVITY.py\` application uses one gravity root chosen in
the GUI: **Output folder**. From this root, it writes:

- \`Gravity_GUI_Actions.log\`: timestamped high-level operations, complete
  numerical result paths and explicit file/package warnings
- \`Gravity_Result_V110.json\`, \`Gravity_Run_V110.log\`,
  \`Gravity_Results_V110.xlsx\`: individual gravity run (when run once)
- \`Gravity_Wall_Base_Comparison/<run-id>/ETABS_SOURCE_SUPPORTS/\` and
  \`CONTINUOUS_WALL_BASE_FIXED/\`: independent full-gravity runs, their
  logs, workbooks, and generated figures
- \`Gravity_Wall_Base_Comparison/<run-id>/Gravity_Wall_Base_Strategy_Comparison.xlsx\`
  plus JSON and node-difference CSV: support-strategy comparison
- \`Gravity_Wall_Base_Comparison/<run-id>/ETABS_Full_Table_Offline_Comparison/\`:
  optional completed ETABS table comparison (no API)
- \`Gravity_ETABS_OpenSees_Direct/\`: optional direct ETABS API
  results, native solver logs and node-by-node comparisons
- \`Gravity_Evidence_Upload/\`: **single central upload location** for
  immutable versioned \`Gravity_ETABS_OpenSees_Evidence*.zip\` archives
  and their sibling unpacked folders.

After a successful gravity run, dual run, offline ETABS comparison or
direct API comparison, the GUI packages existing evidence and displays
the **exact full ZIP path** in its log. Click **Bundle gravity evidence
ZIP** to regenerate a new, immutable revision without rerunning any solver.
Use **Open output folder** and then \`Gravity_Evidence_Upload\` to
attach the newest ZIP to ChatGPT. The GUI event log, solver logs,
reports, figures, direct ETABS node results, current dual case workbooks,
source model configuration, structure mapping and weight audits are
gathered by the same routine.

The ZIP contains:
\`EVIDENCE_MANIFEST.json\` listing exact source path, SHA256, byte count,
missing files and oversized omitted files; and
\`EVIDENCE_FILE_PATHS.txt\` listing source paths of all packaged files.
The original EDB is never altered, and the exporter does not rerun
ETABS/OpenSees or assert code/engineering acceptance.

The uploader normally caps individual uncompressed source files at
40 MB to keep ChatGPT uploads manageable. Oversized **essential** source
model-data and node-mapping JSON files are first losslessly compressed
into a nested ZIP, and included if that compressed representation fits.
Otherwise, oversized files are logged with their absolute original
path and SHA256 instead of being silently omitted. A small file named
`LATEST_GRAVITY_UPLOAD.txt` in the gravity root shows the precise
latest ZIP and evidence-index locations. Every collected/generated
file's full path is also printed in `Gravity_GUI_Actions.log`. A large source ETABS full-table workbook may need separate
upload, or use the offline ETABS comparison workbook/CSV (small).

**When running dual wall-base strategies**, the upload manifest records
both 76-point and 97-point models as separate results and never
mislabels the continuous-base case as ETABS validation. A source case
\`Gravity_Result_V110.json\` is mandatory for a successful bundle; an
absent ETABS direct result remains MISSING until actually extracted.

Tests: \`tests/verify_gravity_comparison_bundle.py\` and
\`tests/verify_gravity_evidence_workflow.py\`.
