# Empirical-first Rayleigh workflow

The project workflow uses the **unamplified** empirical periods from NBC 105:2025 §5.1.2 to generate the preliminary ULS static floor forces. The 1.25 amplification in §5.1.3 is used in the final design-period comparison. NBC §5.1.1 supplies the Rayleigh equation and requires paired lateral forces and elastic center-of-mass translations with torsion excluded. The choice of the empirical-period ESM force pattern for the Rayleigh solve is the project's sequencing rule. [NBC 105:2025 §§5.1 and 6.1–6.3](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf)

| Preliminary ULS input | X | Y |
|---|---:|---:|
| Aw (m²) | 2.073174515 | 2.203080332 |
| Unamplified empirical period (s) | 1.585024708 | 1.537583821 |
| Static coefficient Cd | 0.112661606 | 0.116137687 |
| Vertical distribution exponent k | 1.542512354 | 1.518791911 |
| Reference base shear (kN) | 31,052.7389 | 32,010.8456 |
| Amplified empirical cap (s) | 1.981280885 | 1.921979777 |

1. Import `ULS_95m_V10_10_Empirical_Rayleigh_Input.e2k` into a separate ETABS model and run the centered Step 1 of `EQX+ P-Delta` and `EQY+ P-Delta`, including their nonlinear initial cases. The staged input changes the two ESM load-pattern records. It carries the existing directional preload definitions. Those histories include their directional earthquake patterns, so rerun the initial cases after applying the new coefficients. This file is the preliminary Rayleigh input and its existing RS cases retain the archived settings.
2. Export the assignment and analysis tables from that model. Run `verify_exports.py ASSIGNMENT.xlsx ANALYSIS.xlsx Empirical_PDelta_Readback.json`. The verifier checks the empirical reference coefficient, exponent and base shear in each direction, then computes Rayleigh from the matching 25 signed floor forces, weights and center-of-mass displacements. It records pending status when the reference loads are stale. The archived P-Delta exports fail this stage check in both axes.
3. Run `reconcile.py --pdelta-readback Empirical_PDelta_Readback.json --output Period_Selection_V10_10.json`. The active automatic period is the lesser of the verified Rayleigh period and 1.25 times the empirical period. Final forces use the adopted period. Keep the verified preliminary readback as evidence when staging the final ESM settings, since the final force distribution can differ from the preliminary distribution. Refresh the workbook from the two verified JSON files using the included builder.

In the workbook, rows 32–35 show the preliminary ETABS inputs and readback status. Rows 8, 11 and 12 stay blank in automatic mode while the empirical-period P-Delta results are pending. Row 9 accepts a manually supplied analytical period and applies the NBC cap. Row 10 is an explicit direct override and uses the entered value for downstream calculations.

To stage the preliminary input, run `python reconcile.py --e2k SOURCE.e2k --stage-empirical PRELIMINARY.e2k --output WORKSPACE/Period_Selection_V10_10.json`. Keep source exports and generated results in a local analysis workspace. To build the workbook, place both JSON files there and run `node build_workbook.mjs ARTIFACT_NODE_MODULES WORKSPACE --check-inputs`. The first argument points to the bundled node_modules directory containing `@oai/artifact-tool`.

The native ETABS solve is pending. The reviewed X wall geometry consists of two full-length 12 m groups. This directory contains the read-only review tools and workbook builder. The live ETABS and OpenSees launchers have their own workflows.
