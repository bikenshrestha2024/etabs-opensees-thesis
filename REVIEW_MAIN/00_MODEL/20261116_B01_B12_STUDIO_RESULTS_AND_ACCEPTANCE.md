# 2026-11-16 — Independent OpenSeesPy B01–B12 results and thesis acceptance boundary

**Evidence class:** USER-SUBMITTED NATIVE BENCHMARK REPORTS; not independently rerun by this review.
**Source:** uploaded per-case B01.json–B12.json, HTML and CSV from a single locally executed Verification Studio v2.1.0-single-file run.
**OpenSeesPy:** 3.8.0. **Reference comparison tolerance:** 1% (relative), as recorded in each per-case result.
**Studio source fingerprint recorded in all cases:** `ba4761bdb10f3c6fbdef14fa609a66b6cb2a8294bedd7e6dab67549af76442eb`.
**Privacy:** source reports and machine paths were NOT committed; this is a redacted scientific status record.

## Audited recorded outcomes

| Case | Scope | Recorded status | Metrics | Acceptance boundary |
| --- | --- | --- | ---: | --- |
| B01 | CSI Example 01 propped-beam component | PASS | 4 | Component only, not complete CSI model |
| B02 | Beam subdivision 1/2/4/8 | PASS | 11 | Elastic shared-node beam mechanics |
| B03 | Axial truss analytical comparison | PASS | 2 | Simple truss only |
| B04 | ShellMITC4 wall gravity equilibrium | PASS | 3 | Equilibrium, not deformation convergence |
| B05 | Approximate rigid-end zone | PASS | 3 | Not exact ETABS §7.10 implementation |
| B06 | 6x6 m slab + edge beam, MESH_04/08/16 | PASS | 15 | Equilibrium and symmetry only |
| B07 | Simplified wall on two columns | PASS | 3 | Symmetric 600 kN transfer |
| B08 | Wall with geometric opening | PASS | 3 | Geometry and static gravity, not cyclic wall |
| B09 | Simplified frame/wall parallel support sharing | PASS | 3 | 250/750 kN, not thesis support forces |
| B10 | Simple three-column frame | PASS | 2 | Gravity equilibrium; not entire CSI example |
| B11 | Single-DOF oscillator | PASS | 2 | Analytic eigenvalue and period only |
| B12 | Exponential FVD power-law | ANALYTICAL_PASS | 7 | Equation only; no native damper dynamics |

**Total:** 11 OpenSeesPy native component cases PASS, 1 analytical-only case PASS, 58/58 recorded metrics pass. No native ETABS rerun, full project match or materials calibration is implied.

## Additional quantitative checks

- B06 symmetric patch load: `6 m × 6 m × 1.5 kN/m² = 54 kN`; sums for meshes 4, 8 and 16 are nominally 54 kN. Each of the four symmetric supports carries nominally 13.5 kN.
- B06 vertical center displacement (m): 4x4 `-0.000375036479223`, 8x8 `-0.000391922171079`, 16x16 `-0.000396151202429`. Change from 8x8 to 16x16 is about 1.07% of 16x16 displacement, so the **displacement convergence acceptance gate is not established by B06's equilibrium metrics**. Continue dedicated grid convergence and source ETABS local force/displacement comparison.
- B04 1x1, 2x2, 4x4 wall force equilibrium is nominally 1200 kN; top vertical displacements vary. This does not validate lateral wall stiffness or cyclic/nonlinear behavior.
- B09 transfers 1000 kN into a simplified pair of supports as 250 kN (frame) and 750 kN (wall). This demonstrates a stiffness-sharing idealization, not correspondence to the 18 frame-only and 14 shell-only supports of the 25-storey model.
- B12 uses numerical example C=700, alpha=0.3 with declared coefficient dimensions for input velocities in m/s. This is not adoption or calibration of the research project's damper parameter.

## Implementation in main

- The complete standalone GUI/CLI has been kept in `tools/verification_studio/ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py`.
- The **model readiness desktop GUI** can launch the independent Studio without changing structural parameters or readiness status.
- `tools/verification_studio/import_verified_runs.py` verifies all 12 private case files and writes a **sanitized**, fail-closed consistency summary. It does not certify source ETABS equivalence.
- `tools/verification_studio/test_import_verified_runs.py` covers false PASS, missing cases, mixed source code, invalid numerical values, and status-type errors.
- CI runs **offline** source and report contract checks; user-submitted results remain separately recorded evidence.

## Next necessary engineering acceptance gates

1. Reproduce relevant CSI benchmark assemblies in native ETABS / native OpenSees and compare exact joint/output stations and force/moment vectors.
2. ETABS auto frame/shell mesh, wall edge constraints and beam end offsets must be traced to the exact EDB.
3. Compare MESH_04/08/16 beam forces, wall forces, slab path and displacement convergence on one ETABS-matched subassembly.
4. Reconcile the full 32-support mapped reactions and six global force/moment resultants; 76 and 97 remain deliberately distinct boundary sensitivity cases. Previously identified 18,648.51 kN frame/wall redistribution is **unresolved**.
5. Retain X-wall first-step NLTHA failure and full-record M0–M6 validation as independent P0 blockers.

**Acceptance:** `USER_SUBMITTED_COMPONENT_BENCHMARK_PASS` for B01–B11 and `ANALYTICAL_COMPONENT_PASS` for B12; `ETABS_OPENSEES_EQUIVALENCE_VERIFIED = false`; `THESIS_NLTHA_ACCEPTED = false`. Issue #75 remains open.
