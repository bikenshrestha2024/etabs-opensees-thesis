# Conventional steel-brace buckling, collapse and cold-formed HSS experimental data — 17 November 2026

**Status:** Research and source-audit review. **NO structural-model parameter or code change, NO native OpenSees/Abaqus/ETABS execution, and NO thesis acceptance gate passed by this review.** Authoritative engineering decisions are in `REVIEW_MAIN/06_NONLINEAR_TH/20261117_STEEL_BRACE_ARCHIVE_PARAMETER_TRANSFER_GATES.md`.

## Exact source identity

| Source read | Bibliography and DOI | What was inspected |
| --- | --- | --- |
| User-uploaded `uriz2008.pdf`, SHA-256 `a87846fe633fb9a04a22897c3f9f93a373ed3c6f89754ff197e5920d8034751a` | Uriz, P., Filippou, F. C., & Mahin, S. A. (2008), **Model for Cyclic Inelastic Buckling of Steel Braces**, *ASCE Journal of Structural Engineering*, 134(4), 619–628. https://doi.org/10.1061/(ASCE)0733-9445(2008)134:4(619) | All ten uploaded pages; geometry, Fig. 5/6 convergence and conclusions |
| User-uploaded `karamanci2014.pdf`, SHA-256 `4dccbb801b88c7615669aa141e20858515ee5b1243ea1514e6d2f7eeb5f4d4b8` | Karamanci, E., & Lignos, D. G. (2014), **Computational Approach for Collapse Assessment of Concentrically Braced Frames in Seismic Regions**, *ASCE Journal of Structural Engineering*, 140(8), A4014019. https://doi.org/10.1061/(ASCE)ST.1943-541X.0001011 | All 15 uploaded pages, Table 1 (page 5), fatigue equations, damping/collapse analysis on pp10–13 |
| User-uploaded `archive (1).zip`, SHA-256 `087fb4647344d07833f542475c71cb0c4d64b1f62b59cb44435cc1ad5cc99d46` | Morrison, M., & Wilson, L. (2026), **Cyclic Behavior and Constitutive Modeling of Cold-Formed Structural Steel Used in Hollow Structural Sections — Experimental Dataset**, Zenodo, v1. https://doi.org/10.5281/zenodo.22087404 | Full ZIP inventory, **all 55 CSV files and 1,145,745 numeric rows parsed**, all nine bundled PDFs opened/inspected, README, BB measured thickness note, `CM.f90` source-level inspection |

**Source caveat:** the archive README calls its related journal article *forthcoming*. The dataset DOI and license are supplied in the README; do **not** invent a final journal volume, DOI or source-calibrated high-rise design coefficient. The dataset claims CC BY 4.0; the two ASCE article PDFs are separate copyright works and are **not** uploaded here.

## Uriz–Filippou–Mahin (2008): actual finding and boundary

A conventional brace was represented by **force-based, distributed-plasticity fiber beam-columns** in a **corotational** large-displacement geometric transformation. The tested fiber steel law used Menegotto–Pinto-type cyclic hardening, which permits material and section axial–bending interaction. The paper reports economical **two-element-per-brace**, **0.05–0.1% of member-length initial midspan camber**, and **three section integration points per element** for studied compact brace *global force–displacement loops* (paper p10). A fiber representation of about **10–15 section layers**, including **3–5 flange layers where relevant**, is discussed. The sensitivity studies on pp4–6 distinguish **global loop agreement** from much more mesh-sensitive **local maximum curvature and fiber strains**, particularly under unequal end restraints.

The paper's **Fig. 14** shows that an unmodified fiber model with cross-section-shape preservation does **not** capture pronounced local wall buckling and repeated-cycle compression deterioration for a noncompact HSS. It does not independently calibrate low-cycle-fatigue fracture. **No universal two-element proof exists for critical fracture strain, all boundary conditions, noncompact square HSS or a 25-storey asymmetric outrigger.**

## Karamanci–Lignos (2014): actual finding and boundary

The paper studies a **12-storey special concentrically braced steel frame** (SCBF), not a reinforced-concrete core plus fluid-viscous damped outrigger. It adds fatigue/fracture, column and gusset-connection deterioration and P–Delta instability to a conventional steel-brace response model. A source-fit fatigue relationship is `epsilon_i = epsilon_0 (N_f)^m`, with `m=-0.300` as a representative calibration. For **rectangular/square HSS**, Eq. (4), paper p4, is:

```
epsilon_0 = 0.291 (kL/r)^(-0.484) (w/t)^(-0.613) (E/Fy)^(0.303)
```

**Published calibration-domain limitations:** `27 <= kL/r <= 85`, `4.20 <= w/t <= 30.40`, `223 <= Fy <= 532 MPa`, `R²=0.493`, logarithmic standard error `0.249`. The source Table 1 (p5) presents **eight displacement-based brace segments with five integration points** for an alternate calibrated modeling arrangement and average Menegotto–Pinto parameters (`b=0.001`, `R0=22`, `cR1=0.925`, `cR2=0.25` for its rectangular HSS sample). The paper also discusses **two force-based elements** but notes that an eight-segment displacement-based representation can be useful if force-based analysis has convergence difficulty. **Do not combine Uriz's two-element/three-point and Karamanci's eight-segment/five-point values as if the sources agreed on one mandatory scheme.** Compare them in a specimen-level sensitivity study.

The 2014 work demonstrates (pp10–12) that initial-stiffness-proportional **Rayleigh damping on severely degraded braces** can produce fictitious viscous resistance and **overestimate** the steel frame's collapse capacity. Its proposed remedy has element/geometry/tangent assumptions and is **not a drop-in validated OpenSees command** for this thesis. For the thesis compare true FVD device work, structural inherent-damping work and brace/RC hysteresis **separately**. The paper's sidesway-collapse discussion couples drift, remaining story shear and destabilizing P–Delta, not a single drift threshold. These CBF collapse parameters cannot be accepted directly for the 25-storey RC/asymmetric model.

## Uploaded archive: exact inventory

The ZIP has **97 total entries**, **67 files** excluding directory records: **55 experimental CSVs**, **four specimen-drawing PDFs**, **four protocol-plot PDFs**, an **eight-page numerical formulation PDF**, **one 647-line Abaqus UMAT source**, README and a BB thickness measurement note. All nine embedded PDFs were opened page-by-page; the four protocol PDFs comprise **51 specimen protocol-plot pages**. The drawing PDFs contain specimen geometry/fixture information not interchangeable between types.

| Specimen family | Files | Exact CSV columns | Interpretation |
| --- | ---: | --- | --- |
| BB — buckling brace | 4 | `disp(inch),force(kips),r` | Full conventional HSS steel member force–deformation loops |
| CNS — circumferentially notched | 14 | `disp(in),force(kip),r` | Notch fracture/coupon response; **not** global brace force |
| GP — grooved plate | 5 | `t(s),disp(in),force(kip),r` | Local grooved-coupon cyclic response |
| MC-C — corner coupon | 8 | `t(s),etrue,strue(ksi),r` | Cold-formed HSS **corner** true stress–strain |
| MC-W — wall coupon | 24 | `t(s),etrue,strue(ksi),r` | Cold-formed HSS **flat wall** true stress–strain |

The four **no-heat-treatment (NHT)** nominal section families are **4×4×¼, 4×4×⅜, 4×4×5/16 and 5×5×⅜ inches**, far smaller than the thesis's recorded **SHS 350×350×16 mm** outrigger section. Their steel grade, cold-forming history, welds, corner radius, exact flat width, bracing effective length, gusset restraint and hysteresis are **not** an automatic match to the building. Unit conversion references: 1 inch = 25.4 mm; 1 kip = 4.448221615 kN; 1 ksi = 6.894757293 MPa. Never conflate **true** coupon stress/strain with **engineering** strain or global axial extension.

**Complete 55-CSV numeric inspection result:** 1,145,745 rows; zero empty files, missing cells, nonnumeric/nonfinite cells, negative/fractional loading-ramp indices, ramp-order reversals or ramp jumps >1. This is a numeric-integrity screen **not proof of instrumental accuracy, constitutive calibration or complete validated fracture datasets**. The private per-file manifest contains member SHA-256, schema, row count, ranges and QC flags. It is not copied as raw measurements to public GitHub.

### Two real archive consistency warnings

1. `experimental/docs/measurements/BB.txt` references **`./data/BB/4x4x516-NHT/spec03`** for 0.293 in wall thickness, but the archived specimen is **`spec02.csv`** in that section folder. Another note gives 0.2927 in for `spec02`. Do not silently reassign the conflicting measured thickness; seek lab attribution.
2. `experimental/data/MC-C/4x4x14-NHT/SRC31.csv` has **three decreasing time values** in source data **lines 18210–18212** at ramp 20: `1174.38 → 729.396 → 105.824 → 0.191426 s`. Time-series strain-rate and cycle-energy calculations must flag/segment this interval, **not guess replacement timestamps**. Strain and stress channels have finite values there.

### Technical appendix and Fortran source

`numerical/CM-implementation-formulation-and-optimization.pdf` documents an **Abaqus** 3D rate-independent J2 elasto-plastic model with multiple back-stresses, isotropic/kinematic hardening, memory-surface evolution, an incrementally **corotated stress basis**, semi-implicit scalar return mapping and algorithmic tangent. That UMAT corotation is **not** equivalent to a structural beam-column corotational transform. `CM.f90` uses Abaqus/Standard and Intel MKL; the archive README prescribes Abaqus 2024, Intel oneAPI/ifx, `.for` filename and `/free` compilation. With source `nb=2`, the README requires **20 material properties**, **33 state variables** and two UVARM outputs. **This is not an OpenSeesPy or XARA material or a BRB/FVD model**.

A separate source-review flag: **`CM.f90::delete_empty_log`** declares `line_count` but increments it without a visible initialization. In portable Fortran this is an uninitialized local variable. The suggested compiler `/Qinit=zero` might mask the problem in that environment. This is a *log maintenance* helper; it is **not an observed material-constitutive failure**. Original Fortran remains untouched, compilation/tests absent.

## Thesis applicability and protection gates

**Current documented building implementation** (`docs/OUTRIGGER_MATERIAL_SENSITIVITY_AND_VALIDATION.md`) uses **Steel01 + corotational axial truss** for ordinary steel outriggers with nominal **Fy 345 MPa, b=0.01**. It is an **axial plasticity idealization without flexural brace buckling, local HSS wall buckling, fracture, gusset slip or low-cycle fatigue**. A corotational *truss* does **not** become a corotational *fiber brace beam-column*. Uriz offers an **additional controlled exploratory conventional brace model**, not a silent baseline replacement. Karamanci offers fatigue and damping hypotheses to test after specimen calibration.

| Proposed experiment | Needed observation and acceptance | Boundary |
| --- | --- | --- |
| B0 — source QC and units | Resolve BB thickness reference, SRC31 time reset, test specimen dimensions, 55 member SHA and recorded ramp; preserve original files | Numeric parsing **PASS**, two source metadata warnings **OPEN** |
| B1 — cyclic steel coupon | MC-C vs MC-W stress/strain envelopes, initial E, cyclic hardening, residual offset, repeatability, uncertainty | **NOT RUN**; not Fe500 bar or proprietary BRB |
| B2 — conventional brace fiber benchmark | One valid BB specimen + actual gusset geometry; 2/4/8 segments, 3/5/7 integration points, 0.05/0.1% camber, pin/fixed sensitivity, full axial hysteresis/curvature/energy | **NOT RUN**; no source-calibrated project SHS yet |
| B3 — optional fatigue law | Karamanci domain checks, actual fiber strain histories, Coffin–Manson/rainflow and fracture versus same specimen; noncompact wall buckling limitations | **NOT RUN**; never transfer directly to BRB |
| B4 — actual SHS 350×350×16 | Source steel grade, actual flat width/corner radii, welding, effective length, gusset end restraint, elastic force balance | **NOT RUN**; paper regression trained on different cross sections |
| B5 — damping & devices | Rayleigh force/work, FVD physical work and brace hysteretic work separated; C/alpha dimensional equivalence and element local axes | **NOT RUN**; no FVD coefficients in any of the three sources |
| B6 — source parity and building histories | First resolve original ETABS analytical support 32/76/97 and X-wall 110280 failure, then compare optional brace physics with unchanged baseline M0–M6, **224 full XY/YX** runs | **NOT RUN**; native ETABS/OpenSees needed |

**Source-only decision:** Paper and uploaded-data applications **DOCUMENTED**; archive member integrity **SCREENED**, raw records unchanged. No new structural model, UMAT port, material calibration, native 32/76/97 reaction validation, wall convergence fix, BRB/FVD property qualification, or M0–M6 numerical results have been produced or accepted. Keep engineering acceptance gates OPEN.

## Copyright and provenance

Source PDFs from ASCE remain user-provided references and are **not** committed. Raw CC BY 4.0 archive dataset files are retained privately to avoid unnecessarily publishing 1.1 million experimental observations. The authored summary and engineering decisions here are distributable; publicly link to **the original dataset DOI** and **publisher DOIs**, with correct author attribution.
