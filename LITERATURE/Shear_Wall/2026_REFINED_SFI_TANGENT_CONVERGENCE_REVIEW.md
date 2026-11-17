# 2026 SFI-MVLEM tangent consistency literature — FIRST STEP NLTHA diagnostic relevance

## Publication status and source

**Source:** "Refinement of the SFI-MVLEM formulation for modelling Shear-Axial-Flexural interaction in RC shear walls", University of Canterbury institutional repository (2026): https://ir.canterbury.ac.nz/items/c9d2c5f8-31a8-496b-8916-b4874623bb80. Related preprint *A Refined SFI-MVLEM Formulation for Consistent Tangent Stiffness Representation of RC Shear Wall Behaviour*, SSRN manuscript posted 4 June 2026: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6880782. **Publication/review status:** institutional research output and preprint; do not silently describe as an adopted OpenSees release or verified peer-reviewed implementation. A verified journal DOI and reliable citation count were not established.

**Reported contribution (from research abstracts):** consistent tangent stiffness and enhanced axial-shear stress/strain coupling in the SFI-MVLEM family; aimed at reducing nonlinear iterative convergence problems. This speaks to possible nonconsistent tangent behavior, but the stated research formulation is **not proof** that the currently installed `E_SFI_MVLEM_3D` in OpenSees/XARA contains the refinement.

## Related validated modeling source

- Kolozvari, Lopez and Massone (2023), "Efficient Three-dimensional Shear-flexure Interaction Model for Reinforced Concrete Walls", *Engineering Structures* 294, 116700, DOI [10.1016/j.engstruct.2023.116700](https://doi.org/10.1016/j.engstruct.2023.116700). Official [E-SFI-MVLEM-3D element manual](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html) requires 3D, 6 DOF nodes; four nodes CCW, m FSAM macrofibers and width/thickness arrays. Its documented recorders: `globalForce`, `Curvature`, `ShearDef`, `RCPanel` responses. `localForce` support is **not listed** and may legitimately be empty/unsupported; a nonfinite response nevertheless requires readback and native reproduction.
- Tura, Orakcal, Gullu and Ilki (online 2025, volume 2026), "A new layered shell model for reinforced concrete walls I: model description and dynamic response simulations", *Bulletin of Earthquake Engineering*, DOI [10.1007/s10518-025-02148-3](https://doi.org/10.1007/s10518-025-02148-3). LFSAFE simulates multidirectional walls and a full-scale ten-storey wall-frame test, but is a **different model**; not a drop-in replacement for E-SFI.

## Engineering triage and acceptance

1. Before replacing material models, run existing `first_step_transition` and `one_storey_wall_probe` with exactly mapped wall tag 110280 and source config hash; confirm actual FSAM/ConcreteCM/SteelMPF and integration step.
2. Separate no-eigen/eigen and zero-motion/motion controls with identical gravity, damping zero and a fixed solver build. A failed linear solve with finite sampled wall response is not proof of bad tangent; inspect constraints, mass, solver pivot and element Jacobian.
3. For a source-matched wall coupon, compare alternative algorithms/line searches, force-displacement and tangent perturbations at **committed** states. Do not force a failed material state by accepting a nonzero `ops.analyze` return or replacing NaN with zero.
4. Before trying an external refined element, identify exact original and refined source commits, OpenSees binding version, constitutive specification, parameter/units compatibility, analytical benchmarks, solver consistency and regression results.
5. Preserve 25-storey source model, 4×4 meshing and 32/76/97 support interpretations until direct ETABS and OpenSees validation supports any physics changes.

**Current conclusion:** HIGH-PRIORITY RESEARCH HYPOTHESIS; **NO CAUSAL RESOLUTION OR COMPILED-ELEMENT VALIDATION**. Only reference/sensitivity documentation is added in this audit.
