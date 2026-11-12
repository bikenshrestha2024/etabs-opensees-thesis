# 12 November 2026 — Gravity support boundary conditions, load path and output review

**Review status:** SUPPLIED SOLVED EVIDENCE AUDITED / 76 SOURCE RESTRAINTS REFERENCE / NATIVE ETABS RESPONSE EQUIVALENCE OPEN.  
No original EDB, Excel workbook, model loads, mesh, element stiffness, or proprietary analysis evidence altered. This is a technical interpretation and small GUI-default correction, **not** certified ETABS/OpenSees equivalence.

## Source evidence (2026-11-12 upload)
- `Case_Comparison.json` — all 32/76/97 solves completed under `GRAVITY_1.0D_1.0L`, same applied load, 11,097 common nodes; classifications `SOLVER_EQUILIBRIUM_ONLY_NOT_ETABS_EQUIVALENCE`.
- `Support_Reactions_32_76_97.csv` — 97 unique support tags; 32, 76, 97 nonempty reaction values by case.
- `Common_Node_Displacements_32_76_97.csv`; `Gravity_32_76_97_Comparison.pdf` and PNG.
- `Gravity_Review_UPLOAD(3).zip` — 62 files (56.15 MiB expanded; 22.21 MiB ZIP).
- `Comparisons_Review_UPLOAD(3).zip` — 182 files (120.73 MiB expanded; 49.14 MiB ZIP).
- `ALL_MODULES_Review_UPLOAD(3).zip` — 242 files (176.70 MiB expanded; 71.34 MiB ZIP). Contains previous two evidence categories **again**; do not count as an independent fourth analysis.
- Preflight `GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json` (within Gravity review) flags source vertical restrained count 76; 32 primary reactions selected by nonzero ETABS FZ; 44 restraints removed by diagnostic run; rigid-end zone stiffness unresolved.

## Support-case structural meaning

| Case | Source DOFs | Extra mesh DOFs | Applied kN | Sum Rz kN | Maximum downward Uz (mm) | Status |
|---|---|---|---:|---:|---:|---|
| 32 = ETABS_NONZERO_REACTION_DIAGNOSTIC | **Releases 44 originally restrained nodes** | 0 | 311,367.31387955 | 311,367.31387955 | 21.01764547 | Boundary-condition diagnostic, NOT ETABS replica |
| **76 = ETABS_SOURCE_SUPPORTS** | **Retains all 76 source-export restraints** | 0 | 311,367.31387955 | 311,367.31387955 | 20.73773530 | Primary source-geometry restraint candidate; validate native ETABS DOFs |
| 97 = CONTINUOUS_WALL_BASE_FIXED | All 76 | **Fixes 21 further base shell-mesh nodes** | 311,367.31387955 | 311,367.31387955 | 20.73223852 | Artificial continuous wall-base sensitivity; NOT native ETABS default |

**Critical correction:** The original 44 intermediate points are recorded with full source-restraint DOF string `111111` and ETABS point IDs. They are not simply unrestrained OpenSees-only points that can be ignored because their selected ETABS case reaction is zero. Original automatic wall-mesh restraint propagation must be confirmed through ETABS analysis mesh and source-export tables. See CSI ETABS Wall Auto Mesh Options, “Add Restraints/Constraints on Edge if Corners have Restraints/Constraints”: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm . ETABS restraint DOFs: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Joint/Restraints_Joints.htm .

### Individual reactions — enormous redistribution despite global balance

From the actual uploaded three-case reaction CSV:
- The **44 nodes excluded from the 32-case support set** carry **104,463.013534 kN** in the 76-case solve, **33.55% of total gravity reaction**.
- The 32 common “main” nodes carry **206,904.300346 kN** in the 76-case solve, but all **311,367.313880 kN** after the other 44 source restraints are released in the 32-case solve.
- The single largest change at a common node between cases 32 and 76 is **13,955.374177 kN at OpenSees tag 41** (absolute difference). Thus a small difference in maximum storey shortening is **not** evidence of comparable foundation load distribution.
- In the 97-case, the **21 additional fixed mesh nodes** carry **30,032.220953 kN**, about **9.65% of the common applied total**. Among all original 76 common nodes, largest reaction change from 76 to 97 is **1,690.231218 kN at tag 68**.
- The 21 added tags are 8751/8752/8753, 9544/9545/9546, 10453/10457/10463/10504/11888/11892, 12383/12387/12393/12409/12919/12923, 13509/13510/13511; all have z=0 along the wall-base planes. Additional fixed support number 97 is a user-configured modeling idealization, not “ETABS auto mesh equals fixed”.
- All three satisfy global `sum Rz = applied` with negligible numerical residual. These are separate boundary-value problems, so equilibrium alone proves no ETABS physical matching.

## Global applied-load ledger

Source evidence: uploaded `Gravity_Source_Components_Audit.json` and native beam quantity audit.

| Pattern or component | Load kN |
|---|---:|
| Self Weight (beam, column, wall, floor and brace) | 201,267.313879 |
| Floor Finish | 18,000 |
| Partition | 18,000 |
| Wall | 26,100 |
| Live (1.0) | 48,000 |
| **Total 1.0D + 1.0L** | **311,367.313880** |

Self-weight breakdown: beam **45,331.610528**, column **56,733.867675**, shear wall **52,934.364924**, floor **44,986.712400**, brace **1,280.758352** kN. Sum ~201,267.313879 kN.
Reported native ETABS FZ = **311,367.313600 kN**; absolute global difference **0.00027955 kN**. This strongly verifies *reported global load sum*, not individual node reactions, shell-to-beam load path, local end actions or rigid offset stiffness.

`ETABS_BEAM_CLEAR_LENGTH` policy has already been selected and the native beam quantities reported as `SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH`, with 750 source beam objects and **8,652.444352 kN** gross-vs-clear-length offset weight difference. Do NOT apply another subtraction. The separately computed geometric-overlap **19,358.527452 kN** is explicitly `AUDIT_ONLY`, and the two values are **mutually exclusive hypotheses**, not additive gravity corrections. Source weight matches the ETABS reaction sum already. Native per-object geometric union proof and stiffness transformation still open.

## Load-path theory and validation targets

**ETABS:** official CSI Floor Auto Mesh Options document confirms meshing at beams and wall edges assists load distribution. CSI Shell FAQ distinguishes `Uniform (Shell)` loads, which transfer through connecting shell joints, from `Uniform to Frame (Shell)`, which creates loads on the surrounding frame members under prescribed one-/two-way distribution. These are different mathematical models, and a transfer “floor to beam” must not be assumed twice. 
- https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Floor_Auto_Mesh_Options.htm
- https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2001188/Shell%2BFAQ

**OpenSees:** ShellMITC4 slab shell transmits loads through its shell nodes and their shared DOFs/constraints. The element or consistent nodal loading must be checked; equivalent slab load should **not** also be duplicated as an imposed beam line load. `SurfaceLoad` applies pressure via energetically conjugate forces at shared shell nodes and adds no stiffness; `eleLoad -beamUniform` is for actual beam distributed loads, not a second copy of a shell pressure.
- https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/SurfaceLoad.html
- https://opensees.github.io/OpenSeesDocumentation/user/manual/model/eleLoad.html

**Rigid diaphragm** `rigidDiaphragm(3, retained, ...)` enforces in-plane UX/UY/RZ relations, not vertical UZ equality; it does NOT by itself enforce shell-to-beam vertical compatibility or complete gravity load transfer. Verify actual shared joint IDs, wall/shell/frame DOFs and constraints. 
- https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html

Required deterministic tests: (1) isolated single slab panel uniform load with shell-only and equivalent beams, independent reaction + internal force checks; (2) shell-to-beam edge joint sharing and gravity displacements; (3) slab-to-wall edge transfer under the same point constraints; (4) entire story’s tributary gravity and live patterns independently summed; (5) six-DOF support correspondence, rigid offsets and actual wall base integration; (6) matched gravity case, stiffness, self-weight flags, local force orientation, shell shear, individual reactions and resulting ETABS/OpenSees modal periods.

**Code requirements**: NBC 105:2025 governs seismic mass and combination definitions; general modeling and load path need applicable reinforced-concrete and structural analysis provisions and actual element verification. None of the referenced codes certify a particular Python load-assignment conversion automatically.

## Filesystem layout / disk footprint review

The current per-project module folders `00_SOURCE_MANIFEST`, `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TH`, `07_NONLINEAR_TH`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES` are created by `components/inputs/project_output_layout.py`. The older active writers still put actual artifacts under `OpenSees_Analysis_Results/<state_model>` and an independent `Verified_Clear_Beam_* ` runtime/export root. An empty `02_GRAVITY` folder is thus **not** proof that gravity did not run. Do not move / overwrite old results until all existing readers/launchers/tests have been migrated. Display **NO_MAPPED_RESULT** or **NOT_RUN**, not “Unavailable case”, until a traceable index connects the new module root and exact existing original artifact.

The three uploaded review ZIPs contain repeated SOURCE DATA from the same 32/76/97 solves, not three separate independent run sets. On source disk, large JSON/XLSX/PNG/PDF outputs exist for EACH solved strategy and duplicated organized ZIP snapshots; retaining immutable scientific originals is reasonable but redundant copies add significant storage. The uploaded ZIPs collectively encode ~56.15+120.73+176.70 MiB of uncompressed data, with the all-module bundle containing the two subordinate bundles. This **does not verify the reported ~2 GiB** of local Windows disk usage: a real recursive on-disk size report is necessary before deleting any original, ZIP, or related backup. Safe cleanup policy: retain one authoritative raw run per model/case fingerprint, preserve original manifests/checksums, create deduplicated reference-only review packages as opt-in and move only demonstrably duplicate *derived* previews to archive after user review; never silently delete or rename raw engineering evidence.

## ESM Rayleigh period visibility

The current ESM GUI already contains `_run_rayleigh` / `Preliminary Rayleigh run (X/Y)` with source-state and both-axis preflight checks. It is a **directional period** method, not Rayleigh damping. The action was hidden near the bottom on smaller screens; a second button adjacent to X/Y Rayleigh period entries has now been added. Selected Aw=2.073174515 m² X, 2.203080332 m² Y is validated from exported wall geometry; this does not create `T_{Rayleigh}`. Both ULS/SLS must use matching source stiffness and state; do not substitute ETABS eigenperiod as a Rayleigh period without explicitly documenting a different basis.

## Disposition and remaining gates

**CLOSED AS SOURCE-EVIDENCE FACT:** 32 vs 76 vs 97 support counts and differences, first-order load ledger, gross-vs-clear beam offset policy already applied, data routing location and missing on-screen Rayleigh control.

**OPEN_HIGH:** 32-case released source restraints, source-native ETABS point-DOF crosswalk, individual support reactions, rigid-end-zone stiffness, actual shell/frame/shared-node load transfer, calibrated wall behavior and genuine native model identity.

**OPEN_WORKFLOW:** direct ETABS assignment / full compressed table loading during fresh converter session, unified module-to-active-result output index, and bounded disk footprint/deduplication plan. No changes to physics or file deletions are permitted until native evidence tests establish equivalence.

**NEVER CONCLUDE:** “ETABS equivalent” solely from 311,367.31388kN matching global sum or from a converged gravity solve.
