# Module 01 — 13 Nov 2026 export 02: ETABS→OpenSees evidence review

**Date:** 2026-11-13 | **Status:** `CONVERSION_COMPLETED / ANALYSIS_NOT_READY / PHYSICS_NOT_VALIDATED`  
**Model context:** selected local export folder `ETABS 11-13-2026/2`; **public repository contains only source-safe summary and no raw private model files**.
**Source provenance:** user-provided conversion log, V118 model review summary, readiness suggestions and screenshots; the actual ETABS .EDB, native analysis cases, and full exported files were not executed by this reviewer.
**Governing code:** NBC 105:2025 seismic analysis, spectra, loads and checks; the adopted compulsory initial EQ P-Delta combination is IS 16700:2023 §7.2(d), and conventional slab flexural modifiers are IS Table 5. Both IS excerpts remain subject to BIS 2025 amendment verification.

## WHAT — reported source vs assembled state

- EDB SHA256: `8d09a2367fcdf17f969c77226d17a8668ab7989122aea59f6328aabbca9434bc`; this matches the earlier `20261113_EXPORT_01` audit. Distinct *export folders* do not automatically mean different source EDBs.
- Source units requested by ETABS API: **kN–m–C**. Extracted: 25 stories, 95 m; 1,101 ETABS points, 1,367 frames, 725 areas, 0 links. Frame source groups: 805 beams + 450 columns + 112 braces = 1,367; area groups: 350 floors + 375 shear walls = 725.
- Mapped source topology: all 1,367 frame endpoints, all 725 area polygons. 2,092 preview/source element tags are **not** 2,092 assembled OpenSees solver elements; actual expanded assembly reports 11,072 nodes, 3,862 frame segments, 10,400 shell elements and 25 diaphragm groups. A preview tag and solver tag can differ and can represent one-to-many splits.
- Sections: 1,312 / 1,367 frames returned nonempty assignment. **55 undefined API assignments** require raw return codes and exact element-role identification; do not silently assume they are links, trusses or harmless objects. Area assignments 725/725, two distinct area properties.
- 25 diaphragm master groups with 32 structural node memberships each (800 total). Only 25/1,101 explicitly assigned named ETABS point diaphragms; auto-derived membership/meshing and actual rigid-diaphragm constraints require comparison to original ETABS solver.
- 76 source base nodes at Z=0 fully fixed in exported model. `SOURCE_ONLY` wall base policy added **zero** extra auto-mesh support nodes; ETABS shell-edge restraint propagation is not proven equivalent.
- Frame brace hinged release/zero torsional-transfer warning for numerous source frame IDs (e.g. 1308–1388): document I/J My/Mz and torsional releases and test numerical hinge behavior. `NONLINEAR` hinge realization is still gated.
- 350 uniformly loaded ETABS areas expanded to 1,050 load-pattern area components; 750 distributed wall-frame loads; parser skipped 0. ETABS area-object load query reported no assignments, **distinct** from successful assignment-table load extraction; verify complete load-pattern assignments and specifically inspect point, temperature, prestress, link, and non-uniform actions rather than equating 0 API object records with no load.
- ETABS self-weight multiplier: `Self Weight=1`; other source patterns report 0. Preserve only one automatic geometric self-weight application and match native ETABS material density settings.
- Assembly reported `assembly_errors=[]` and `elastic_assembled=true`, but explicitly `analysis_ready=false`, `nonlinear_ready=false`, `nonlinear_parameters_reviewed=false`, `nonlinear_materials_file=""`, `nonlinear_wall_fsam_tags={}`.

## WEIGHTS — do not mix purposes (kN)

| Source pattern | Applied gravity |
|---|---:|
| Self Weight | 209,919.758231 |
| Wall | 26,100.000000 |
| Floor Finish | 18,000.000000 |
| Partition | 18,000.000000 |
| Live (configured factor 0.30) | 14,400.000000 |
| **Total downward assembled gravity** | **286,419.758231** |

- `total_seismic_weight_including_fixed_nodes_kN = 286,419.758231`, and `active_horizontal_seismic_weight_kN = 284,691.556185`. The 1,728.202046 kN difference is related to how *active* versus *fixed-node* mass/weight is reported and **not proof of an error or acceptance**. Compare 25-storey mass and ETABS mass source independently, including restrained nodes and diaphragm rotational mass/inertia.
- The same factor table (`Live=0.3`, `Roof Live=0`) appears in `gravity_factors` and `mass_factors`. This does **not** establish correct source dead/imposed-load classifications, nor does it make the full 1D+1L gravity test equal to NBC §5.2 seismic gravity.
- The earlier export folder `/1` reported the same source EDB SHA, source counts and 286,419.758 kN. The earlier full-gravity comparison near 311,367.314 kN pertains to **different applied load case factors**; do not treat its difference as ETABS mismatch without identical case definition.
- Beam self-weight `GROSS_SECTION_LENGTH` reported 750 beams, gross 53,984.05488 kN, possible clear-length reduction 8,652.44435 kN, **not applied**. Overlap estimate 19,358.52745 kN is **AUDIT_ONLY_NOT_APPLIED**, based on unverified assumed geometry. Neither candidate correction is to be deducted automatically or combined.
- Slab: `floor_subdivisions=4`; conventional slab bending factor 0.25 ULS and 0.35 SLS, from IS 16700 Table 5 project source. Preserve physical weight from physical slab thickness and separate membrane EA. Mesh 8 and 16 require separately built/case-bound solver comparisons, not rebadged formula exports.
- Core walls use gross elastic in-plane stiffness pending rational NBC Table 3-1 cracked-wall EI implementation and ETABS equivalence. A 0.25 *slab* factor does not supply wall stiffness reduction.

## HOW — bottleneck prioritization (do not prematurely run NLTHA)

| Priority | Gate | Exact evidence / action | Ownership |
|---|---|---|---|
| P0 | Actual ETABS gravity/mass parity | Obtain original ETABS story-by-pattern gravity, matching reactions at each mapped foundation support, native mass source by storey, 76 restraints and their wall-auto-mesh equivalents; compare same SHA/state/load factors | Structural researcher / independent checker |
| P0 | Nonlinear frame/wall materials | Obtain project reinforcement schedules and actual sections, material test data, wall thickness, boundaries, confinement, web steel, axial load; map ConcreteCM+SteelMPF+FSAM tags; run member/wall cyclic benchmarks | Materials engineer |
| P0 | Signed P-Delta cases | Independently solve X±, Y± initial EQ P-Delta per adopted IS §7.2(d), with **EL derived under NBC 105**; record reaction balance and consistent tangent/state transfer; do not hold static EL on top of full ground motion by default | Earthquake engineer |
| P0 | Opening, coupling beam, braces | Inspect all 3D core openings and column/wall/beam junction DOFs, brace I/J releases, local axes, mesh edge compatibility, missing section assignments and nonlinear element duplication | FE reviewer |
| P1 | Nonlinear device strategy | Either mark FVD/BRB disabled for a specified source scenario or provide independently benchmarked K/Cd/alpha, yield/cyclic/stroke/core-area data, placement and units | Researcher |
| P1 | Rayleigh and device damping | Select physical initial-state modal band, calibrate αM/βK, quantify damping mode-by-mode and separate material/device dissipation | Numerical reviewer |
| P1 | Seismic record integrity | Source hashes and pair indices, dt, total record length, acceleration units, exact factor 9.80665 once, NBC matching/scaling and XY/YX directions | Record reviewer |
| P1 | Run proof | Fresh-domain gravity → ZERO/X/Y/XY first-step response → long complete NLTHA and demand/energy validation. No partial 0.1s trial as full history | Numerical reviewer |
| P2 | Numerical performance & organized outputs | Instrument native solver build/grav/transient timing; status UI should say `NO FILE DISCOVERED IN SEARCHED LOCATIONS` not `analysis never run`; use case names and SHA in manifests | Software engineer |

## WHEN / WHERE — next evidence pack

Do NOT copy entire private `/2` export into public GitHub. Package only requested redacted evidence into a private/reviewable ZIP with source hash and case-bound manifest:
```
RUN02_EVIDENCE/
  00_SOURCE_MANIFEST/PROJECT_CONTEXT.json
  01_IMPORT/OpenSees_Complete_Export_Report_V118.json
  01_IMPORT/OpenSees_Section_Assignment_Audit.csv
  01_IMPORT/OpenSees_Area_Section_Assignment_Audit.csv
  01_IMPORT/OpenSees_Load_Conversion_Audit.json
  02_MODEL/OpenSees_Complete_Model_Config_V118.json
  02_MODEL/LOAD_PATH_AND_DIAPHRAGM_AUDIT_V130.json
  03_GRAVITY/ETABS_Native_Gravity_Reactions.csv
  03_GRAVITY/OPENSEES_76_Support_Reactions.csv
  04_NONLINEAR/Reviewed_Project_Materials.json
  04_NONLINEAR/Member_Wall_Benchmark_Report.json
  05_RUN_LOGS/ETABS_OpenSees_Conversion_Log.txt
```
Paths in this block are a **proposed copy-only evidence structure**, not claimed current output files. Keep original generated file locations unchanged until every caller and result reader has been migrated and tested. For absent files, explicitly record `NOT_YET_PRODUCED`.

## WHY — code and model interpretation

The entire ESM, MRSM, LTH, NLTHA and seismic combination workflow is NBC 105:2025. Its §§8.1.1.2/.3 and 9.3.1.2/.3 require appropriate §5.2 gravity and P-Delta, respectively. Under the user's declared project basis, compulsory signed initial EQ P-Delta cases use IS 16700:2023 §7.2(d) as the gap-filling initial combination, while only conventional slab bending uses IS Table 5 values. All other IS checks are separately marked supplemental and cannot override NBC seismic acceptance. The base IS source has a recorded 2025 amendment requiring verification.

## References

- [NBC 105:2025 official PDF](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
- [IS 16700 amendment and clause provenance](../../../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md)
- [OpenSees ShellMITC4](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html)
- [OpenSees loadConst](https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html)
- [OpenSees PDelta geometric transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html)
- [PEER Tall Buildings Initiative Guidelines (2017)](https://peer.berkeley.edu/sites/default/files/publications/tbi-working-group-led-by-co-chairs-ron-hamburger-and-jack-moehle_10.9.2017.pdf)
- [Prior source-identical Export 01 review](../20261113_EXPORT_01/01_IMPORT_FINDINGS.md)

**Bottom line:** Imported connectivity and selected load components are reported complete. **No native structural equivalence or nonlinear component calibration has been demonstrated.** Preserve distinction between `CONVERSION_COMPLETED`, `ELASTIC_ASSEMBLED`, `GRAVITY_SOLVED`, `MATERIAL_VALIDATED`, and `NBC_ACCEPTED`.
