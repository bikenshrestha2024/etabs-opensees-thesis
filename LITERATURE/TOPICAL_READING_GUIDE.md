# Thesis-targeted literature sequence

1. **Damped outrigger concept and mechanism**: L001, L017, L026, L027. Locate outrigger elevation, perimeter-column flexure, connection and damper assumptions before importing design values.
2. **Asymmetric/irregular 25-storey global seismic question**: L020, L018, L021, L022 and L023. L020 uses 990 archetypes and R-factor interplay; this is a methodology reference, not an NBC 105 substitution.
3. **RC core, shear-flexure and openings**: L006, L007, L008, L009, L015, L016; compare 3D force transfer, wall opening pier/coupling actions and first-step X-axis numerical stability.
4. **FVD Maxwell behavior and support flexibility**: L004 and L010–L011. L004 finds that nonlinear damper velocity exponent, series spring/support stiffness and seismic intensity influence displacement and absolute floor acceleration; do not model the damper as a pure dashpot without checking connection stiffness.
5. **Steel cyclic sensitivity and calibration**: L003 and L005. Both use reinforcing steel test datasets and Bayesian/sensitivity procedures; L003 reports 36 cyclic coupons, and L005 explicitly compares Steel02, SteelDRC and Steel4. Their ASTM A615/A706 Grade 60 steel is not automatically the thesis project's Fe500.
6. **Independent code verification**: NBC 105:2025 R10 and L028 OpenSees formulation. Record every verification/validation gate independently.

## Required paper-level reading sheet
For every cited paper, record: exact bibliographic metadata; DOI and official URL; permitted PDF link; measured citations and source/date; relevant equations and figure/table numbers; specimen/model geometry; ground motions; implemented constitutive law; dimensions/units; uncertainty or sensitivity method; numerical integration/solver; evidence that maps to user’s 25-storey M0–M6 model; assumptions *not transferable*; status: REFERENCE_ONLY / REPRODUCED / PROJECT_ASSUMPTION / PROJECT_VERIFIED.
