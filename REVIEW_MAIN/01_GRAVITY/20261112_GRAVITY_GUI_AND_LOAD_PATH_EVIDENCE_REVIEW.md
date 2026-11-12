# 2026-11-12 — Native gravity load-path evidence, source conventions and GUI review

**Case:** `GRAVITY_1.0D_1.0L`, ULS Floor 3 25-storey ETABS export, 32/76/97 restrained-node alternatives.  
**Review ID:** RV-GRV-004 / RV-GRV-001 (cross-reference), status **GLOBAL_VERTICAL_EQUILIBRIUM_VERIFIED / SOURCE_LEDGER_RECONCILED / INDIVIDUAL ETABS REACTION & LOAD-PATH EQUIVALENCE NOT VERIFIED**.  
**Priority:** P0 structural acceptance, P1 interface/traceability.  
**Scope:** read-only native evidence verification and user-facing GUI ergonomics. This review does not alter EDB, ETABS analysis mesh, OpenSees loads/stiffness, material properties or accepted source motions.

## 1. What was independently inspected

New user-uploaded archives `Gravity_Review_UPLOAD(5).zip`, `Comparisons_Review_UPLOAD(5).zip`, `ALL_MODULES_Review_UPLOAD(5).zip`, as supplied 2026-11-12, including:
- `Gravity/Analysis/Gravity_Reaction_Diagnostic/20261112_222234_066314/Gravity_Result_V110.json`, `Gravity_Source_Components_Audit.json`, `Primary_32_ETABS_OpenSees_Reactions.csv/.xlsx/.json`, `ETABS_Nonzero_Reaction_Support_Audit.json`, joint weight audit tables and action PDFs.
- `Gravity/Analysis/Gravity_Native_Equivalence_Preflight/20261112_223108_650345/GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json`, original support-DOF and end-zone stiffness CSVs.
- `Comparisons/Analysis/Gravity_Case_Comparison/Case_Comparison.json`, `Support_Reactions_32_76_97.csv`, displacement CSV, PDF and XLSX.
- `Comparisons/Analysis/Gravity_Wall_Base_Comparison/20261112_222410_861696/Gravity_Wall_Base_Strategy_Comparison.json/.xlsx` and independent support cases.
- `ALL_MODULES` is an aggregation of above categories, NOT an independent third physical model run. These private archives were used for analysis only; **do not push raw archives to public GitHub**.

## 2. Quantified results and meaning

| Case | Support treatment | Load (kN) | Sum Rz (kN) | Min Uz (mm) | Governing interpretation |
|---|---|---:|---:|---:|---|
| 32 | ETABS_NONZERO_REACTION_DIAGNOSTIC; **releases 44 of 76 original fixed joints** | 311367.31387955 | 311367.31387955 | −21.01764547 | Source-DOF-invalid for direct ETABS equivalence until proven otherwise |
| **76** | ETABS_SOURCE_SUPPORTS; all 76 source-fixed joints preserved | 311367.31387955 | 311367.31387955 | −20.73773530 | Preferred *source support reference*, not proven native ETABS mesh matching |
| 97 | CONTINUOUS_WALL_BASE_FIXED; 21 additional shell base joints fixed | 311367.31387955 | 311367.31387955 | −20.73223852 | Idealized sensitivity, not ETABS native default |

The exact 32-support run reports equilibrium error `1.869421e-14%` and `frozen=True`. Native ETABS global FZ reported as `311367.313600` kN, difference `0.00027955` kN versus OpenSees: **global load resultant agreement only**.

From the supplied `Support_Reactions_32_76_97.csv`:
- 32 vs 76 support cases: 32 common nodes, **maximum absolute common-node reaction redistribution 13,955.374 kN** at OpenSees nodes 36 and 41; mean absolute difference across 32 common nodes **3,264.469 kN**.
- 76 vs 97: 76 common nodes, **maximum absolute change 1,690.231 kN** (nodes 68, 9, 12, 65 among the largest); mean absolute difference across 76 common nodes **395.161 kN**.
- The 32-point ETABS versus OpenSees reaction audit reports worst single difference **3,041.266 kN** at OpenSees nodes 36/41, ETABS IDs 263/264, roughly **20.62%** against their corresponding ETABS force.

**None of these local reaction differences is fixed by matching total Rz**: global balance is a scalar necessary condition, not a uniqueness/equivalence test for the stiffness matrix, shell membrane/bending transfer, constraints, diaphragm or support selection. The 76- and 97-support displacement comparison shows a small max Uz difference of `5.49678e-6 m`, but localized reaction differences persist.

## 3. What load source has been checked

From `Gravity_Source_Components_Audit.json`:
- `Self Weight = 201267.313879` kN; `Live = 48000` kN; `Floor Finish = 18000` kN; `Partition = 18000` kN; `Wall = 26100` kN. Total `311367.313879` kN.
- Source components: slab area loads `84000` kN, frame loads `26100` kN, beam self-weight `45331.610528` kN, brace `1280.758352`, column `56733.867675`, slab shell `44986.7124`, shear-wall shell `52934.364924` kN.
- Beam policy already uses `ETABS_BEAM_CLEAR_LENGTH` with `750` native beam objects. Original gross candidate `53984.054880` kN and beam end-offset candidate `8652.444352` kN explain the previous **historical gross-beam gap**; the new case has no 8652-kN global gap to fix again.
- A separate geometric junction-overlap estimate `19358.527452` kN comes from limited axis-aligned intersection hypotheses, with a mixture of beam/column/slab/wall ownership. **Do not subtract the 19,358.53-kN junction hypothesis or add it to the 8,652.44-kN beam offset**. The source report itself identifies unsupported rotated/eccentric geometries. Verify native ETABS's analysis-element volume/weights and model-owner accounting.
- `Gravity_Native_Equivalence_Preflight.json` has `engineering_acceptance=NOT_VALIDATED`, exactly **76 source vertically restrained joints**, 32 diagnostic joints and 44 released original restraints, and **1367 native frame offset records** still requiring an equivalent OpenSees stiffness transformation. Zero missing offset metadata is not proof of matching end-zone stiffness.

**Load purpose:** This is the project's full gravity comparison with 1.0D + 1.0L and assigned roof live where present; seismic weight uses NBC 105:2025 §5.2 Table 5-1 (D 1.0, storage live 0.6, other live 0.3, roof live 0). Do not compare the 311367-kN full gravity response directly to the ~286420-kN seismic-preload case.

## 4. Why shell load path remains unverified

CSI ETABS internally converts object-based geometry to a refined analysis mesh. ETABS uniform shell loads are distributed to its **analysis-element corner joints**, and joint reactions are a function of the assembled stiffness, constraints, connectivity and support reactions. ETABS end offsets are a separate topic from rigid-zone factors; the former define physical end locations/output station positions, while the latter alter beam/column bending and shear flexibility. OpenSees nodal loads or ShellMITC4 can be mechanically reasonable substitutes only if the model's **connected mesh, DOFs, load transfer, end offsets, supports, element formulation, mass and diaphragm** reproduce the source idealization.

The exported material/beam quantity proof improves *load source accounting* but does **not** prove ETABS analysis mesh connectivity/auto-mesh edge restraint propagation or ETABS frame internal axial/bending stiffness. The 32-support solution has physically removed restraints and can never be declared equivalent merely because the matching ETABS display lists zero reaction there.

**What is NOT established:** wall-to-slab/beam edge sharing versus tied/equalDOF interfaces; internal ETABS meshed joint constraints and rigid diaphragm projection; source shell section property modifiers and thickness; frame end stiffness, rigid end factor, insertion offsets and local axes; six DOF support reactions with identical coordinate origins; independent load-path element force balances at each interface.

## 5. Smallest safe next physical validation sequence (P0)

1. **Freeze source fingerprint:** original EDB SHA, exported JSON+config SHA, original assignment/source workbook SHA and exact 1.0D+1.0L case. Record 32/76/97 case model paths separately. No source file overwrites.
2. **Use 76 native source restraints for initial parity test.** Extract ETABS analytical model joints, auto-mesh shell corner-to-frame connectivity, all restraint DOFs (including zero reaction nodes), diaphragm constraints and six-component joint reactions for a single full-gravity case. Do not use the 32 reduced supports as acceptance baseline, or 97 as the default native ETABS replica.
3. **One gravity floor and one beam–slab–wall edge:** compare native joint/load assignment under a unit pressure (1 kN/m²) and unit line load (1 kN/m); sum element forces and joint reactions locally, not only total base Rz; compare shell bending/membrane thickness, share/connectivity. Test a slab meshed shell with and without connected frame, and a core wall strip with correct boundary restraints.
4. **Offsets and member forces:** from ETABS extract frame analysis end offsets, rigid-zone fractions, section assigned modifiers, insertion point, local axes, point/line load station ranges; apply mechanically equivalent OpenSees offsets (not merely clear self-weight length), then compare N, V2, V3, T, M2, M3 at *matching faces/stations*. Use the 1367 per-frame records to locate differences.
5. **All foundation nodes:** join ETABS/OPS by original ETABS analysis-joint IDs plus XYZ tolerance. Compare FX/FY/FZ/MX/MY/MZ per node; include 44 originally restrained but zero reaction-bearing nodes. Report absolute kN, normalized errors, force/moment equilibrium with one common origin.
6. **Only after like-for-like parity:** test the full 25-storey gravity reaction distribution and floor/mass distribution; document accepted thresholds in advance; keep 32/97 as sensitivity. Repeat for seismic gravity preload with correct NBC factors and P-Delta initial state.

For local verification, carry the response through `ops.reactions()` before querying `ops.nodeReaction(tag,dof)`, confirm reaction coordinate/sign convention, and include all transformed constraint forces. A nonzero joint response at a node that ETABS displays as zero is diagnostic of a mapping or stiffness/support difference, not license to delete the joint.

## 6. GUI changes — process versus engineering status

**When:** opening Gravity Analysis, plotting saved cases, running solver, exporting all member actions or viewing logs. **Why:** screenshots show three horizontal rows of competing actions, no visible independent vertical Run Log scrollbar, and a single state line mixed with acceptance claims.

**Implemented on this review branch:**
- Action commands preserved and grouped into **Review saved results**, **Verify ETABS and load path**, **Reports and evidence**. No duplicate plot-selection action outside the plot's own toolbar.
- `RUNNING` uses blue foreground/light-blue background, `FINISHED` green and `BLOCKED` red. A separate label states **PROCESS STATUS ONLY — ETABS equivalence not inferred**. Existing indeterminate progress remains. Colors are paired with text (not color-only status).
- Run Log now has always-present vertical/horizontal scrollbars, full-log copy and `Scroll to start` / `Scroll to latest`. Existing saved output folder, logs and ZIP commands are unchanged.
- Existing output indexing for each 32/76/97 run remains untouched; **no completed case is silently promoted to physically validated**.
- Tk Windows high-DPI and exporter-worker behavior still require a native desktop test; CI is a static contract plus compilation check, not a visual screenshot test.

## 7. Source/citation index (manufacturer/official software documentation)

The following are **software manuals, not journal papers**: DOI and citation counts are **NOT APPLICABLE**. Do not invent DOI/citation counts. For copyrighted CSI documents, link to the official freely readable URL; **do not redistribute PDF binaries in this public repo**.

| ID | Owner / title | Source | Engineering use |
|---|---|---|---|
| ETABS-M01 | Computers & Structures, Inc., *CSI Analysis Reference Manual*, ETABS 2016 (July 2016), Ch. IV (restraints/reactions), Ch. V (constraints), Ch. VII (frame), Ch. X (shell loading) | https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf | Defines how physical objects become analytical joints, shell uniform loads to corner joints and frame end offsets |
| ETABS-M02 | Computers & Structures, Inc., *Frame End Length Offset* user help | https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm | Distinguishes end offsets from rigid zone factor and face-of-support output stations |
| ETABS-M03 | Computers & Structures, Inc., *Welcome to ETABS* (official PDF) | https://docs.csiamerica.com/manuals/etabs/Welcome%20to%20ETABS.pdf | Objects → automatically meshed analysis model |
| OS-M01 | OpenSees/OpenSeesPy, *eleLoad Command* | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html | Local beam distributed load is a reference elemental load and requires correct axes |
| OS-M02 | OpenSees, *Rigid Diaphragm* | https://openseesdocumentation.readthedocs.io/en/latest/user/manual/model/mp_constraint/rigidDiaphragm.html | Three-dimensional in-plane rigid constraint, 6 DOF nodes and transformation treatment |
| OS-M03 | OpenSeesPy, *Gravity column example (loadConst and LoadControl)* | https://openseespydoc.readthedocs.io/en/latest/src/columneq.html | Correct gravity ramp and freezing loads before dynamics |
| OS-M04 | OpenSeesPy, *reactions and nodeReaction commands* | https://openseespydoc.readthedocs.io/en/latest/src/reactions.html , https://openseespydoc.readthedocs.io/en/latest/src/nodeReaction.html | Assemble total reactions before per-node query; use exact coordinate and DOF sign |

These are verifiable official and project documentation resources, not proof of model-specific calculations.

## 8. Companion artifacts and evidence grouping

**Source-native, not recreated as authoritative values:** the user-supplied archives contain companion `.xlsx`, `.pdf`, `.csv`, `.json` and `.png` files (explicit names above). Keep them in their original evidence folders with manifest/ SHA; the all-modules ZIP is a grouped duplicate. The original selected source file and 32/76/97 results must remain separate.

**Useful local audit workbook/PDF:** `Gravity_Load_Path_Review_20261112.xlsx` and `Gravity_Load_Path_Review_20261112.pdf` can be generated from the same supplied saved evidence, with separate sheets for case summaries, source load ledger, per-node reaction deltas and outstanding gates. They are **independent companion review reports**, not native ETABS or solver replacement outputs. Do not commit private result binaries to public GitHub.

**Conclusions:** RV-GRV-001 SUPPORT_REACTION_EQUIVALENCE **OPEN / BLOCKED**; RV-GRV-002 GLOBAL_LOAD_AMOUNT_RECONCILED, local routing **OPEN / BLOCKED**; RV-GRV-003 boundary-condition sensitivity **COMPLETE AS DIAGNOSTIC**; RV-GRV-004 GUI navigation improvement **IMPLEMENTED / WINDOWS CHECK PENDING**.
