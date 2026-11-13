# 02 — Model stage: independent 4 / 8 / 16 slab mesh studies and area-element integration

**Date:** 2026-11-13  
**Status:** CODE/PROVENANCE REVIEW — NOT ETABS EQUIVALENCE OR NONLINEAR ACCEPTANCE  
**Source scope:** `components/gravity/load_path_formulas.py`, `components/model/assembly.py`, `components/sections/area_elements.py`; uploaded V141 workbooks and V125 element/property audit are historical evidence, not automatically new mesh results.

## What is the area-element integration module, and when should it be used?

The **Area Element Integration** GUI prepares an **optional, additive call** to `instantiate_area_elements` which creates 3D shell/wall elements on an OpenSees model **after its nodes, sections, material definitions and connection constraints exist**. It bridges an ETABS area topology/property audit to (1) linear `ShellMITC4` floor elements using `ElasticMembranePlateSection` and (2) nonlinear `E_SFI_MVLEM_3D` wall panels using separately defined/calibrated FSAM materials. It preserves missing ETABS wall quads as openings. It is **not** the normal first-step importer; it does **not** apply loads or seismic mass, run a gravity solve, prove coupling-beam/opening behavior, or create a complete nonlinear building model.

**Where/why:** Use when explicitly building an area formulation in a domain **which does not already include those elements**. The conventional assembled model from `components/model/assembly.py` already generates floor shells/walls. Running the additive helper on those elements risks duplicate stiffness, element-tag conflicts, invalid load distribution and/or mass. The default remains `AREA_STAGE_EXECUTION = False`; do not turn it on merely to improve an existing slab mesh.

**Who approves:** A structural engineer reviews original ETABS source EDB identity, topology, area names, wall thickness, FSAM/steel/concrete calibration, gravity + mass source, contact/mesh edge connectivity and intended solver commands. The model-bound checklists are separate approval gates. A valid JSON file and Excel inventory are **not** that approval.

**How to inspect first:** Choose current `OpenSees_Element_Connectivity.json`, `OpenSees_Area_Section_Assignment_Audit.csv` and `OpenSees_Area_Model_Config_V116.json`. Click **Export area-object inventory (Excel + JSON)**. Output to `02_MODEL/AREA_INTEGRATION/excel/Area_Integration_Inventory_<topology-hash>.xlsx` and `02_MODEL/AREA_INTEGRATION/json/Area_Integration_Inventory_<topology-hash>.json`. Sheets: Summary, Area objects, Engineering limitations; include source SHA256, object category/property, preview nodes/tag, checked geometry and unapproved status. Only use **Write reviewed area-stage call** after engineering review and choose floor/wall toggles to prevent duplication.

## Separate slab load path / mesh size 4, 8, 16

`floor_subdivisions=N` in `OpenSees_Complete_Model_Config_V118.json` is the **number of divisions per source floor-panel direction**. **N is not an element width in millimetres and not the total number of elements per floor.** Under regular quadrilaterals, N×N cells would result per source panel before conforming shared mesh constraints. Irregular geometry and adjoining lines can change actual count. Each N changes the discrete shell mesh and potentially element/node count, connected split-beam frame segments, stiffness matrix bandwidth, convergence, forces and runtime.

**How:** In **Slab vertical load path / mesh and formula audit**, choose **Prepare MESH_04 / MESH_08 / MESH_16 configurations**. The operation writes **separate, non-executed** configuration JSON snapshots in `02_MODEL/SLAB_LOAD_PATH/PREPARED_CONFIGS`. For each N, make a separate export/case folder and supply the N-specific config to its model build. Rebuild the complete assembled model (this must update its recorded config SHA256), run **identical full gravity load case and physical supports** and save independent solved evidence. Only then use **Export verified current mesh workbook**, writing:
- `02_MODEL/SLAB_LOAD_PATH/MESH_04/excel/Slab_Load_Path_MESH_04_V141.xlsx` (likewise 08/16)
- `02_MODEL/SLAB_LOAD_PATH/MESH_04/json/Slab_Load_Path_MESH_04_MANIFEST.json` (likewise 08/16).

**Safety:** The export rejects any config hash mismatch between current config and assembled model, and any N outside 4/8/16. The workbook is a **formula and connectivity audit**, not the reaction/moment result for a different mesh. The new configuration snapshots are NOT a batch solve. Do not merely change N and re-export; the stale assembled model is invalid for that N. Existing legacy V141 files remain untouched.

**Next numerical validation (not yet automated by this change):** For each same EDB and same physical case, compare total assembled load, reaction sum/individual mapped supports and six-DOF supports, shell edge reactions, beam moments and shears, shell deflection, total vertical strain energy and maximum/minimum principal stress. Quantify \(\delta_{4\rightarrow8}=|Q_8-Q_4|/|Q_8|\), \(\delta_{8\rightarrow16}=|Q_{16}-Q_8|/|Q_{16}|\) per quantity; avoid a universal acceptance threshold without an engineering decision and ETABS reference. Explicitly identify signed q, load pattern, geometry and source load type (uniform shell vs uniform-to-frame). An elastic shell mesh-convergence study cannot validate nonlinear wall fibers.

## Vertical gravity load path (explain why the two modules differ)

For an eligible affine shell cell of area A carrying uniform downward pressure q, the consistent nodal total is qA, and each of its four corners receives qA/4; separate shape functions govern how assembled stiffness then distributes nodal forces through slab bending, shared beam nodes, column/wall nodes, and foundation reactions. Non-parallelogram geometries require \(\int N_i q\,dA\) rather than presuming equal shares. A rigid in-plane diaphragm constrains UX/UY/RZ but not UZ or out-of-plane slab bending. The normal full-model gravity path is already in `assembly.py`; the area-integration helper adds ELEMENTS ONLY. **Never add a second tributary beam UDL for the same shell load.**

`Slab_Load_Path_MESH_NN_V141.xlsx` is algebraic provenance: area, q, modifiers, mass factors, assigned node shares and topology. It is not a direct member-force recovery. Solver beam end actions and measured foundation responses must be independently exported after a completed gravity solve.

## Engineering source and current known limitations

- CSI ETABS [Analysis Reference](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf): area loading, shell objects, auto-mesh mechanics
- OpenSees [ShellMITC4](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html) and [rigidDiaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html)
- Kolozvari, Lopez & Massone (2023), *Engineering Structures* 294, 116700, DOI [10.1016/j.engstruct.2023.116700](https://doi.org/10.1016/j.engstruct.2023.116700), wall-panel model. Not calibration for this project's reinforcement.
- Compare `REVIEW_MAIN/01_GRAVITY/20261112_MESH_SUPPORT_AND_SLAB_TRANSFER_VALIDATION.md` for unresolved 32/76/97 support and auto mesh issues.

**Open gates:** source ETABS-to-OpenSees object/analysis joint equivalence, explicit mesh edge compatibility for openings, full gravity load balance (1D+1L) vs code-specific earthquake preload and seismic mass, joint-volume/beam-offset conventions, 4/8/16 native solved comparisons, M45 confinement/rebar and FSAM specimen calibration, site Vs30 and earthquake-history acceptance. The new code does not close them.
