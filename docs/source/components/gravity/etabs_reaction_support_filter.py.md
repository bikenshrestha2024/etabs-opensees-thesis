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
