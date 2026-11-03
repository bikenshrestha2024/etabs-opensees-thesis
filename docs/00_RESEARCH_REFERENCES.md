# 00 — Thesis scientific source register

Source register prepared from the PDFs supplied to this chat and relevant documented code references. A source paper supplies a formulation or measured specimen, not automatic numerical validation of this building.

| ID | Bibliographic source | Source URL | Appropriate use | Explicit transfer restriction |
|---|---|---|---|---|
| R01 | Kolozvari, Orakcal and Wallace (2015), PEER 2015/12, Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading | [Source](https://peer.berkeley.edu/publications/2015-12) | ConcreteCM/SteelMPF/FSAM and measured wall cyclic comparisons | Do not import a PEER wall material card into all building walls as experimentally calibrated |
| R02 | Kolozvari, Lopez and Massone (2023), Efficient three-dimensional shear-flexure interaction model for reinforced concrete walls | [Source](https://doi.org/10.1016/j.engstruct.2023.116700) | E-SFI-MVLEM-3D numerical formulation, 3D cyclic panel and wall benchmarks | Benchmarked shapes and loads are not equivalent to project openings, re-entrant core or connections |
| R03 | Ji, Sun, Wang and Kolozvari (2023), T-shaped RC walls under high axial force ratios | [Source](https://doi.org/10.1002/eqe.4060) | Axial-load sensitivity, boundary failure and T-wall validation | Match axial ratios, specimen layout and loading; not universal stiffness factors |
| R04 | Stokley and Lowes (2024), PEER 2024/11, Evaluation and Calibration of an OpenSees Layered Shell Element Model | [Source](https://peer.berkeley.edu/) | Separate calibration/validation wall specimens and layered-shell approaches | Layered shell parameters cannot simply be reused as E-SFI-MVLEM-3D FSAM inputs |
| R05 | Korkmaz and Kircil (2026), supplemental damping in RC buildings equipped with FVDs, Buildings 16, 711 | [Source](https://doi.org/10.3390/buildings16040711) | Supplemental damping methodology based on structure-device interaction | Project-specific damper stiffness, coefficient, exponent and installation must be demonstrated |
| R06 | Ozkaya and Gurbuz (2026), irregular high-rise composite building FVD placements | [Source](https://doi.org/10.1007/s10518-026-02428-6) | FVD arrangement sensitivity and comparison workflow | Composite-structure percentages are not predictions for asymmetric RC building |
| R07 | Guerrero Bobadilla et al. (2025), BRB cumulative ductility and fatigue life, SDEE 199, 109700 | Source PDF supplied; DOI not independently confirmed | BRB cyclic fatigue, overstrength and energy response | Use actual BRB product geometry and tested protocol; DOI to verify |
| R08 | Cao et al. (2024), out-of-plane eccentricity of buckling-restrained braces | [Source](https://doi.org/10.1007/s11803-024-2282-4) | Out-of-plane connection eccentricity influence on BRBs | Do not assume pin-ended corotTruss represents full connection behavior |
| R09 | Tian, Lv and Dong (2026), circular steel tube brace hysteresis, Buildings 16, 3751 | [Source](https://doi.org/10.3390/buildings16183751) | Buckling/reversal hysteresis modeling reference and ML surrogate research direction | Circular tube not the thesis SHS 350x350x16; AI surrogate is not material calibration |
| R10 | DUDBC NBC 105:2025, Seismic Design of Buildings in Nepal (second revision) | [Source](https://dudbc.gov.np/pages/24231978/) | Seismic input, 3D time histories, drift/torsion and structural acceptance | Section 9.3.3.1 refers to 5.6 although drift text is at 5.5.3; retain discrepancy |
| R11 | Ji, Cheng and Xu (2018), coupled axial tension-shear behavior of RC walls | Source PDF supplied; DOI not independently confirmed | Tension-shear sensitivity of wall panels | Different wall slenderness and axial loading than high-rise core |
| R12 | Rezapour, Ghassemieh and Hajian (2026), coupled shear walls with asymmetric openings | [Source](https://doi.org/10.1007/s10518-025-02353-0) | Coupling-beam/opening macro-modeling and geometry | Proposed formulations require independent reproducible case tests |
| R13 | Tura, Orakcal, Gullu and Ilki (2026), layered fixed-strut-angle shell validation against U/H wall tests | [Source](https://doi.org/10.1007/s10518-025-02165-2) | Nonplanar core wall multidirectional and torsional experimental benchmarks | LFSAFE is an alternative formulation and not identical to E-SFI |

## Material evidence policy

A manufacturer leaflet, including the uploaded Steel 500XD brochure, is NOT measured cyclic material data, heat certificate or an experimental Fe500/500XD calibration. Demand a mill certificate or recorded coupon test, then calibrate nominal versus measured Steel02 or SteelMPF separately.

Research evidence tiers: FORMULATION -> EXPERIMENT -> NUMERICAL_REPRODUCTION -> PROJECT_TRANSFER_ASSUMPTION -> PROJECT_VERIFIED. Every stored parameter must include its source identifier, original units, conversion, publication/specimen locator, calibration objective, fit statistic, and limitations.

Recommended measured comparisons: peak strength, initial/secant stiffness, hysteretic loops, pinching/unloading slope, cumulative dissipated energy, strain profile and failure/drift capacity. A nominal grade and a smoke test do not establish these.

NBC 105:2025 section 5.5.3 gives interstory drift ratios 0.025 ULS and 0.006 SLS; section 9.3.3.1 cross-reference to 5.6 is inconsistent with that source section. Do not quietly alter the code text.
