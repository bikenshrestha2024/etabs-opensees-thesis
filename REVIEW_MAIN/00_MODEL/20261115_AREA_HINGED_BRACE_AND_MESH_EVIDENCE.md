# 2026-11-15 — hinged brace source releases, 4/8/16 slab-mesh evidence and area integration UI

## Boundaries and source artifacts

Sources inspected **locally only**, not committed: user PNG (Area Element Integration V116); `Pasted text(20261115-113708).txt`; `Model_Config_MESH_{04,08,16}(3).json`; the three supplied `Slab_Load_Path_MESH_..._V141.xlsx` workbooks; and `OpenSees_Material_Section_Library_20261115_173540.xlsx`. Existing active source inspected in `components/sections/area_elements.py` and `components/model/assembly.py` plus regression tests. No private EDB, private output or raw workbook has been uploaded to the repository.

## 1. What is the warning, exactly?

The supplied local converted elastic export records `elastic_assembled=true`, `assembly_errors=[]`, `total_downward_load_kN=286419.7582311328`, and `active_horizontal_seismic_weight_kN=284691.5561853357`. The pasted warning stream includes **112 distinct ETABS unique frame IDs**, from **1308 through 1423** with some omitted IDs. Example: ETABS frame `1308`, **topology preview** tag `25049`. Neither identifier is the assembled OpenSees solver tag.

The source implementation in `components/model/assembly.py` reads ETABS `GetReleases` arrays; acceptance of a special hinged brace is restricted to `BRACE` members with no U1/U2/U3 releases, R2/R3 released at both ends, at least one R1 release and no nonzero partial-fixity spring. This condition is a *source release pattern* — not proof of an actual pin/axial-only connection in the 3D building. The warning is deliberately appended before solver elements are fully assembled, so the text `solver tag pending assembly` **is not a numerical failure**.

The elastic converter currently constructs `elasticBeamColumn` with `-releasey/-releasez` codes, setting torsional `J=0` for a hinged brace; this retains an elastic numerical representation but needs independent stiffness/mode/reaction checks, especially rotational null modes and brace force equilibrium. The exploratory nonlinear route switches selected hinged braces to `corotTruss` with illustrative `Steel01` uniaxial properties. `corotTruss` is an axial-only large-displacement element; it does not automatically implement brace flexural buckling, local SHS wall instability, connection fracture, cyclic strength loss or BRB behavior. The **reviewed nonlinear route explicitly raises** on this unimplemented connection; bypassing it would falsify calibration readiness.

**Engineering judgement:** Do not treat the 112 warnings as 112 failing finite elements. Nor should they be suppressed: they identify 112 ETABS frame *source objects* needing exact connection/release and physical brace behavior review. Do not assume source BRACE members are all CO/BT/CT, or all have genuinely pinned axial-only connections. Compare as-built connection details and ETABS property/group classification separately from display names. A real FVD or BRB must be represented as a device with tested property and stroke/overstrength evidence, **not** as a generic SHS axial brace by default.

## 2. Code correction and what is not changed

- The report now includes `hinged_brace_release_review` with count, original **full GetReleases arrays**, ETABS unique frame ID, topology preview tag, actual solver segment tags in current frame assembly order, source category/section, elastic and exploratory assumption, and nonlinear blocker. This exposes the missing source evidence behind each repeated line instead of removing warnings. `solver_element_tags` are derived from real frame-segment order, never from preview tags.
- The **Area Element Integration V116** GUI has an `Open output folder` button. If the integration call was saved during this session, it opens that file's parent; otherwise it opens the existing `02_MODEL/AREA_INTEGRATION` inventory folder; if it has not been generated, it opens the existing export root. It creates no folders and runs no analysis, and shows an error for missing or linked output roots. Windows uses Explorer via `os.startfile`.
- No release matrices, stiffnesses, mass/weight factors, initial P-Delta loads, material grades or solver convergence criteria are changed.

## 3. Actual uploaded mesh evidence

| Supplied input | `floor_subdivisions` | Reported assembled shell cell count | Assembled config SHA256 in workbook | Status |
| --- | ---: | ---: | --- | --- |
| `Slab_Load_Path_MESH_04_20261115_172608_314810_V141.xlsx` | 4 | 10400 | `02200a800e2893b61ce9414435f634f79d16c3862be8d433b8cbc90bc1492653` | Formula/connection audit only; no native ETABS parity |
| `Slab_Load_Path_MESH_08_20261115_172947_296300_V141.xlsx` | 8 | 33100 | `624cc4fa79d219b567b5face01f4dfbd9feb47d61b7ddabdb3b5f02e3fb45499` | Formula/connection audit only; no native ETABS parity |
| `Slab_Load_Path_MESH_04_20261115_173457_949762_V141.xlsx` | 4 | 10400 | Same 04-config SHA above | Repeated 04-case snapshot, not a third mesh level |
| No 16 workbook supplied | 16 config provided | **NOT PROVIDED / NOT RUN** | n/a | Do not infer 16 results from config presence |

All three mesh configs have the *same* gravity/mass factors (0.3 Live, 0 Roof Live), `joint_volume_weight_policy=AUDIT_ONLY`, `etabs_beam_weight_policy=GROSS_SECTION_LENGTH`, `wall_base_restraint_policy=SOURCE_ONLY`, `nonlinear_parameters_reviewed=false`, blank nonlinear material file and empty wall FSAM tags. A 04/08/16 difference in mesh cell count without verifying native loads/reactions/deflections/periods and connectivity is not mesh convergence.

## 4. Materials workbook: strong separation of templates from project evidence

The supplied `OpenSees_Material_Section_Library_20261115_173540.xlsx` has tabs `00_README_PROVENANCE`, `Section formulations`, `Parameter values and citations`, `Current source parameters`, `Validation and limits`. `Current source parameters` records a 1100×1100 RC source column area 1.21 m² and E≈33.54102 million kN/m², whereas `Parameter values and citations` lists editable illustrative beam-cover 25 mm, tie diameter 12 mm, bar diameter 16 mm, bars-per-side 4, and an example M35-style material — **not extracted project reinforcement**. The `Validation and limits` tab confirms project M45 and reinforcement calibration not established; Kobe first-step failure remains an unresolved numerical issue. Do not promote this workbook into a calibrated solver material file simply because the table has references/parameter values.

## 5. Required next tests (engineering gates)

1. Export ETABS source `GetReleases` arrays and ETABS element group/section/geometry for **all 112** warned source IDs. Compare six DOFs at I/J and any partial springs. Identify actual BR normal, CO core-to-perimeter, BT belt and CT roof cap, and any true BRB/FVD as separate device class. Verify solver segment ID mapping, source length, insertion, local axes, and connection detail.
2. Member unit test: apply same axial tension and compression, transverse end shear/moment, nodal rotation, torsional test and geometric stiffness to ETABS and elastic OpenSees; compare forces, displacement, strain energy, modal nullity. Record tolerance and fail if axial-only conversion removes a legitimate bending/moment transfer path.
3. In reviewed nonlinear, choose and calibrate for **each verified physical class**: pin-ended ordinary elastic/truss, steel brace buckling+fracture, validated BRB hysteretic material/connection or FVD device. Document local/global buckling, cyclic backbone, hysteresis energy, strength degradation, stroke and signed axial response. Do not convert to `Steel01` as a universal solution.
4. For 04/08/16 mesh, rerun all three **actual** assembled models with distinct source/model/config SHA; store mesh edge/element quality, gravity vertical reaction per support, slab-to-beam force distribution, vertical deflection, natural frequencies, story seismic masses, and Wall opening/FSAM connectivity. Native 16 model is not supported by supplied workbook.
5. Reconcile 32 primary supports against 76 source restraints and optional 97-node diagnostic; no additional grounded restraint should be invented. Independent complete gravity 1.0D+1.0L vs 1.0D+0.3L seismic preload, then MRSM/ESM and signed initial P-Delta cases.
6. Wall cyclic panel/member benchmarks and calibrated ConcreteCM/SteelMPF/FSAM first, followed by constrained 1-bay/1-storey interface tests **with equivalent upper-structure actions**, then full record XY/YX M0–M6 NLTHA and time-step sensitivity. No completed full-history performance ranking yet.

## References (source/command syntax, not calibration)

- [CSI ETABS cFrameObj.SetReleases official documentation](https://docs.csiamerica.com/help-files/etabs-api-2016/html/967eb7da-6e42-0708-a4e9-00a61d506575.htm): six independent end DOFs U1, U2, U3, R1, R2, R3, and six partial-fixity spring values per end. The `GetReleases` source return must be inspected for each physical connection.
- [OpenSees elasticBeamColumn](https://openseesdocumentation.readthedocs.io/en/latest/user/manual/model/elements/elasticBeamColumn.html): independent y/z end releases; 0/1/2/3 codes; 3D torsional `GJ` argument.
- [OpenSees CorotationalTruss](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html): uniaxial material, large displacements, optional Rayleigh damping; not an automatic brace buckling/fracture law.
- [Kolozvari, Lopez and Massone (2023)](https://doi.org/10.1016/j.engstruct.2023.116700): E-SFI-MVLEM-3D wall methodology, not a calibration of this building's reinforcement.

**Acceptance**: software report/UI checks via exact PR CI; native ETABS/OpenSees and thesis engineering gates NOT_RUN.


## 6. Spreadsheet-formula granularity and evidence limitations

Further non-destructive workbook-level inspection confirmed:
- Both MESH_04 workbooks: `Surface load formulas` and `Surface seismic preload` each have **28,000 data rows** (sheet range A1:Q28001); `Member weight formulas` has **3,862 frame segment rows** (A1:I3863). Their source cell example for a 2.25 m² area uses Floor Finish 1.5 kN/m², Live 4 kN/m² and Partition 1.5 kN/m².
- MESH_08 workbook: those corresponding area-load sheets each have **113,600 data rows** (A1:Q113601); `Member weight formulas` has **7,162 frame segment rows** (A1:I7163). A sampled 0.5625 m² cell shares the same unit pressures, indicating smaller subdivision, not a separate loading case.
- Sampled `self_weight_floor` formulas use `=O5*P5*Q5`; sampled `Material unit formulas` use `=C2/1000`. These saved formula cells have no numeric cached result in the uploaded OOXML; independently calculating/cross-checking all thousands of rows is **NOT DONE**. The `Vertical load path` narrative explicitly states rigidDiaphragm(3) constrains UX/UY/RZ, **not UZ**, and warns against imposing a second beam tributary load on the same source shell area.
- No model stress/force or source-native ETABS support-reaction convergence evidence is contained in these identity rows. A spreadsheet with a 4-mesh/8-mesh formula sheet cannot prove slab bending force delivery, primary32 support equivalence or dynamic mesh convergence.

The material workbook contains five sheets and source E-modulus/property values, but representative beam cover 25 mm, tie 12 mm, longitudinal bar 16 mm and four bars per side are marked editable illustrations; **not** project as-built reinforcement. This review is a targeted header/sample/identity/formula inspection, not cell-by-cell recalculation of all large workbook sheets.
