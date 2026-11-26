# Project primary ETABS-reaction support filter

Source module: `components/gravity/etabs_reaction_support_filter.py`

This is an **offline, deterministic, strictly opt-in** gravity sensitivity model. It filters original mapped OpenSees supports to the exact 32 node IDs confirmed by the user for the project. It does not run ETABS or change the source model definition. It must not be generalized to other EDB projects without verified mapping changes.

## Input/evidence

* Original solved ETABS `1. DL + LL` `Joint Reactions` XLSX/CSV, all Base rows (not a view filtered to one story or step).
* `OpenSees_Element_Connectivity.json` ETABS unique-name ↔ OpenSees tag mapping.
* Original assembled model six-DOF support assignments.
* A project-specific, explicitly user-confirmed 32-tag reference list in source code. The selector **fails closed** if the table and mapping do not select these exact 32 nodes.

## Output

`ETABS_Nonzero_Reaction_Support_Audit.json` includes ETABS source path and SHA256, selected and released source tags and point reactions. After a successfully completed primary diagnostic gravity solve, `Primary_32_ETABS_OpenSees_Reactions.xlsx`, `.csv` and `.json` compare each ETABS point with its OpenSees mapped support, rank discrepancies and report separate global and worst-node errors.

## Safety and acceptance

* ETABS zero FZ does not prove a node has no source UZ or other restraint. Releasing 44 nodes is a **diagnostic assumption**, not actual ETABS support verification.
* Native ETABS restraints, wall shell auto-mesh edge constraints and internal generated mesh joints remain to be verified in the source EDB.
* Do not confuse original 76 mapped support nodes, project primary 32 reaction-filtered points and independently idealized continuous wall base.
* Numerical equilibrium and low reaction mismatch are **not sufficient** to assert equivalent structural boundary conditions, nonlinear stiffness, seismic mass or code compliance.
* This filter only acts under the gravity GUI opt-in `ETABS_NONZERO_REACTION_DIAGNOSTIC` mode. It neither modifies original persistent model data nor affects modal/ESM/MRSM/NLTHA.

Related review: [Reaction-filter workflow](../../../review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md).

## V25 — explicit source six-DOF restraint validation and atomic publication (2026-11-15)

`classify_supports()` now refuses **every** malformed record in `original_supports`: it requires six explicit flags, each literal `bool` or integer 0/1. Previously a malformed entry could be silently dropped by the length filter or a text flag such as `"0"` could be evaluated truthy. The project-selected 32 nodes are unchanged. This **does not** mean that ETABS zero reaction identifies a free DOF, or that the 76 and 97 alternatives are physically equivalent.

`export_primary_32_comparison()` now rejects duplicate selected source mapping tags and nonfinite source reactions before publication, validates its summary JSON, refuses symlinked output directory/direct target files and uses shared atomic JSON/CSV writers plus a uniquely staged XLSX with atomic final replacement. **The existing JSON, CSV, XLSX filenames and return schema remain unchanged**, so existing GUI/readers are preserved. The three-file report is not one transactional bundle; reviewer must inspect case identity and each final file. Tests: `tests/verify_primary_32_support_reactions.py`. The NLTHA quality CI now also directly triggers and runs this verifier on primary-32 selector edits. No ETABS EDB, original Excel or native solver output was touched.

2026-11-26 — Primary 32-node report adds separate global and pointwise screening, maximum/sum/RMS absolute residuals and the existing direct comparison's 1 kN numerical screen. Numerical agreement requires both global and pointwise screens; no code or engineering tolerance is inferred. The original ETABS and OpenSees forces remain unchanged.
