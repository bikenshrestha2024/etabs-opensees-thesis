# Additional reinforced-concrete Aw / openings sources — 2026-11-12

**Classification:** LITERATURE_REVIEW_COMPLETED / SELECTED_PROJECT_WALL_GROUPING_UNCHANGED / NATIVE_STIFFNESS_VALIDATION_OPEN.

This register updates the [Aw validation source register](SOURCE_REGISTER.md) without adding any copyrighted source PDFs to this **public** repository. The author's selected NBC 105:2025 §5.1.2 calculation continues to be two connected 12 m X walls, each containing two 2m-wide floor-level circulation doorways, t=0.6m and H=95m: **Aw-X = 2.073174515 m²**; Y: three 6m solid walls **Aw-Y = 2.203080332 m²**. Refer to [completed first-storey export node review](20261112_EXPORT_NODE_GEOMETRY_REVIEW_COMPLETED.md). This is an empirical-period area, **not** an effective finite-element wall stiffness multiplier. Native ETABS equivalence and NBC acceptance are not certified.

## New sources received

| ID | Authors | Year | Publication / title | DOI | Key PDF pages (this upload) | Claim supported |
|---|---|---:|---|---|---|---|
| L01 | Li-Hyung Lee, Kug-Kwan Chang, Young-Soo Chun | 2000 | *Experimental formula for the fundamental period of RC buildings with shear-wall dominant systems*, Structural Design of Tall Buildings 9:295–307 | [10.1002/1099-1794(200009)9:4<295::AID-TAL153>3.0.CO;2-9](https://doi.org/10.1002/1099-1794(200009)9:4%3C295::AID-TAL153%3E3.0.CO;2-9) | pp.9–10, printed pp.303–304 | **Direct RC use** of historical UBC wall-area/overall-length empirical period; code predictions may poorly match measured periods from 50 buildings |
| L02 | Anas Marwan Hasan Fares | 2018 | *Effect of Shear Wall Openings on the Fundamental Period of Shear Wall Structures*, MSc thesis, An-Najah National University | No verified DOI | PDF pp.34–35 and 73 onwards (door openings) | Explicit doorway stiffness/period study, **not** NBC formula validation |
| L03 | SEAOC Seismology Committee | 1999 | *Recommended Lateral Force Requirements and Commentary*, Seventh Edition | No DOI | §C105.2.2, period formula commentary | Earlier UBC-era period commentary; distinguishes empirical formula from dynamic model period |
| L04 | J. Kent Hsiao | 2014 | *Hand-Calculated Procedure for Rigidity Computation of Shear Walls with Openings*, ASCE | [10.1061/(ASCE)SC.1943-5576.0000210](https://doi.org/10.1061/(ASCE)SC.1943-5576.0000210) | pp.1–9 | One-storey perforated wall *elastic rigidity* under same-height opening and rigid-base assumptions. No direct NBC Aw formula |
| L05 | H.-S. Kim, D.-G. Lee | 2003 | *Analysis of Shear Wall with Openings Using Super Elements*, Engineering Structures 25:981–991 | [10.1016/S0141-0296(03)00041-5](https://doi.org/10.1016/S0141-0296(03)00041-5) | pp.1–11 | RC shell/opening mesh and stiffness benchmark; not NBC empirical-period grouping |
| L06 | J. I. Daniel, K. N. Shiu, W. G. Corley | 1986 | *Openings in Earthquake-Resistant Structural Walls*, Journal of Structural Engineering 112(7):1660–1676 | DOI needs independent verification | pp.1–17 | **RC experimental specimens**: isolated solid wall vs wall with openings at each floor, opening reinforcement/lintel and cyclic response |

## Repeat uploads / not independent new sources

SEAOC Vol I+II 1997-UBC manual (includes **masonry** Example 19); SEAOC Vol III RC wall/coupling examples; ICBO 1997 UBC **Volume 1** (NOT the structural Volume 2); Goel & Chopra 1998; Balkaya & Kalkan 2004; SEAOC Blue Book 2019 are repeat copies. Compare exact SHA256 in the **private** uploaded reference-register CSV; do not count repeated filenames as multiple corroborating sources.

## Engineering inference and limits

- **UBC/SEAOC effective wall-area convention** is relevant to both concrete and masonry, as explicitly confirmed in SEAOC 2019 Period Determination Article 04.03.010 p.4 (PDF p.125). Lee et al. 2000, printed p.303, separately identify minimum cross-sectional shear area `Ae`, overall wall length `De` along loading and full building height `hn` for the RC shear-wall empirical equation. This further supports the distinction behind 12m grouping.
- **It does not prove the current wall's actual stiffness.** Hsiao 2014, Kim & Lee 2003, Daniel et al. 1986, and Fares 2018 are relevant independent benchmarks for the perforated wall stiffness, opening/coupling-beam action, stress concentrations and mesh sensitivity. Use consistent dimensions and material assumptions; do not substitute reference specimen stiffnesses without calibration.
- **Lee et al. 2000 and Goel & Chopra 1998 warn** that an empirical code period need not equal the measured or full dynamic model period. Compare these independently rather than altering an OpenSees physical wall stiffness to force its eigenperiod to match the empirical (A_w) formula.
- **Do not use wood shear-wall opening commentary** from the 1999 SEAOC volume as proof of RC connectivity.
- Selected Aw-X **2.073174515 m²** and Aw-Y **2.203080332 m²** remain as before; this review makes **no code or original workbook/EDB changes**.

## Next physical-validation tests

1. Reproduce a 12m long, 0.6m thick wall with two first-storey 2m×2.3m doors, full-height concrete above the doors, and consistent supports in an isolated ETABS/OpenSees elastic-shell benchmark; test mesh convergence and door-edge stress concentrations.
2. Check first-storey coupling/head-spandrel section/reinforcement and nonlinear behavior separately (Daniel 1986 and SEAOC Vol III), not from empirical Aw.
3. Compare eigenperiod, modal mass, stiffness and story drift in source-matched full-building ETABS/OpenSees. Document objective discrepancies, not code acceptance without the separate native gates.

**Files:** Source PDFs remain private user-uploaded evidence; a separate downloadable manifest contains full SHA256 of the 12 new uploads.
