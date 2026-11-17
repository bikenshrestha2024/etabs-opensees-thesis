# 2026-11-17 — targeted NLTHA semantic audit: Steel02, FSAM, wall tangent, literature

**Disposition:** confirmed P1 invalid transition override corrected with tests; source-accurate research-only candidate matrix added. **This is a targeted source review**, not a whole-repository manual function-by-function audit or an engineering certification.

## 0. Inventory, dependency path, and file roles

Canonical repository-wide inventory is `tools/audit_repository_integrated.py` and its CI artifacts in `audit/integrated/`; don't create another root-level repository scanner. Critical active path traced:

```text
NLTHA/Material study configuration
 -> components/nonlinear_time_history/material_source_sets.py
 -> components/nonlinear_time_history/research_building_materials.py
 -> components/sections/definitions.py (frame Concrete01, Steel02)
 -> components/nonlinear_time_history/first_step_transition.py
 -> components/nonlinear_time_history/failure_evidence.py
 -> components/nonlinear_time_history/runner_and_gui.py
```

The actual wall material route uses ConcreteCM / SteelMPF / FSAM with `E_SFI_MVLEM_3D`, **not** frame Steel02. Paper-based Steel02 shape sensitivity cannot be claimed to validate wall FSAM first-step response unless a separate tested wall-material mapping is implemented. `Material_Catalog/M30_Fe500_Steel02.json` is a nominal Fe500 research card, not project coupon data.

Snapshots in Saved_Project, Research_Components and historical Verification directories remain provenance-only; they were not executed or rewritten. Existing output stages, 4×4 geometry and 32/76/97 supports remain unchanged.

## 1. Confirmed source inconsistency: unbounded normalized transition cR1

**P1 MATERIAL-NL-001 (reproducible, software validation):** `research_building_materials.MATERIAL_OVERRIDE_BOUNDS` allowed `frame.steel_cR1` and `wall.cR1` up to **50**. Existing repository source already documents a prior NaN on the first reversal when an absolute Menegotto–Pinto a1=18.5 was passed directly as cR1 rather than normalized using cR1=a1/R0=.925. As a result, a user could accidentally reintroduce that unsafe value through material sensitivity overrides.

**Correction:** bounded both research overrides to `0 < cR1 < 1` and added direct frame-section validation on `steel_cR1`. This enforces the normalized transition used in the existing source and rejects an absolute a1 coefficient mistakenly passed to Steel02/SteelMPF. No valid baseline changes and no pretense that a cR1 bound alone cures a singular stiffness/mass model.

**Test:** `tests/test_steel02_carreno_reference.py` rejects both wall/frame overrides at 18.5, accepts .9, and rejects a directly assembled frame section at 18.5 before calling a numerical solver.

## 2. User-uploaded Carreño material paper: source and proposed study

- R. Carreño, K. H. Lotfizadeh, J. P. Conte, and J. I. Restrepo (2020), *Journal of Structural Engineering*, 146(2):04019205, DOI 10.1061/(ASCE)ST.1943-541X.0002505. User PDF pp. 14–16, Table 12 p.16, 36 Grade 60 coupons, ASTM A615/A706.
- A615 and A706 reference yield stresses (480/476 MPa) and postyield b (.02/.012) are **NOT** Fe500 source properties. Both paper profiles use E=202000 MPa, R0=20, cR1=.9, cR2=.08, a1=.039, a2=1, a3=.029, a4=1.
- Original `Material_Catalog/M30_Fe500_Steel02.json` is retained intact. Added `components/nonlinear_time_history/steel02_carreno_reference.py` to generate four research cases (nominal Fe500 existing; Fe500 *transition-shape-only* alternative; paper-exact A615; paper-exact A706) with original source/units, no auto-apply, no calibrated/design claim.
- **Important no-op:** `components/sections/definitions.py` frame Steel02 definition currently passes Fy, E0, b, R0, cR1, cR2 and **does not pass a1-a4**. The new paper references do NOT secretly activate isotropic hardening in your model. A separate native coupon/model feature and test is required if desired.

## 3. Latest published research: nonlinear wall tangent and dynamic validation

| Work (verification) | Source | Why relevant | Current transfer status |
| --- | --- | --- | --- |
| SFI-MVLEM tangent consistency (2026 institutional report and SSRN 4 Jun 2026 preprint; journal status unverified) | https://ir.canterbury.ac.nz/items/c9d2c5f8-31a8-496b-8916-b4874623bb80 ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6880782 | Proposed axial-shear coupled consistent tangent improvements to NL wall iterative convergence | Literature hypothesis only; not identified as installed in your E-SFI-MVLEM-3D build |
| Kolozvari, Lopez, Massone (2023), E-SFI-MVLEM-3D, DOI 10.1016/j.engstruct.2023.116700 | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html | Exact four-node FSAM macro-fiber 3D element syntax, 6 DOF, recorded globalForce/Curvature/ShearDef/RCPanel channels | Audit the compiled binding and element mapping before solver physics changes |
| Tura et al., LFSAFE model I (published online Mar 2025, volume 2026), DOI 10.1007/s10518-025-02148-3 | https://link.springer.com/article/10.1007/s10518-025-02148-3 | Independent dynamic RC wall benchmark, U-shaped wall and 10-storey wall-frame under multidirectional motions; discusses missing strain penetration/interface behavior | Benchmark option; **not** a drop-in E-SFI model replacement |
| PEER 2017/06, Tall Buildings Initiative v2.03 | https://peer.berkeley.edu/publications/2017-06 | Model verification, component behavior, ground-motion and tall-building acceptance | Supplemental engineering guidance, not automatically adopted Nepal code |
| NIST GCR 17-917-46v1, Guidelines for Nonlinear Structural Analysis and Design Part I | https://www.nehrp.gov/library/guidance_pbsd.htm | Analysis verification/modeling uncertainty workflow | Independent QA checklist, not a local mandatory standard |
| NIST/ASCE 41 benchmarking RC nonlinear procedures (2023) | https://www.nist.gov/publications/ascesei-41-assessment-reinforced-concrete-buildings-benchmarking-ascesei-41-nonlinear | Compare modeled damage to measured RC wall/frame response | Validate specimen/global demands; do not infer local failure just from displacement |

**Recency rule:** peer-reviewed published, open access, institutional research, preprint and guidance are recorded with their actual publication/status; 2026 SSRN is **not** treated as an officially adopted OpenSees patch. Citation counts not verified.

## 4. Regression and physics acceptance matrix

| Gate | Required evidence | Status |
| --- | --- | --- |
| S0 file inventory | Untruncated tracked Git tree and non-executing archive provenance | Existing integrated audit; rerun in PR CI |
| S1 source code | Exact paper profiles; finite units; invalid cR1 rejected; original Fe500 material card untouched | Implemented, pending exact-head CI |
| S2 runner and material | No accidental import or changes to SteelMPF/FSAM, no accepted failed steps | Production physics files unchanged; existing regression tests |
| S3 independent Steel02 | Native cyclic coupon loops in OpenSees with paper-matched protocol + independent Fe500 coupon | **NOT VERIFIED** |
| S4 first-step wall | Actual E-SFI wall tag, mass/constraints, zero vs motion, with/without eigen, first non-finite source | **NOT VERIFIED** |
| S5 structures | Exact ETABS vs OpenSees 32/76/97 supports, wall-base resultant, gravity mass and PDelta | **NOT VERIFIED** |
| S6 thesis NLTHA | Complete M0–M6 XY+YX, calibrated materials/damper devices, CBC/NBC method compliance | **NOT VERIFIED** |
| S7 secure release | Public source excludes user PDF, private EDB/Excel/result files, CI green, source guides present | PR gate; no copyrighted PDF uploaded |

**Next priorities:** (a) run deterministic baseline vs cR1 shape-only coupon experiments without inventing Fe500 cyclic calibration, (b) source-compiled E-SFI wall tangent/recorders check with a 4-node panel and specific element tag, (c) replay gravity+zero/motion+eigen 2×2 matrix, (d) analyze first native exception/UMFPACK pivot and finite mass before changing constitutive law, (e) validate 32/76/97 wall mesh support reaction equivalence and whole-building NLTHA. This finding does not establish the root cause of the 25-storey first-step error.
