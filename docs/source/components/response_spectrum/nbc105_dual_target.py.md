# nbc105_dual_target.py

**Source:** [nbc105_dual_target.py](../../../../components/response_spectrum/nbc105_dual_target.py). Pure standard-library implementation of NBC 105:2025 Figure 4-2 Eq 4.1(2), Table 4-1, and RC dual system Table 5-2. It creates physically different C/D targets for ULS `C_h(T)*Z*I/Omega_u`, with `Omega_u=1.4`, `R_mu=3.5` and `Omega_s=1.2`.

**Inputs:** actual documented design zoning `Z`, importance `I`, soil type C or D, period grid between 0–6s. All numeric inputs are checked. No blanket assumption of Z=.35/I=1 or of Soil C/D site eligibility.

**Outputs:** two independent CSVs and manifest JSON, neither of which is a matched-accelerogram validation.

**Tests:** `tests/verify_nbc105_dual_target.py` verifies the official piecewise formulas for both types and checks that a D curve fails a C-target comparison.

[Full instructions](../../../programs/34_NBC105_RC_DUAL_SOIL_C_D_TARGETS.md).
