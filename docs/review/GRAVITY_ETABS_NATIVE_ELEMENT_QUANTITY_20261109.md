# 32-support gravity: original-object quantity and load path audit (2026-11-09)

## Primary reference and engineering gate
- The primary reaction diagnostic is the 32 ETABS reaction-bearing source points (ETABS_NONZERO_REACTION_DIAGNOSTIC). The other 44 zero-reaction mapped ETABS points remain in the shell-mesh/restraint provenance, with the 76 and 97 support models kept as sensitivity cases. Zero FZ is NOT proof of a free DOF.
- Direct ETABS gravity: 311367.313880 kN; OpenSees gravity: 320019.758231 kN; excess: 8652.444352 kN. Matching beam clear-span weight candidate is a numerical hypothesis, NOT an adopted self-weight correction.
- Model identity remains subject to working-copy versus original EDB evidence. All ETABS quantity tables must be obtained from the same currently analyzed copy as the direct ETABS base reaction.

## Load path: distinguish FORCE application from physical WEIGHT

Current assembly (`components/model/assembly.py`) does the following:
1. Each original ETABS floor polygon is meshed into ShellMITC4 cells. Shell self-weight is calculated from cell area * slab thickness * material weight density once under the original load pattern's self-weight multiplier.
2. Assigned floor area loads (Floor Finish, Partition, Live etc.) are converted to consistent/equivalent nodal forces based on child cell area. They are NOT automatically another slab structural self-weight. An area-load assignment that itself represents slab dead weight must be explicitly classified or it can double count the slab.
3. Source beams, columns and braces have separate frame self-weight under source pattern self-weight multipliers; shell shear walls have source shell self-weight. Source additional wall/frame loads remain distinct external loads.
4. `apply_gravity_profile` applies profile load factors to the assembled unfactored pattern vectors. Reapplying a profile factor in the exported nodal loads would be a defect and must be detected by comparing `load_provenance`, `gravity_by_pattern_kN`, and applied nodal-force totals.
5. Shell load vectors assembled onto beam/column-connected nodes are a LOAD DISTRIBUTION technique. They do not create a second slab weight unless the same source force is also independently applied elsewhere. They may not produce identical local stiffness/load path to native ETABS Shell elements even when force sums match.

## Actual native ETABS element/material quantities

The integrated direct ETABS comparison now uses
`components/validation/etabs_native_quantity_tables.py` on its SAME
active ETABS COM model, with selected display units set to kN-m-C and then
restored. It queries GetAvailableTables first; this avoids inventing
version-dependent table keys. It reads matching Material List, material
quantities, frame/area object, section properties and assignment tables,
where available, and emits:

```text
Gravity_ETABS_OpenSees_Direct/
  ETABS_Native_Quantity_Tables/
    ETABS_NATIVE_ALL_TABLE_NAMES.json
    ETABS_NATIVE_QUANTITY_MANIFEST.json
    etabs_table_<hash>.csv
```

Each table retains native original fields and source-key/hash. A missing
table or an API failure is explicitly recorded. Extracted table values are
not automatically joined to source IDs or interpreted as volume/weight
without confirming the native column labels, units, object type and source
EDB identity.

## Matching OpenSees original-object quantities

The per-run `components/gravity/joint_weight_reconciliation.py` reads
existing geometric solid ownership data and writes:

- `Gravity_Original_ETABS_Object_Quantities.csv`: original ETABS ID,
  category, mesh child count, gross/net/overlap m3 and kN.
- `Gravity_Joint_Weight_Reconciliation.json`: exact conservation,
  overlap priority, original beam crosswalk, source hashes and nonacceptance.
- `Gravity_Joint_Weight_Scenarios.csv`: three mutually exclusive
  current gross, clear beam-only and geometric union-only alternatives.

There are 750 source beam objects subdivided into 3300 FE segments in this
working model; the total is based on source object weights, NOT multiplied
by the number of FE pieces. Slab source polygon/mesh conservation is separately
audited by `components/gravity/slab_self_weight_audit.py`.

**Do not apply automatic deductions.** A floor-to-floor column/wall owner
can be a valid physical takeoff partition; clear beams may exclude the concrete
inside columns/walls and slab footprints may overlap columns/walls at each
storey. But the sum must be the actual 3D union with real wall openings,
noncentered insertion, slab locations and beams crossing wall lines, not
several unrelated 2D deductions. Braces require a separate source-object
material length/area and connection assessment: they are not part of the RCC
box union. Real ETABS material quantities and recorded weight modifiers
must decide the correct partition.

## Action sequence
1. Update local repository and run unit tests (below). Re-execute the
   integrated **Extract ETABS + compare gravity** action against the same
   analyzed working-copy EDB: this collects native quantity tables. No
   ETABS installation is available in the CI environment.
2. Rerun the primary 32-point diagnostic source audit (no physical model
   modifications are made). Bundle gravity evidence so that native ETABS
   raw tables and OpenSees original-object quantities are in the same ZIP.
3. Compare source-object IDs, sections, unit weights and volumes from native
   ETABS exports to OpenSees and reconcile components by load pattern.
   Reject ambiguous or absent native per-object fields; do not fit global
   8652.444 kN difference into a guessed member deduction.
4. Only after native material volume conventions are verified should the
   source model be explicitly updated (separate reviewed change), followed
   by fresh gravity, modal, NLTHA preflight and time-history runs.

```powershell
python tests/verify_etabs_native_quantity_tables.py
python tests/verify_gravity_joint_weight_reconciliation.py
python tests/verify_gravity_source_load_reconciliation.py
python tests/verify_joint_volume_ownership.py
python tests/verify_slab_self_weight_audit.py
```

No ETABS OAPI test or full nonlinear thesis model acceptance is implied by
committing these checks.

Official CSI references:
- https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Floor_Auto_Mesh_Options.htm
- https://docs.csiamerica.com/manuals/etabs/User%27s%20Guide.pdf
- https://web.wiki.csiamerica.com/wiki/spaces/safe/pages/1802698/
- https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell_Loads/Uniform.htm
