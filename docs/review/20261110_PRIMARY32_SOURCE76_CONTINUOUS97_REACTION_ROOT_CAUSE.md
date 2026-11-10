# November 10, 2026 — Gravity foundation reaction audit (user V04 ZIP)

## Evidence, not structural acceptance

Source: user-supplied `Gravity_ETABS_OpenSees_Evidence_V04(6).zip`, with 199 archive entries. This is a local-only project artifact: do **not** upload original EDB, full private material-assignment workbook or raw site/project information to public GitHub. Numbers below were independently recomputed from the ZIP's saved CSV and three native OpenSees result JSON files. The source/archive content is **not** committed.

### Corrected physical total

| Parameter | kN |
|---|---:|
| ETABS FZ (saved source table) | 311,367.313600 |
| OpenSees gravity applied / sum RZ | 311,367.31387955 |
| Absolute difference | 0.00027955 |
| Previous gross-beam excess now corrected | 8,652.444352 |

The native assignment review identifies 750 beam objects, verified source unique IDs and end offsets, reported clear-beam weight 45,331.6105 kN and source gross-beam weight 53,984.05488 kN. The assembled source uses `ETABS_BEAM_CLEAR_LENGTH`. This reconciles **overall gravity**, not individual support reaction paths.

### Three distinct numerical boundary cases

1. `ETABS_NONZERO_REACTION_DIAGNOSTIC`: **32** restraint/reaction nodes, Rz sum 311,367.313880 kN; compared to 32 nonzero saved ETABS point reactions. Maximum absolute point difference 3,041.265778 kN (OpenSees node 36, ETABS point 263). Sum of absolute point differences **37,297.027232 kN**; signed net difference nearly zero. Selecting the 32-node set releases 44 previously restrained source nodes and **changes the physical boundary-value problem**.
2. `ETABS_SOURCE_SUPPORTS`: **76** OpenSees restrained nodes, Rz sum 311,367.313880 kN. The 44 points with **zero** saved ETABS joint FZ carry **104,463.013534 kN** total in this 76-restraint solution (**33.55%** of the gravity total). Recomputing the 76 true nodewise comparisons from `wall_base_comparison/ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json` (rather than from the selected 32-node result) yields sum absolute differences **208,926.027068 kN**. This does NOT represent extra gravity: totals still balance. It represents a very different load path/support-reaction assignment compared with the saved ETABS joint table.
3. `CONTINUOUS_WALL_BASE_FIXED`: **97** OpenSees restrained nodes, Rz sum 311,367.313880 kN. This is an additional sensitivity case, not a direct ETABS pointwise baseline. Do not substitute its point reactions into the 76 audit.

### Why 19 missing was misleading

The manifest has **19** entries under `missing`; **18 are optional or not produced** (SLS/ULS alternate diagnostics, legacy files, skipped optional native EQ/PDelta/table extraction, offline comparison, duplicate optional references). Only **one** required item was the `node_audit_76/ETABS_REACTION_MATCHES` gate. The bundler generated the 76-node audit from the *selected 32-node diagnostic payload*, despite having the authentic solved 76-node result in the same ZIP. That marked the 44 excluded reactions as MISSING_OPENSEES_REACTION. This is a **bookkeeping/source-selection bug**, not absence of a 76-node solver run. Patch: use actual 76-source-support payload after checking same source-model script path, gravity profile, applied load, 76 reactions and solver success.

After correcting the audit, the 44 points are **not missing**. Their reported ETABS zero Rz and OpenSees nonzero Rz are an **unresolved engineering mismatch**. Preserve the mismatch and do not claim ETABS equivalence. The source reactions cannot be made valid by copying or redistributing ETABS values.

### Likely physical investigations — NOT yet proven

- Establish whether the ETABS 44 zero saved point reactions represent external ETABS object joints, while ETABS automatically generated restrained shell-mesh/interior joints are omitted or condensed into different objects. Obtain actual analysis-mesh joint reactions and transformed global FZ, not merely saved object-label point reactions.
- Confirm *exact* six-DOF restraints, wall shell base edge conditions, coupled/merged nodes, diaphragm, beam rigid-zone offsets, kinematic constraints, local axes and element connectivity using a source-ID-and-coordinate crosswalk, separately for column footings and wall base segments.
- Compare wall, column, brace and floor reaction resultants by **foundation zone**, not only pointwise tags; preserve vector components and reactions from constraints not represented as `nodeReaction` on object points.
- Examine native ETABS and OpenSees slab MITC4 bending/membrane stiffness, wall shell stiffness and frame end offsets after verifying mapped geometry and equivalent load sources. Avoid retuning stiffness just to make FZ match.
- Confirm source ETABS model SHA and exact `1. DL + LL` load combination, shell and frame load patterns and opening geometry before any interpretation of local differences.

**Priority native evidence:** original ETABS automatically generated analysis joints/mesh and their FZ reactions; wall-line foundation section forces; original 32 source point set plus 44 mesh points; source 76 and continuous 97 OpenSees solver outputs; full signed nodal applied load and local frame/shell action audits.

### Packaging changes

The bundler now keeps all generated per-run evidence files in case-specific namespaces (`all_case_outputs/selected_gravity_full/`, `source_76_full/`, `continuous_97_full/`). A manifest distinguishes `missing_required` from `not_produced_optional`, and the GUI displays both counts separately. The output ZIP cannot contain files which were never produced; missing native analysis-mesh ETABS evidence remains clearly labeled. Source code does not change any beam, wall, mass, gravity or solver values.

**Acceptance:** `GLOBAL_EQUILIBRIUM_PASS`; `NODAL_FOUNDATION_REACTION_EQUIVALENCE_NOT_ESTABLISHED`; `NATIVE_ETABS_AUTOMESH_REACTION_EVIDENCE_PENDING`.
