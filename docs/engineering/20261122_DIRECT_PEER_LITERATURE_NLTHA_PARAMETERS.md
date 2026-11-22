# Direct literature-parameter adoption for thesis NLTHA — source, units and transfer policy

**Date:** 2026-11-22. **Methodological decision:** use **published numerical parameters as the initial constitutive-law research baseline**, then conduct one-at-a-time and selected joint sensitivity studies. Do **not** require the researcher to re-test every concrete, reinforcing-steel, FSAM and damper specimen before an exploratory thesis model can run. That is an explicit methodological choice, distinct from claiming that the literature specimen is the as-built structure.

**Model scope:** existing 25-storey asymmetric M0–M6 OpenSees model with 2×12 m X walls with openings, 3×6 m Y walls, 32 physical foundation supports and 44 additional wall-mesh transfer points. Neither literature data nor this code migration changes actual building geometry, 1.0D+1.0L comparison, NBC 105:2025 seismic mass, mesh connectivity, source EDB or measured reinforcement.

## Primary, directly inspected paper and extraction

**R01.** Kolozvari, K.; Orakcal, K.; Wallace, J. W. (2015), *Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading*, **PEER Report 2015/12**, **Appendix B.3, printed pp. 89–91**, specimen **RW-A15-P10-S78**. Original PDF: https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf ; alternate: https://apps.peer.berkeley.edu/publications/peer_reports/reports_2015/webPEER-2015-12-kolozvari.pdf .

**The original paper prints the following values in the source specimen's input file.** Do not attribute its full specimen cyclic validation to the 25-storey core. The report uses **ksi** for steel/concrete stresses and modulus in Appendix B.3. Source cards in `Material_Catalog/` already convert `1 ksi=6.894757293168 MPa` (dimensional conversion; small numerical rounding differences may occur). The project solver uses kN–m–s, so `1 MPa=1000 kN/m²` in actual material commands.

| Parameter / material | Published *as printed* | Applied research numerical value | Local software basis |
| --- | --- | --- | --- |
| Unconfined web concrete peak compression | `fpc=8.09 ksi` | `fpcc=-55.7785865 MPa` | `ConcreteCM` web, not boundary |
| Unconfined web concrete peak compressive strain | `ec0=-0.002371` | `epcc=-0.002371` | Dimensionless |
| Web concrete modulus | `Ec=5403.2172 ksi` | `Ec=37253.8712 MPa` | Material stiffness; not wall section cracking factor |
| Web concrete tensile stress | `ft=0.335798 ksi` | `ft=2.31524571 MPa` | Source `ConcreteCM` |
| Web concrete strain at tensile peak | `et=0.00008` | `et=0.00008` | Dimensionless |
| Web concrete compression shaping/cracking | `ru=15; xcrnu=1.022` | `rc=15; xcrn=1.022` | `ConcreteCM` |
| Web concrete tensile shaping/cracking | `rt=1.2; xcrp=10000` | `rt=1.2; xcrp=10000` | `ConcreteCM` |
| Steel web X/Y yield | `fyX=58.4103 ksi; fyYw=58.4103 ksi` | `fyp=fyn≈402.72484 MPa` | `SteelMPF` web |
| Steel web X/Y postyield ratios | `bx=0.02; byw=0.02` | `bp=bn=0.02` | `SteelMPF` |
| Steel modulus | `Esy=29000 ksi` | `E0≈199947.9615 MPa` | `SteelMPF` / transferred `Steel02` frame |
| Steel curvature terms | `R0=20; A1=18.5; A2=0.0015` | `R0=20; cR1=0.925; cR2=0.0015` | **Formula conversion** `cR1=A1/R0`, not arbitrary recalibration |
| FSAM web steel ratios | `rouXw=0.0074; rouYw=0.0074` | `rho_x=rho_y=0.0074` | **Adopted directly for all explicitly unconfined web research panels** |
| FSAM boundary steel ratios | `rouXb=0.0082; rouYb=0.0587` | Retained as separate boundary card | **NOT applied to all walls or guessed zone geometry** |
| FSAM shear transfer | `nu=0.8; alfadow=0.01` | `nu=0.8; alpha=0.01` | `FSAM` material inputs, not E-SFI element Poisson parameter |
| E-SFI/MVLEM reported region split in the source | 5 fiber columns across section (2 boundary, 3 web) | Source specimen **only** | Do not infer the same fiber widths and wall-boundary confinement for each 12 m building wall |

**Separate boundary materials in the same original source:** `fyYb=69.0 ksi`, `byb=0.005`; the confined concrete has `fpcc=10.479723 ksi`, `ec0c=-0.005873`, `Ecc=5953.9187 ksi`, `rc=12.072964`, `xcrnc=1.023`. A true confined boundary assignment must use *all* corresponding steel/concrete and FSAM region values together, plus a source-identified boundary zone. Selecting only the larger longitudinal ratio without those materials would not be a source-faithful paper transfer.

**Concrete/SteelMPF convention warning:** PEER's legacy `A1=18.5` is from an **absolute** curvature-decay term; the installed OpenSees formulation expects a normalized term. Thus `cR1=18.5/20=0.925`. Using `cR1=18.5` unchanged can produce a negative curvature parameter and invalid cyclic states. Keep `cR2=0.0015`, not `0.15` from a different example. This is a law-specific **parameter transformation**, not a material calibration.

## 3D formulation — separate publication

**R02.** Kolozvari, K., López, C., Massone, L. (2023), *Efficient three-dimensional shear-flexure interaction model for reinforced concrete walls*, *Engineering Structures* **294**, article 116700, DOI https://doi.org/10.1016/j.engstruct.2023.116700 . Author's element guide https://kkolozvari.github.io/E-SFI-MVLEM-3D/ . It supports `E_SFI_MVLEM_3D` four-node 3D axial–flexure–shear modeling and syntax, **not** evidence that the older 2D RW specimen reproduces the re-entrant 25-storey core. The E-SFI element's optional `CoR`, `ThickMod` and *Poisson* parameters have different meanings from the *FSAM* friction/dowel `nu=0.8 / alpha=0.01`. Do not swap or silently copy values between those definitions.

## Damped-outrigger FVD literature source (separate from RC wall source)

**R03.** Yang, Y., Zhao, X., Shi, W. and Li, J. (2021), *Optimal Design of Mega-Frame Core Wall Structures Equipped with Viscous Damped Outriggers for Human Comfort Performance under Wind Loading*, *Shock and Vibration* (2021), article 6673682. DOI https://doi.org/10.1155/2021/6673682 .

The paper explicitly reports an **initial design trial** with **one damper at each outrigger end in zone 4**, coefficient **C=700 kN/(mm/s)^0.3** and exponent **alpha=0.3**; later wind-serviceability optimization reports **C=635 kN/(mm/s)^0.3** in zones 4 and 6. This confirms the origin of the user's earlier **C=700, alpha=0.3** literature baseline; it is **not** the paper's optimized final coefficient, and the paper is about *wind comfort*, not an experimental seismic qualification of the thesis damper.

In `kN–m–s` the same force–velocity law `F=C|v|^alpha sign(v)` has `C_model=700*(1000**0.3) kN·(s/m)^0.3` (approximately 5560.3), **NOT 700 kN·(s/m)^0.3**. However, an OpenSees **Maxwell** `ViscousDamper(K,Cd,alpha)` additionally requires a separately sourced and physically consistent spring stiffness `K`; do not invent `K` or assign the same `C` with an incompatible velocity unit. The existing `components/sections/devices.py` enforces positive finite `K,Cd,alpha`. No FVD is needed for the M0 no-device baseline; M2/M4/M6 must record the separate damper/connection model and units before execution.

## Direct transfer in the repository

- `components/nonlinear_time_history/material_source_sets.py::peer_fsam_panel_values` stores the exact Appendix B.3 **web and boundary** `rho_x/rho_y/nu/alpha` values and printed-page citation. Its provenance rows are `FROM_SOURCE` for these now directly attested FSAM values.
- `components/nonlinear_time_history/material_draft.py::prepare` uses **web** `rho_x=rho_y=0.0074` for `PEER_2015_12_SINGLE_SOURCE` instead of deriving ratios from a fictitious D20@200 reinforcement spacing; it records the boundary pair separately, `UNCONFINED_WEB_ONLY`, and leaves the saved copy unapproved. Other `M30_FE500_SENSITIVITY`/mixed bases retain their existing explicitly labeled assumptions.
- `components/nonlinear_time_history/research_building_materials.py::define_building_materials` assigns the same published web ratios to the direct existing-building **PEER research model**. Explicit one-at-a-time override studies remain allowed and are recorded. It preserves source wall thickness and element count instead of recreating a literature wall.
- `components/nonlinear_time_history/material_source_sets.py::baseline_values` now provides published `0.0074` as the baseline for `wall.rho_x/y`. The existing `0.9×/1.0×/1.1×` parameter candidates are **analyst-selected sensitivity multipliers**, not experimental confidence intervals or published bounds.
- `tools/run_existing_nltha.py` / `docs/programs/38_DIRECT_EXISTING_MODEL_NLTHA.md` remain the intended source-based **research** XY+YX run; the old production checklist is **not** silently auto-approved. Published inputs are enough to define a *hypothesized research baseline*, not enough to prove actual foundation MPC equivalence or that the nonlinear wall transient converged.

## Two distinct run decisions (avoid the 21-blocker confusion)

**A. LITERATURE_RESEARCH_NLTHA:** cite the exact source and use published parameter values directly. No new experimental testing of each material is required to *define and attempt* the numerical model. Still inspect numerical finite-state, accepted steps, initial static stability, solver failures, sensitivity, component checks, original waveform identity, NBC time-history selection and 32-support/44-mesh load paths. Report findings as **literature-based transfer results**, not as validated predictions of real construction.

**B. PROJECT_VALIDATED_NLTHA:** intended for claims of as-built reinforcement, material response, design acceptance or certified ETABS/OpenSees equivalence. That requires separately verified source and engineering evidence. Do not change `nonlinear_parameters_reviewed`, the 16 readiness flags, or `approved_for_nltha` automatically. The GUI's 21 unresolved production gates stay true to their purpose and should be presented separately from the research path instead of being misdescribed as a mandatory experimental test before thesis exploration.

**First analysis target:** existing **M0, Kobe, ULS, XY and YX**, with native time integration of the complete paired record. Preserve 32 real foundation supports, 44 shell mesh transfer points, exact existing seismic source input, two 12 m X walls with openings, source frequencies and 5%-or-lower damping. Later M1–M6 FVD/BRB models require **separate directly cited device coefficients** and a physically consistent damper stiffness and interface; a paper's viscous `C, alpha` alone does not define OpenSees `ViscousDamper(K,Cd,alpha)`.

## References and implementation evidence

- PEER R01 PDF Appendix B.3 web and boundary card, original source numerical listing: https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf
- 3D E-SFI authors' manual: https://kkolozvari.github.io/E-SFI-MVLEM-3D/
- OpenSees official E-SFI element syntax: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html
- Code source and tests: `tests/test_peer_direct_literature_fsam_transfer_20261122.py`, `tests/verify_material_source_sets.py`, `tests/verify_peer_material_draft_isolation.py`.
- This source-only integration must not be described as a completed 25-storey OpenSees transient or successful independent PEER specimen numerical reproduction; use exact saved solver evidence for those separate claims.
