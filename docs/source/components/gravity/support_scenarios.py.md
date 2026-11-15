# Gravity wall-base boundary condition sensitivity

Source: [support_scenarios.py](../../../../components/gravity/support_scenarios.py)

The existing `10_GRAVITY.py` GUI includes a wall-base support
selector and **Run BOTH wall-base gravity strategies**. The two runs are
sequential independent OpenSees processes with identical 1.0D+1.0L
(including assigned Roof Live) and independent seismic mass, using the
same generated ETABS->OpenSees geometry and source loads.

- `ETABS_SOURCE_SUPPORTS`: current export's original source ETABS
  point restraints (only the points explicitly recorded, including
  wall corners and opening edge points with actual restraints).
- `CONTINUOUS_WALL_BASE_FIXED`: source restraints PLUS generated
  mesh nodes on *horizontal wall edges at the foundation elevation*
  whose two original endpoints are both fixed in six DOFs. This is
  a fully fixed wall-foundation idealization, **NOT** a validated
  foundation/soil/raft model. An unsupported wall edge is NOT
  automatically fixed, even in this mode. Intermediate wall nodes
  above the foundation are not fixed.

The source EDB, exported model-data JSON and model configuration are
not changed by the gravity-only runtime override.
The separate ETABS wall auto-mesh restraint/constraint setting
must still be reviewed on the actual EDB. ETABS edge interpolation
constraints are **not automatically equivalent** to `ops.fix` applied
to every internal wall mesh node: see CSI
[Wall Auto Mesh Options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm)
and [Auto Edge Constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm).

The GUI writes separate case reports and logs under
`<output>/Gravity_Wall_Base_Comparison/<run id>/`:

```text
ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json
ETABS_SOURCE_SUPPORTS/Gravity_Run_V110.log
ETABS_SOURCE_SUPPORTS/Gravity_Results_V110.xlsx
CONTINUOUS_WALL_BASE_FIXED/Gravity_Result_V110.json
CONTINUOUS_WALL_BASE_FIXED/Gravity_Run_V110.log
CONTINUOUS_WALL_BASE_FIXED/Gravity_Results_V110.xlsx
Gravity_Wall_Base_Strategy_Comparison.json
Gravity_Wall_Base_Strategy_Comparison.xlsx
Gravity_Wall_Base_Nodal_Reaction_Differences.csv
```

The aggregate comparison validates the same applied full-gravity load
and reports support counts, reaction balance, maximum downward
displacement and reaction differences at shared tags. New fixed mesh
nodes do not have ETABS matching point reactions and remain
`CONTINUOUS_ONLY` records; a zero is never inserted for the missing
ETABS/source counterpart.

Change of gravity support idealization requires repeat analysis.
The `OPENSEES_GRAVITY_WALL_SUPPORT_STRATEGY` runtime setting is restricted
to `OPENSEES_GRAVITY_GUI_MODE`, so ESM, modal, MRSM and nonlinear
time histories do not inherit the sensitivity support model.
This tool does not decide which base model is physically correct
without foundations, ETABS auto-mesh settings and structural evidence.

Tests: `tests/verify_gravity_support_scenarios.py` and
`tests/verify_wall_base_restraints.py`.

## V23 source-based evidence checks — 2026-11-15

The 76-versus-continuous-wall sensitivity comparator rejects duplicate node and reaction tags (no silent dictionary replacement), rejects missing/nonfinite coordinates for reaction nodes, and requires coincident **global XYZ for any shared native node tag** before comparing its Rz. A node that appears only in the source case retains the source-case coordinate instead of an invented coordinate or a blank continuous-case coordinate. Each saved `support_vertical_reaction_kN` summary must reproduce the actual sum of finite `rz_kN` records within `max(0.01 kN, 1e-6 × |reported support sum|)`. This is a consistency tolerance for data export, **not** acceptance of gravity load balance or structural equivalence. See `tests/verify_gravity_support_scenarios.py`.

The comparator still compares only the two independently solved original-source (nominal 76 restraints) and continuous-wall (nominal 97 restraints) idealizations. The user's preferred 32 reaction-bearing physical support locations remain a separate, independently validated source selection. Matching tags/totals cannot prove that only boundary conditions differ; actual EDB/model SHA, mesh stiffness, load ledgers and six-component restraint geometry remain a separate native engineering review.
