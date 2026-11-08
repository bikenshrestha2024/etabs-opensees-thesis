# ETABS wall-base mesh nodes versus genuine restraint nodes (8 Nov 2026)

## Finding from native and offline evidence

In the supplied 76-node offline comparison, 44 ETABS point IDs have **zero FZ** but their matched OpenSees nodes carry vertical reactions. The source-support case had 76 fixed nodes; the independent continuous-wall-base case had 97 fixed nodes. This discrepancy is a serious **restraint-classification / wall-shell compatibility question**, not proof that every ETABS zero-reaction joint is free.

Crucially, the terms *analysis mesh point*, *source point object*, and *restrained analysis DOF* are different. ETABS may internally mesh a wall and transfer forces through constraints. Zero FZ at a displayed ETABS point does **not alone prove** GetRestraint(UZ)=false. Conversely, a coordinate-merged OpenSees node is not automatically supposed to be fixed just because it lies along a wall foundation edge.

### Engineering policies (do not conflate)

* `ETABS_SOURCE_SUPPORTS`: must use genuine, verified source-EDB restrained points. Do **not** add every mapped mesh node merely because it appears in the 76-node table; similarly do **not** delete 44 restraints on the basis of zero output force alone.
* `CONTINUOUS_WALL_BASE_FIXED`: leave unchanged, as requested. This is a fixed-base sensitivity idealization, not a replacement for native ETABS constraints or a physical raft-foundation model.
* `EDGE_PROPAGATE_CONFIRMED` in `components/model/assembly.py`: existing opt-in mesh-edge support propagation requires explicit native ETABS wall auto-mesh confirmation. It must not silently alter the source validation baseline.

### What to verify from original EDB

1. PointObj.GetRestraint for every source point, including unique IDs 725, 717, 720, 802, 721, 724, 719, 799, 718, 798, 723, 722, all other zero-reaction mapped points, and structural corners 701, 264, 8. Save raw API returns, units, source file SHA256 and analysis mesh association.
2. ETABS wall auto-mesh option *Add Restraints/Constraints on Edge if Corners have Restraints/Constraints*, plus internal generated-node restraint / constraint mapping from the **original solved model**. Confirm whether reactions of internal nodes are condensed to adjacent source points.
3. Categorize each node: `NATIVE_RESTRAINED`, `NATIVE_UNRESTRAINED`, `INTERNAL_MESH_CONSTRAINED`, `UNKNOWN`. Determine whether the OpenSees solver has the same constraint equations, or merely matches the graphical point locations.
4. If the native ETABS source truly only restrains endpoints and opening-edge points, rebuild the **source** OpenSees case with those source restraints and compatible wall-shell MPC / mesh connectivity; keep the independent continuous case intact. Do **not** simply release all intermediate shell mesh nodes: it may cause instability or destroy the actual wall-base support mechanism.
5. Compare integrated `WALL_25`, `WALL_8`, `WALL_53` foundation region totals and all column reactions. Single wall-shell mesh-joint reactions are not invariant under remeshing or constraint redistribution.
6. Separately audit the unresolved gross beam end-offset weight (8,652.444 kN potential) and ETABS ULS elastic shell stiffness modifiers. Do not use reaction matching as an excuse for weight/stiffness tuning.

## Offline 3D reaction view (no ETABS or OpenSees solver required)

From the repository root:

```powershell
conda install -c conda-forge plotly
python Run_Offline_Gravity_3D.py
```

Choose the already-exported `ETABS_OpenSees_All_76_Nodal_Reactions.csv`. Select a native ETABS restraint CSV **only if its original source-EDB provenance is verified**. Otherwise leave the question unanswered; audit will label all 76 statuses `UNVERIFIED`.

Alternatively:

```powershell
python -m components.validation.gravity_reactions_3d "ETABS_OpenSees_All_76_Nodal_Reactions.csv" "Gravity_3D_Review"
```

Files:
* `Gravity_Base_Reactions_3D.html`: self-contained 3D visualization at physical XYZ. Dropdown switches ETABS, OpenSees source, OpenSees continuous, and both signed discrepancies. Hover lists ETABS unique name, OpenSees node tag, reaction and native restraint status.
* `Gravity_3D_Restraint_Audit.csv`: per-point reaction and provenance table.
* `Gravity_3D_Restraint_Audit.json`: exact totals, zero-ETABS-FZ count, native restraint coverage, and explicit `NOT_VALIDATED` status.

If native ETABS restraints CSV is available, it must include columns `ETABS Unique Name`, `restraint_verified`, `uz_restrained`, each true/false. Do **not** derive these flags from the FZ values. Unknown restraints remain UNVERIFIED.

## Current status

The comparison is **NOT STRUCTURALLY VALIDATED**. This change adds transparent offline visualization and a verification gate; it intentionally does **not** change wall boundary conditions, elastic stiffness, physical weights, seismic mass, or nonlinear model mechanics without reviewed native restraint evidence. Continuous-wall-base strategy remains unchanged.
