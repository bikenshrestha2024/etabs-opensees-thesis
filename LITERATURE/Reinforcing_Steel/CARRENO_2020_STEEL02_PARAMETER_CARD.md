# Carreño et al. (2020): GMP / OpenSees Steel02 reference card

**Citation:** Carreño, R., Lotfizadeh, K. H., Conte, J. P., and Restrepo, J. I. (2020). "Material Model Parameters for the Giuffrè–Menegotto–Pinto Uniaxial Steel Stress–Strain Model." *Journal of Structural Engineering* 146(2): 04019205. DOI: [10.1061/(ASCE)ST.1943-541X.0002505](https://doi.org/10.1061/(ASCE)ST.1943-541X.0002505).

**Source examined:** Uploaded 21-page publisher PDF, especially PDF pp. 14–16 / printed pp. 04019205-14 through 16; Table 12 on PDF p. 16. **Copyright:** ASCE; user-uploaded PDF must remain private, no publication or copy into this public repository. Verified publisher landing page [ASCE Library](https://ascelibrary.org/doi/10.1061/%28ASCE%29ST.1943-541X.0002505). Citation count not verified; do not manufacture.

**Experimental scope:** 36 Grade 60 reinforcement coupons, ASTM A615/A706, multiple mills, calibrated from cyclic stress–strain loops and checked against separate cyclic specimens. Bar grade/diameter and US fabrication do not identify actual project Fe500 steel. Figure/curve fits must not be described as Nepal-specific experimental calibration.

## Paper Table 12: recommended unmachined bar parameters

| Quantity | A615 Grade 60 | A706 Grade 60 | Units |
| --- | ---: | ---: | --- |
| Elastic modulus E | 202000 | 202000 | MPa |
| Yield Fy | 480 | 476 | MPa |
| b | 0.020 | 0.012 | – |
| R0 | 20 | 20 | – |
| cR1 | 0.90 | 0.90 | – |
| cR2 | 0.08 | 0.08 | – |
| a1 | 0.039 | 0.039 | – |
| a2 | 1.0 | 1.0 | – |
| a3 | 0.029 | 0.029 | – |
| a4 | 1.0 | 1.0 | – |

OpenSees official defaults/typical values (`R0=10–20, cR1=0.925, cR2=0.15`) are **not** the same as the paper's cyclic calibration estimates. Steel02 a1/a3 govern isotropic yield-envelope changes; their default zero value does not mean paper-calibrated isotropic hardening is implemented.

**Exact executable research code:** `components/nonlinear_time_history/steel02_carreno_reference.py` creates paper cards and one *shape-only Fe500 transfer hypothesis*. It does not alter `Material_Catalog/M30_Fe500_Steel02.json`, the current frame section, SteelMPF wall material, FSAM, FVD/BRB or production model.

**Next acceptance:** independent Steel02 cyclic coupon strain histories, stress/strain/energy envelopes, source-consistent Fe500 yield/tensile tests, strain-rate and bar-buckling sensitivity, then wall-material and structure checks. Do not use this card to turn an invalid first-step solve into a "verified" material model.
