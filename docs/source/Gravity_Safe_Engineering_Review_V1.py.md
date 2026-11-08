# Safe Gravity Engineering Review V1 — ETABS / OpenSees

**Program:** \`Gravity_Safe_Engineering_Review_V1.py\` at repository root.

This is a **source-evidence reviewer**, not a substitute for native
ETABS/OpenSees gravity analysis. It is a *fail-closed* alternative to
blindly subtracting the historical 8680.475 kN excess or automatically
installing Claude's unreviewed patch.

## The independent physics and the separate analysis conventions

Global gravity loading:
\`W = sum(q A) + sum(gamma V_physical_union) + independent nonstructure dead loads\`.
OpenSees frame and shell stiffness elements should remain independently
defined: no solver performs building-scale concrete union subtraction.

The existing gross-length OpenSees report showed beam weight
53984.055 kN; original ETABS material list reported 45331.611 kN.
ETABS source beam-end offsets totaled 721.25 m, which at 600x800 mm
and 24.992618 kN/m³ gives a **potential** 8652.444 kN beam-weight
difference. It is a *diagnostic comparison*, not a physical/ETABS
equivalence certificate. Beam \`CP 8 Top Center\` may make slab/beam
physical overlap different from a centered box. The physical union
sensitivity (~19358.527 kN) must NOT be subtracted in addition to the
beam clear-length convention.

The program rigorously recomputes each source beam's gross/clear weight
from its own object ID, dimensions, density and end offsets, checks
per-object reported gross/offset values, rejects duplicate IDs,
nonfinite or missing data and rejects double deductions.

**Independent source weight:** Prepare a small CSV extracted from the
*actual source ETABS EDB Material List by Object Type*:

\`\`\`csv
object_type,weight_kN
Beam,45331.611
\`\`\`

Other categories can be included with their own row, provided exactly
one total beam row is present. A manually typed number is usable for
exploration but does not enable a candidate. The *CSV alone* still
requires an engineer to review original EDB identity, section material,
Self Weight Option and insertion geometry. Its SHA-256 is recorded.

Run from the repository root with Windows Python 3.12 and no additional
dependencies (openpyxl is optional if enabled in a later version):

\`\`\`powershell
python Gravity_Safe_Engineering_Review_V1.py --export "D:\Thesis Opensees\...\1" --etabs-beam-csv "D:\ETABS_material_list_beams.csv"
\`\`\`

The program writes:
- \`<export>/Gravity_Safe_Engineering_Review/GRAVITY_SAFE_REVIEW.json\`
- \`.../GRAVITY_SAFE_REVIEW.txt\`
- \`.../BEAM_SOURCE_RECONCILIATION.csv\`
- \`.../FOUNDATION_REGIONS.csv\` if explicit region evidence is present

There is **no change** to the structural model, source configuration,
analysis results or original ETABS model.

For a trial candidate configuration, after checking the source geometry:

\`\`\`powershell
python Gravity_Safe_Engineering_Review_V1.py --export "D:\Thesis Opensees\...\1" --etabs-beam-csv "D:\ETABS_material_list_beams.csv" --stage-reviewed-candidate --approval-text "I REVIEWED ETABS BEAM SELF WEIGHT AND SOURCE GEOMETRY"
\`\`\`

This writes a new timestamped **candidate config** and original
config backup to \`Gravity_Safe_Engineering_Review/CANDIDATE_...\`.
It does **not** overwrite the actual config or rebuild the model.
A competent reviewer must confirm the independent source convention,
retain original model evidence, and explicitly install/test the staged
candidate before comparing reactions. Even a match within screening
tolerance is **NOT STRUCTURAL ACCEPTANCE**.

## Foundation-region comparison — manual, geometry-verified mapping

Use the same original 76 ETABS support points in
\`Gravity_Node_Reaction_Comparison.json\`; create \`regions.csv\`:

\`\`\`csv
etabs_point,region_id,region_type,verified,source_basis
264,CORE_PIER_X1,WALL_PIER,YES,Original ETABS source wall-line panel W17
263,CORE_PIER_X1,WALL_PIER,YES,Original ETABS source wall-line panel W17
\`\`\`

**All 76 points must be reviewed and included**, not just the
illustrative two rows. Every row must have a nonempty source geometry
basis and \`verified=YES\`; the program rejects missing/ambiguous
global-Z node matches and incomplete assignments. Region types:
\`COLUMN\`, \`WALL_PIER\`, \`CORE\`, \`OTHER\`.

Launch with \`--foundation-map regions.csv --node-comparison
Gravity_Node_Reaction_Comparison.json --etabs-base-kn 311367.313879\`.
The program reports both groups and each original node reaction,
global joint-sum vs ETABS base, normalized load shares and the
**worst individual reaction difference within each region**.

A core-total agreement alone is NOT wall force equivalence. It can
hide significant local reactions, as illustrated by the original
ETABS point 264 / OpenSees node 41 mismatch around 10861 kN.
A grouped comparison must be paired with original node responses,
wall mesh connectivity and source reference geometry.

## Required structural follow-up

1. Source-verify section physical placement, slab thickness reference
   plane, wall polygon openings and beam insertion points.
2. Preserve original ETABS \`1. DL + LL\` 1.0/1.0 factors and independent
   seismic 0.3 Live preload and mass configuration.
3. Independently rebuild a reviewed candidate with actual source
   offset policy; **never stack** \`ETABS_BEAM_CLEAR_LENGTH\` with
   \`VERIFIED_SINGLE_OWNER\`.
4. Rerun gravity source-only **76-support** and separate **97-support**
   sensitivity; independently rerun ETABS direct analysis against the
   **same model revision**, not a stale ZIP result.
5. Compare total applied gravity, support equilibrium, mapped
   foundation-region totals, original individual reactions,
   vertical displacements, beam end actions, wall shell forces,
   structural mass and periods. Only then proceed to ESM/MRSM/NLTHA.

**Test:** \`python tests/verify_safe_gravity_engineering_review.py\`.

## OpenSees documentation

- Frame \`eleLoad\`: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html
- \`ShellMITC4\`: https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html
- \`rigidDiaphragm\`: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html
- \`PDelta -jntOffset\`: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html

Those commands do not automatically remove a physical beam-column-slab
intersection from member self weight.
