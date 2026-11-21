# Clause 7 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 40–41. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 40–41 | `components/nbc105/clause_07_modal_response_spectrum.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 40–41 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §7.2 modal effective gravity load, signed floor modal forces; §7.3 directional mass coverage; §7.4 SRSS helper; §7.5 force-only scaling.

**Open / do not claim fully implemented:** CQC correlation coefficient/damping, ≤15% close-frequency grouping, >33 Hz missing-mass correction and ETABS/solver 90% coverage are NOT implemented in this reference module. Source wording for close-mode direct summation is retained for engineering review.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 7 gate can pass.

## §7.4 canonical CQC routing and limits (2026-11-21)

NBC §7.4 printed p.41 allows established CQC or SRSS modal combinations. The CQC *correlation equation itself* is **not tabulated in NBC**: the canonical helper `clause_07_modal_response_spectrum.cqc_correlation_matrix` preserves the previously active solver's equal-damping CQC ratio formula, adds finite positive frequency/damping validation, and is now the sole source for `components/response_spectrum/model_analysis.cqc_matrix`. This is a refactor of an accepted dynamics algorithm, not a claim that NBC explicitly prints its coefficients. Tests confirm diagonal unity, symmetry, near-degenerate modal frequencies, invalid input refusal and production numerical parity.

Still not proven: native modal shape identity, cumulative 90% directional mass and 33 Hz cutoff/missing-mass correction, source-bound ETABS/OpenSees modal equivalence and appropriate damping for the model.
