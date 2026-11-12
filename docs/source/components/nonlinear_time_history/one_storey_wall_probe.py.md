# First-storey wall-QUAD isolation diagnostic — 2026-11-12

**Scope:** New **Run 1st-storey wall-QUAD diagnostic (NOT full floor)** button in the *Building nonlinear research history* GUI. The program selects an **actual first-storey 4-node SHEAR WALL mesh element** from the existing `OpenSees_Complete_Model_Data_V118.json`, writes a source SHA256 manifest and attempts a small-load 10-increment nonlinear OpenSeesPy single-element static test. Results are in a new `ONE_STOREY_WALL_QUAD_YYYYMMDD_HHMMSS` folder. If E-SFI/FSAM or the solver fails, write `FAILED` with error; do not fabricate a successful response. No original EDB/export is modified.

## What this IS and IS NOT

This is the smallest reproducible **one-storey wall panel** extracted from the selected building, not the complete first floor. It excludes adjacent elements, walls, perforations, columns, beams, vertical tributary gravity, damping, spectral inputs and earthquake records. The lower two panel nodes are fixed for the test; these are **not** accepted project foundation boundary conditions. Upper nodes receive an artificial small monotonic lateral load; there is no representative building axial load or cyclic history. The smoke test addresses numerical element/material implementation and source-geometry mapping only. It cannot be used to infer E-SFI wall yield, damage or overall building behavior.

A complete one-storey *structural subassembly* trial will subsequently require cut-interface conditions, tributary mass/gravity, upper-storey force transfer, diaphragm constraints, adjacent beams and 3D wall/core continuity; isolating the first floor by deleting the 24 upper storeys **without equivalent boundary actions would be mechanically incorrect**. Do not call this a completed one-storey building NLTHA or a material calibration.

## Core literature and exact provenance

1. **Kolozvari, Kristijan; Orakcal, Kutay; Wallace, John W. (2015).** *Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading*. **PEER Report 2015/12**, Pacific Earthquake Engineering Research Center, University of California, Berkeley, December 2015. Appendix B.3, printed pp. 90–91: RW-A15-P10-S78 wall-web ConcreteCM and SteelMPF source card. Permanent PEER source: https://peer.berkeley.edu/publications/2015-12 . PDF https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf . **DOI not found/present for this PEER report; do not invent one.**
2. **Kolozvari, Kristijan; López, Carlos N.; Massone, Leonardo M. (2023).** *Efficient Three-dimensional Shear-flexure Interaction Model for Reinforced Concrete Walls*. **Engineering Structures**, 294, 116700. DOI: **10.1016/j.engstruct.2023.116700**. This is the **E-SFI-MVLEM-3D 24-DOF element formulation**, *not* a source of the full 2015 RC specimen material card. https://doi.org/10.1016/j.engstruct.2023.116700 and https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html .
3. Optional external comparison only: **Kolozvari & Wallace (2016)**, *Practical Nonlinear Modeling of Reinforced Concrete Structural Walls*, **ASCE Journal of Structural Engineering** 142(12), DOI **10.1061/(ASCE)ST.1943-541X.0001492**. This is **not a source** for our numeric baseline or experimental material values.

## Exact source-card values used

| Family | Parameter | Value (source card) | Provenance |
|---|---|---:|---|
| ConcreteCM (unconfined web) | fpcc | −55.7785865 MPa | PEER Appendix B.3 |
| ConcreteCM | epcc | −0.002371 | PEER Appendix B.3 |
| ConcreteCM | Ec | 37253.8712 MPa | PEER Appendix B.3 |
| ConcreteCM | rc / xcrn | 15 / 1.022 | PEER Appendix B.3 |
| ConcreteCM | ft / et / rt / xcrp | 2.31524571 MPa / 0.00008 / 1.2 / 10000 | PEER Appendix B.3 |
| SteelMPF web | fyp = fyn | 402.724842 MPa | PEER Appendix B.3 |
| SteelMPF web | E0 | 199947.9615 MPa | PEER Appendix B.3 |
| SteelMPF web | bp = bn / R0 | 0.02 / 20 | PEER Appendix B.3 |
| SteelMPF | printed transition a1=18.5, a2=0.0015 | OpenSees cR1=**0.925** = 18.5 / 20; cR2=0.0015 | Mathematical conversion between differently normalized transition equations; source printed value retained in provenance |
| Panel FSAM | assumed rho_x / rho_y | 0.0074 / 0.0074 | Existing research **PATCH assumption**, not verified project reinforcement |
| Panel FSAM | nu / alpha | 0.8 / 0.01 | Existing research **FSAM PATCH** data, separate from E-SFI element Poisson |
| E-SFI element | out-of-plane Poisson / CoR / ThickMod | 0.25 / 0.4 / 0.63 | Separate E-SFI element/formulation values, **not** claimed to be PEER 2015 B.3 specimen values |
| Stress conversion | MPa → kN/m² | ×1000 exactly once | kN–m–s model units |

Source cards are `Material_Catalog/PEER_Web_ConcreteCM.json`, `PEER_Web_SteelMPF.json`, `PEER_Web_ESFI_Patch.json`. They describe one specimen/research setup and mixed 3D modeling assumptions; they do not determine the user's actual project concrete grade, rebar arrangement, confinement, original FVD device specification, SHS Fy/E, or structural damping.

## Model and numerical sequence

1. Read source JSON and SHA256; select smallest physical base-elevation rectangular 4-node shear-wall quad with two bottom and two top nodes, consistent width and same thickness from the source.
2. Form OpenSees `model('basic','-ndm',3,'-ndf',6)`; place selected nodes at **relative coordinates** preserving source dimensions.
3. Define PEER ConcreteCM and SteelMPF in kN/m²; use two FSAM fibers and E-SFI-MVLEM-3D element. The native OpenSees element may require a custom build; a missing command causes **FAILED**, not a silently substituted alternative element.
4. Fix base pair; use two equal artificial lateral loads at top; perform 10 nominal force-controlled increments with Newton and UmfPack; record finite displacement; store every accepted result, or exact error if failed.
5. Write `One_Storey_Wall_Probe_Inputs.json` and `One_Storey_Wall_Probe_Result.json`. A `NUMERICAL_PROBE_COMPLETE_NOT_PROJECT_VALIDATED` status means only this idealized isolated panel solve converged. No assertion of experimental match, physical capacity or NLTHA code acceptance follows.
6. One-at-a-time material sensitivity for **full-building exploratory runs** is already present separately in `components/nonlinear_time_history/building_exploratory.py`. Always vary one parameter while all other recorded settings, mass, dt and motion stay fixed. Existing 0.9/1.0/1.1 candidate brackets are **analyst-selected**, not uncertainty bounds reported by PEER. Separate baseline and sensitivity runs must use same source SHA and report cases, peak/drift/energy metrics.

## Why the production NLTHA GUI said material file MISSING

`components/nonlinear_time_history/research_building_materials.py::define_building_materials` dynamically defines PEER specimen/assumed materials **inside the exploratory builder**. The **production** `OpenSees_Complete_Model_Config_V118.json` still has `nonlinear_parameters_reviewed=false`, no `nonlinear_materials_file` and no approved `nonlinear_wall_fsam_tags`. That status is correctly **unapproved** and must not be overwritten simply because a 0.1-second numerical trial finished.

The *Nonlinear model readiness* GUI now distinguishes missing **production** assignments from existing exploratory material evidence and offers **Create isolated PEER 2015/12 material/FSAM draft (not approval)**. That action writes `Research_Wall_Materials.py`, `Research_Wall_Parameters.json` and copied config under a new separate diagnostics folder, keeping production export and EDB untouched. Any reinforcement ratios based on the historical two-curtain 20-mm/200-mm pattern are explicitly **assumptions**; replace from verified project drawings before interpreting the draft physically. It never checks `nonlinear_parameters_reviewed=true` or signs off an NLTHA manifest.

## Evidence gates still OPEN

- Native Windows OpenSees test of this exact one-panel routine (CI only tests source selection and provenance; the full 3D element may be unavailable in stock OpenSeesPy).
- First-floor correct load boundary and 3D wall/coupling/opening connectivity; no one-storey whole-building analogue yet.
- Experimental cyclic comparison against the PEER specimen itself; a research-literature input is **not** calibration.
- Project-specific reinforcement, wall confinement, slab beam load path, bracing, damper and P-Delta qualification.
- Full 45.29-s Kobe/Hector or other complete record run and XY/YX sensitivity convergence; the user's 0.1-s result is `TRUNCATED_DIAGNOSTIC` even though it accepted 21 time samples.
- Initial tangent eigenperiods should be measured on the nonlinear domain at the reviewed gravity equilibrium; the user's trial 2.21147-s first eigenperiod is **not** the adopted NBC empirical/Rayleigh period and is not Tn90.
