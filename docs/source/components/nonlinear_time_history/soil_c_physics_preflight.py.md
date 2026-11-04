# Soil C NLTHA — additional required source and solver evidence

The following arguments are **new strict research data fields**, not automatic certification. See [Stage 37](../../docs/programs/37_SOIL_C_NLTHA_PARAMETER_AND_COMMAND_AUDIT.md) for all parameters and full NBC clause matrix.

- `damping_reference_modes`: exactly two **1-based positive eigenmode IDs**, e.g. `[1, 4]` for a sensitivity **example only**, selected after reviewing modal mass, coupled torsion and actual structural frequencies. No fixed indices are prescribed by NBC; the model reports actual selected modal periods and 5% Rayleigh coefficients `alphaM` and `betaKcomm`.
- `rayleigh_device_exclusion_reviewed`: verified reviewer flag for nonlinear wall, FVD and BRB element Rayleigh damping and potential double-counted energy; mandatory only for `THESIS_NLTHA`. This flag documents a reviewer declaration, not an automatic element inspection.
- `seismomatch_original_pair_scale_evidence`: object with documentary original `scale_log_sha256`, reviewer, `factor_A`, `factor_B`, `adopted_common_pair_factor=min(A,B)`, and `matching_log_reviewed=true`. Mandatory for thesis intent; never compute this from PGA ratio. Output Path factor remains 9.80665 for pre-matched Acc(g).
- `sls_seismic_input_basis_reviewed`: SLS use of the **ULS-matched source suite** cannot be silently labelled SLS code compliance. An independent review of the intended SLS motion basis is required for thesis intent.
- `nbc105_2025_design_evidence`: existing reviewed modal periods T1_X/T1_Y/Tn90_X/Tn90_Y, hazard target/source and source SHA; the model checks NBC fitting interval and dt and logs status.
- `soil_c_primary_nltha=true`, `source_records_already_scaled=true`, `soil_type=C`, `scale=1.0`, `orientations=[XY,YX]`, `diagnostic_excitation=XY`; validated using actual user's eight pairs and Soil C workbook.

DO NOT call an exploratory model `THESIS_NLTHA` until current real building reinforcement, axial wall properties, openings, gravity/PDelta/torsion, and material/device experiments are verified and the first-step X-wall failure is resolved. Source checks are necessary but not sufficient.
