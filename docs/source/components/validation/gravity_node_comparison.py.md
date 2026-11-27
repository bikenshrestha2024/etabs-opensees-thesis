# Coordinate-matched gravity support reactions

[REF components/validation/gravity_node_comparison.py]

The existing Gravity GUI **Extract ETABS + compare gravity** action calls this
module automatically *after* successful ETABS direct API extraction and
OpenSees gravity JSON validation.

## Required evidence

- OpenSees `Gravity_Result_V110.json`: `nodes` with global XYZ and
  `reactions` with support tags and RZ values in kN.
- ETABS `etabs_gravity.json`: `joint_reactions` with support point XYZ and
  verified *global-Z* vertical reactions, plus original ETABS point local axes.
- Matching EDB source, load combination and support restrictions are independent
  prerequisites. Identical global base totals do NOT prove correct transfer.

## Matching and error gates

Nodes are matched one-to-one by global XYZ within default 0.01 m tolerance.
Node identifiers may differ. Multiple candidates, coincident duplicated
wall/column nodes or unmatched supports are logged separately and NOT summed
or assigned invented load. ETABS `JointReact` provides point-local F1/F2/F3:
this implementation compares `F3` to global OpenSees RZ **only when the API
reports all point-axis angles zero and advanced axes disabled**. Other cases
remain `MATCHED_AXES_UNVERIFIED` until an audited axes transformation or
global-coordinate source result is available. For CSI's point-axis angles see
[GetLocalAxes API](https://docs.csiamerica.com/help-files/etabs-api-2016/html/308522dd-3722-207b-c394-45b9db82fb4b.htm).

The principal ranking is `|Rz_ETABS - Rz_OpenSees|`, with percentage
differences normalized by the larger absolute reaction. Report also includes
unmatched counts, coordinate separation, source point labels, and a table of
all 1:1 matched nodes. `matched_sum_difference_kN` covers **only** supported,
unambiguous and axis-verified pairs, and is not substituted for either model's
global `BaseReact` total.

This is a **support-reaction map**, NOT the applied gravity force at each
slab/beam/wall node. The latter requires independent ETABS assigned-load
and mesh connectivity exports and compatible OpenSees applied-nodal force
evidence. High reaction difference alone cannot identify a specific faulty
slab element or defective load assignment. Examine structural self-weight,
slab geometry/mesh/load, beam and wall connectivity, boundary conditions,
and wall openings at the largest discrepancy coordinates.

## Reports

`<gravity output>/Gravity_ETABS_OpenSees_Direct/`:

- `Gravity_Node_Reaction_Comparison.json`
- `Gravity_All_Support_Nodes.csv`
- `Gravity_Top_Node_Discrepancies.csv`
- `Gravity_Node_Reaction_Comparison.xlsx` (with openpyxl)
- `etabs_gravity.json` (raw returned ETABS point reactions and provenance)

The existing ZIP exporter includes these reports.

Tests: `python tests/verify_gravity_node_comparison.py`.

## All-model node Excel and critical support locations (2026-11-08)

The Direct ETABS gravity comparison now also creates:

- `Gravity_All_Model_Nodes.csv` — every recorded OpenSees
  gravity node (supports and free nodes), mapped original ETABS
  point name where available, XYZ, OpenSees 6 DOFs, measured
  vertical support reaction, and ETABS support-only reaction
  and displacement where exported.
- `Gravity_Node_Reaction_Comparison.xlsx` — sheets
  `Audit`, `All support nodes`, `Largest differences`,
  `All OpenSees nodes`, `ETABS ID mapping`.

**Do not confuse a mapped non-support node with an ETABS support.**
Only the original 76 source ETABS restrained-point reactions are
directly comparable. Missing non-support ETABS displacement and
reaction entries remain empty, never invented or coerced to zero.
The source ETABS workbook contains more joint displacement data
than the current direct API support extraction; a separate importer
is needed to compare all 1,101 original ETABS joint displacements.
The 11k+ OpenSees node inventory is useful for locating mesh
connectivity at critical core-wall, slab and column junctions.
An identical coordinate match does not establish equivalent
structural connectivity or restraint transfer.

The conventional V04 **critical support examples** remain points
264/263, 8/7 and 725/717/720/802; the ranking is recalculated from
each newly executed direct comparison, not hardcoded.

Regression: `python tests/verify_gravity_node_comparison.py`.


## V16 numerical-data integrity gate (2026-11-14)

Before node matching or reaction discrepancy ranking, reject nonfinite global XYZ
coordinates (NaN/Inf), nonfinite OpenSees vertical support reactions, missing
ETABS point identities and duplicate ETABS or OpenSees reaction identifiers.
Previously, NaN XYZ could appear as an unmatched coordinate and NaN Rz could
contaminate the summed/ranked differences, producing a plausible-looking
comparison with invalid numeric evidence. Duplicate reaction IDs could also
contribute repeated support values. The new behavior **fails closed** with a
specific `ValueError`; it does not fabricate missing loads or automatically
consolidate physically distinct wall-mesh support reactions.

Passing these screens still requires ETABS global-Z axis verification,
source-model identity, equivalent gravity combination, restraints and load
path. Refer to `tests/verify_gravity_node_comparison.py` for regression cases.

## V21 axis-provenance propagation and duplicate-row rejection (2026-11-15)

The native ETABS direct extractor supplies `global_z_basis=GLOBAL_Z_VERIFIED_DEFAULT_AXES` only when all three point local-axis angles are zero and advanced axes are disabled. A finite numeric `rz_global_kN` with another or missing basis is **not** proof of global-Z reaction. The `compare_support_nodes` matcher therefore labels such coordinates `MATCHED_AXES_UNVERIFIED` and excludes their difference from the valid one-to-one global-Z ranking. Nonfinite ETABS values are explicitly rejected.

This same check now applies to `export_fixed_source_support_reactions` and the all-node crosswalk: the 76-support workbook cannot rank a numeric local-axis reaction as `MATCHED_GLOBAL_Z`; its ETABS global sum remains unavailable if any point lacks verified basis. All-model node exports exclude its unverified ETABS global Rz/delta fields. Duplicated ETABS point reaction and displacement rows cause an explicit error rather than replacing one row with another.

These are metadata/axis and data-integrity checks. They are **not** actual ETABS restraint equivalence, don't convert rotated point-local axes, don't alter the user's 32/76/97 support scenarios and don't substitute for six-component force/moment checks. Tests: `python tests/verify_gravity_node_comparison.py`.

## 2026-11-27 — six-component support evidence

The gravity runner now records all six global OpenSees reaction components (forces kN, moments kN m); old results without moments remain missing evidence. The existing coordinate/axis gate is reused to report component residuals and matched support resultants about the global origin, using M_origin = M_node + r cross F and each model's actual coordinates. Output is in existing JSON/CSV/XLSX and the Six DOF resultant worksheet. A subset of pairs cannot establish whole-foundation parity; neither summed nodal forces nor moments are independently recovered section-cut forces. No physical parameters, load factors or support restraints changed. Native analytical mesh/MPC transfer and matched cuts still require actual source evidence. Unit tests exercise the moment translation, missing moments and unmatched native nodes.
