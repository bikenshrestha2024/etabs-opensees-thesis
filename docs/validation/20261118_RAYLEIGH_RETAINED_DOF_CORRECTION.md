# Rayleigh period correction for partially fixed diaphragms

## Reproduced cause

OpenSees 3.8.0 with the Transformation handler resets constrained-node trial displacements when a retained MP degree of freedom also has an SP. In `TransformationDOF_Group::enforceSPs(0)`, the transformed vector starts at zero and gets only the SP-fixed retained coordinates. The free translations are therefore reset on the tied nodes as each LoadControl step starts. In the elastic replay, the restoring forces then require the full current step displacement, while the retained node increments on top of its previous committed translation. This is the mechanism identified in the open upstream pull request. [OpenSees v3.8.0 source](https://github.com/OpenSees/OpenSees/blob/v3.8.0/SRC/analysis/dof_grp/TransformationDOF_Group.cpp) · [Upstream PR #1785](https://github.com/OpenSees/OpenSees/pull/1785)

The Rayleigh model fixes the floor-master RZ for the translational estimate. At Y load factor 0.2, the roof master reported 9.166668 mm and each sampled tied roof node reported 6.111112 mm. At factor 1.0 the ratio was exactly 5.5. The ten free-translation contributions were proportional to the factors 0.1, 0.2, …, 1.0, which sum to 5.5. In the quotient, multiplying every displacement by 5.5 multiplies the numerator by 5.5² and the denominator by 5.5, increasing the period by √5.5. Base equilibrium still closed because the element-connected nodes carried the correct final displacement. A permanent RZ fix reproduced the failure. A three-node elastic cantilever reproduced it with master or physical-node loading, with or without added mass. With Lagrange constraints the master and tied node both reached the analytical 1/300 m. In a Transformation control with RZ free, the reduced case also tracked correctly.

## Correction and evidence

Each direction starts from a fresh elastic model and an equilibrated torsion-suppressed gravity baseline. The reference load now uses one Newton step. The NBC work sum uses the common physical-node translation on each tied floor, after subtracting that floor's gravity baseline. The runner rejects nonzero tied floor rotation above 10⁻⁹ rad, a translation spread above 10⁻⁸ m, an incomplete story ledger, a load factor different from 1, or incremental base reaction imbalance above 0.1%. The retained-node increment is stored for diagnosis. The numerical tolerances are verification thresholds used by this implementation.

| ULS direction | Archived ten-step retained-node period (s) | Corrected one-step period (s) | Ten-step physical floor period (s) | Same-domain eigenperiod (s) | Roof displacement, corrected / archived (mm) |
|---|---:|---:|---:|---:|---:|
| X | 3.898514 | 1.662332 | 1.662332 | 1.663934 | 14.902 / 81.961 |
| Y | 5.590441 | 2.383772 | 2.383772 | 2.383914 | 30.556 / 168.056 |

The full runner used 25 storeys, 76 source supports, UmfPack/Newton, and the normal 20-step sustained gravity preload per direction at 286,419.758 kN. The reference force was 2,846.915562 kN per direction and the incremental base reaction was −2,846.915562 kN. Maximum within-floor translation spread was zero at reported precision. A separate fresh-domain sensitivity replay at 0.5%, 1%, and 2% of seismic weight gave the same periods within 4 × 10⁻⁹ s. The full X/Y runner took 190.5 s, including approximately 173 s for the two gravity solves.

A ten-step Y replay with RZ free and a floor moment of 1.45 m × Fi agreed with the inverse diaphragm transformation from all tied floor nodes within 4 × 10⁻¹⁸ m. This control narrows the verified trigger to the overlapping SP and retained MP DOF. Leaving RZ free is appropriate for the ESM torsional load cases, which require their own response runs with the updated loads.

| NBC 5.1(1) reconstruction | X | Y |
|---|---:|---:|
| Sum of Wi × di² (kN·m²) | 20.7590242613 | 87.2098257122 |
| Sum of Fi × di (kN·m) | 30.2316728649 | 61.7627612350 |
| g × sum of Fi × di (kN·m²/s²) | 296.5727108044 | 605.8926877158 |

The V126 JSON, Excel, plots and logs preserve the new calculation separately from V123. The compatibility launcher retains its existing filename. Automatic period import requires both axes, V126 displacement provenance and matching state, model SHA, story-weight SHA and directional Aw. The legacy calculation and snapshots remain available for historical review. Rebuild dependent X/Y ESM and design-spectrum comparison outputs before using them with V126. The source EDB, OpenSees gravity restraints, structural elements and native dynamic solver configurations were outside this change.

## NBC 105:2025 and the grouped walls

Section 5.1.1 uses elastic directional displacement at each floor's centre of mass with torsion suppressed. A rigid horizontal diaphragm with RZ = 0 translates uniformly, so its verified tied nodes give the same displacement at the centre of mass. The reference load shape here uses the empirical-period exponent. Section 6.3 design floor forces use the exponent of the adopted period. Section 5.2 and Table 5-1 use dead load, 0.60 storage live load and 0.30 other live load, with roof live load excluded. Sections 5.1.2 and 5.1.3 govern the empirical estimate, 1.25 amplification and comparison with the Rayleigh estimate for design actions. [DUDBC NBC 105:2025, printed pp. 28–30](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf#page=51)

The source-export geometry verifies the project-selected grouping of two 12 m X wall lines across both bays. Each line has two 2 m door openings up to 2.3 m and 0.60 m wall thickness. The first-storey horizontal net area is 0.60 × (12 − 2 − 2) = 4.80 m² per line. The reviewed grouping uses the full connected 12 m length in the weighting term, giving Aw-X = 2.073174515 m². Three solid 6 m Y walls at 0.60 m thickness give Aw-Y = 2.203080332 m². The four-6 m interpretation gives X Aw = 1.958293629 m² and remains a workbook sensitivity case. The grouped values are applied by the shared importer before the Rayleigh cache is checked. This keeps the ESM, modal and MRSM inputs on the same reviewed geometry when the source geometry matches.

| Period and ULS diagnostic force | X | Y |
|---|---:|---:|
| Empirical period at H = 95 m (s) | 1.585025 | 1.537584 |
| 1.25 × empirical period (s) | 1.981281 | 1.921980 |
| Adopted §5.1 period (s) | 1.662332 | 1.921980 |
| Soil C Ch(T), provisional | 1.503911 | 1.300742 |
| Design Cd, provisional | 0.10742225 | 0.09291015 |
| §6.3 distribution k | 1.581166 | 1.710990 |
| Equivalent-static base shear (kN) | 30,582.206 | 26,450.735 |

The ESM arithmetic used W = 284,691.556 kN, Z = 0.35, I = 1, Rµ = 3.5 and Ωu = 1.4. X diagnostic base shear rises by 4,923.160 kN, about 19.19%. Y remains governed by its amplified empirical period. Section 3.2.1 keeps this 95 m model's ULS ESM results in comparison status. Section 4.1.3.1 requires Vs,30 for a building over 40 m. Independent ETABS model-equivalence checks still need matched foundation restraints, stiffness/modifiers, mass, load combinations and mode shapes. The 32-support joint reaction conversion is recorded in the parallel [gravity review](20261118_32_SUPPORT_GRAVITY_CONVERSION.md).

The 1,728.202 kN gap between sustained gravity and the seismic ledger is fully accounted for by self-weight applied at nodes fixed in both horizontal directions. Those loads enter gravity equilibrium and their nodal masses are excluded from the active horizontal mass sum. The active OpenSees weight and assembled story-ledger weight match exactly at the report's precision. An independent ETABS check should reconcile the per-storey allocation against §5.2's mid-height convention. The ledger described here assigned inter-floor nodal weights to the next floor above. Superseded 2026-11-21: `components/model/assembly.py` now applies the §5.2 mid-height rule through `storey_index_for_elevation` (see `docs/nbc105/clause_05_dynamic_characteristics_matrix.md`, row 13); re-assembled exports differ from the figures in this report.

The Windows regression run under `tests/` passed 427 tests and 218 subtests, with 39 skips. The retained-DOF benchmark ran against OpenSees 3.8.0. A separate import through the installed analysis runtime read back the corrected X/Y periods and reviewed X/Y Aw. Repository-root pytest also discovers historical `Verification_V*` scripts that expect archived local files and are outside the active suite.

## November 21 clear-beam and native-elastic replay

The newer ULS package used the original gross-beam and gross-shell export. Independent reconstruction of all 25 saved floors gave Rayleigh periods of 1.661966 s (X) and 2.383341 s (Y). Its automatic ZIP contained six X case calculations because packaging started before the Y export completed. The combined export now starts one archive after both directions finish.

A fresh OpenSees 3.8.0 replay used the verified clear-beam export, reviewed ETABS elastic modifiers, 76 source supports, and the assembled seismic preload. The directional seed used the amplified empirical period, then each centered solve used the actual applied floor forces and incremental elastic translations in §5.1.1 with g = 9.81 m/s². The 25-floor active seismic weight was 276,039.112 kN. The nodal mass reconstruction matched each floor to within 1.5 × 10⁻¹¹ kN.

| ULS quantity | X | Y |
|---|---:|---:|
| Empirical period (s) | 1.585025 | 1.537584 |
| Amplified empirical period (s) | 1.981281 | 1.921980 |
| Centered Rayleigh period (s) | 1.977548 | 2.703236 |
| Adopted directional period (s) | 1.977548 | 1.921980 |
| Adopted-period ESM comparison base shear (kN) | 17,448.316 | 17,952.785 |

Incremental base reactions closed to within 7 × 10⁻¹⁵ relative error. The export holds all 12 directional, polarity and eccentricity force calculations. These are ULS comparisons under §3.2.1. Soil B remains provisional pending Vs,30 under §4.1.3.1. Verify the analytical restraints and mass allocation against native ETABS before comparing physical response. [NBC 105:2025, §5.1–5.2](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf)

## Research and international context

- Goel and Chopra evaluated empirical period expressions against measured motions of concrete shear-wall buildings. Their results explain why a fitted code estimate can differ from a calculated mode. They cannot explain step dependence with unchanged final loads. Here, X is 4.88% above the raw empirical period and Y is 55.03% above it. The corresponding Rayleigh/eigen discrepancies on the same domain are approximately 0.096% and 0.006%. [Period Formulas for Concrete Shear Wall Buildings](https://doi.org/10.1061/(ASCE)0733-9445(1998)124:4(426))
- ASCE/SEI 7-22 §12.8.2 provides international context for limiting an analytical period using an empirical reference in equivalent lateral force calculations. The project uses NBC's own factor and eligibility limits. [ASCE/SEI 7 publisher](https://www.asce.org/publications-and-news/asce-7) · [NEHRP Recommended Provisions](https://www.nist.gov/news-events/news/2021/02/2020-nehrp-recommended-seismic-provisions-new-buildings-and-other)
- Second-generation Eurocode 8 EN 1998-1-1:2024 and EN 1998-1-2:2026 are relevant international seismic references during national-annex transition. PEER Tall Buildings Initiative 2017/06 provides peer-review guidance on model adequacy and tall-building seismic analyses. They provide comparison context for this NBC assessment. [JRC Eurocode 8](https://eurocodes.jrc.ec.europa.eu/events/second-generation-en-1998-eurocode-8-design-structures-earthquake-resistance) · [JRC transition dates](https://eurocodes.jrc.ec.europa.eu/faq) · [PEER 2017/06](https://peer.berkeley.edu/publications/2017-06)
- IS 16700:2023 and its published amendment are supplementary under the project code matrix. The selected initial P-Delta and slab stiffness provisions are separate from this Rayleigh correction. [BIS amendment publication](https://egazette.gov.in/WriteReadData/2025/260405.pdf) · [Project code matrix](../../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md)
- The `rigidDiaphragm` and LoadControl manuals describe the kinematic transformation and factor increments used in this replay. The OpenSeesPy paper documents the native FEM interface. The upstream PR status should be checked before qualifying a new native solver build. [Rigid Diaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html) · [Load Control](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/integrator/LoadControl.html) · [Zhu, McKenna and Scott, SoftwareX](https://doi.org/10.1016/j.softx.2017.10.009)
