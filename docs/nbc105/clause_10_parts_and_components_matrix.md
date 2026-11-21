# Clause 10 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 49–52. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 49–52 | `components/nbc105/clause_10_parts_and_components.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 49–52 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §10.1 component weight cutoff 25%, reduced friction; §10.2 shutdown <=0.2g; §10.3 component Fp; Table 10-1 ap interpolation; Table 10-2 μp, Table 10-3 Ip.

**Open / do not claim fully implemented:** Table 10-1 omits an explicit equality at ΔT=0.5s; take continuous endpoint ap=1.0 and report it. Research-supported μp up to 3.5 is NOT automatically approved. Attachment/anchor design, safety cables and equipment serviceability require additional evidence.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 10 gate can pass.

## §10.4(d) hanging/swinging light safety cables

The uploaded 2025 code (printed p.51; PDF p.73 in the 137-page edition) requires safety cables fixed to the structure and fixture to resist a **lateral load equal to four times the hanging or swinging light's weight**. The canonical `light_safety_cable_design_capacity(component_weight_kN)` returns `4Wp` in kN and rejects zero, negative or nonfinite weights. Tested in `tests/test_nbc105_printed_table_verification_2025.py`. This checks the demand only; real cable/anchor capacity, connection detailing and installation remain engineering evidence requirements.

The same test independently checks Tables 3-1, 4-1, all 21 rows of 5-2, 6-1 and 10-1/2/3 against source-transcribed values rather than importing implementation constants.
