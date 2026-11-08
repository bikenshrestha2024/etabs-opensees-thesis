# Gravity validation gates and evidence-based correction sequence

[REF components/gravity/validation_scorecard.py]

The gravity upload ZIP contains three files in its root:
`GRAVITY_VALIDATION_SCORECARD.json`,
`GRAVITY_VALIDATION_SCORECARD.csv` and
`GRAVITY_VALIDATION_SCORECARD.txt`.
They are generated from actual source configurations, OpenSees gravity
reports, direct ETABS reaction comparison, and the evidence manifest.
No missing numeric result is guessed; the scoreboard always reports
`NOT_STRUCTURALLY_VALIDATED` until separate engineering acceptance
is documented. A converged OpenSees solver does **not** imply ETABS
equivalence.

## Existing dated reference run, November 8, 2026

| Gate | Original observed evidence | Status |
| --- | --- | --- |
| Global gravity load agreement | ETABS 311367.313879 kN, OpenSees 320047.788933 kN; **8680.475054 kN excess** | **NOT VALIDATED** |
| Individual foundation reactions | 76 one-to-one coordinate matches yet large discrepancies (ETABS point 264 / OpenSees 41 differs about 10861.4 kN) | **NOT VALIDATED** |
| Evidence collection | ZIP created, **7 optional items missing**, 0 oversized in uploaded log | **INCOMPLETE** |
| Beam self-weight | RCC gross 53984.055 kN, potential source clear-span reduction 8652.444 kN | **Unverified corrected run** |
| RCC joint overlap | Centered-box volume union ~19358.527 kN but source CP8 beam insertion not modeled physically | **Geometry unverified** |

The supplied 7 missing items were:
`Gravity_Profile_ULS.json`, `Gravity_Profile_SLS.json`,
`OpenSees_Complete_Gravity_Check_V118.json`,
`Gravity_Beam_End_Actions_ULS_V141.csv`,
`Gravity_Beam_End_Actions_SLS_V141.csv`,
`Gravity_GUI_Actions.log` at the selected dual-case subfolder
(the root GUI log is independently packed), and the offline ETABS
table comparison (not run). They are **optional**; no placeholders are
created. Their absence is not a model failure, but the evidence
manifest must show it.

## Root cause and model-development rules

The current 8680 kN excess is not a permitted "target subtraction".
The original ETABS material list separately reconciled an RCC beam
self-weight difference of approximately 8652.444 kN to the reported
total end-offset lengths. This supports investigating a mismatch of
frame weight conventions. It does NOT establish that
all end-offset volume corresponds to unique physical material removed.
A beam at `CP 8 Top Center` overlaps the slab differently from
a centered rectangular box.

Check ALL potential contributors independently:
1. Source load pattern multipliers and full gravity 1.0D+1.0L,
   separate from 0.3 sustained seismic live preload.
2. Whether source frame self weight uses full or ETABS effective
   clear length, per ETABS source object and `Self Weight Option`.
3. Slab physical top/bottom placement and cast-in-place beam-slab,
   beam-column, wall-column and wall-slab shared concrete volume.
4. Null-line-to-wall finite element connectivity and actual base
   restraints. ETABS 76 point supports are the source-validation case;
   continuous wall fixed 97 supports are sensitivity analysis.
5. SHS hot-formed rounded corner area and material density; do not
   tune brace weights just to equal ETABS.
6. Missing/duplicated floor, wall and device source load patterns;
   differences between nodal pressure and self-weight ledgers.
7. ETABS beam end kinematic rigidity vs OpenSees `-jntOffset`,
   cracked stiffness, diaphragm and shell-mesh discretization.
8. Physical wall openings, mesh node merging and nonlinear preload
   assumptions; confirm global source FZ and per-support transfer.
9. Source model revision identity and stale ETABS direct comparison
   artifacts. The scorecard compares the direct comparison's OpenSees
   reaction total against the selected gravity result; disagreement
   is flagged `STALE_COMPARISON_REBUILD_AND_RECOMPARE`.
10. Include input artifacts and detailed provenance for rerunning.

The selected beam weight policy is printed separately from the global
load discrepancy in every ZIP. The default
`GROSS_SECTION_LENGTH` is intentionally unchanged by evidence
packaging. Only after independent verification of the source offset
and weight convention can
`ETABS_BEAM_CLEAR_LENGTH` plus
`etabs_clear_beam_weight_confirmed=true` be deliberately selected
**before rebuilding the source OpenSees export**. Avoid combining it
with `VERIFIED_SINGLE_OWNER` physical joint deduction.

## Numerical screening vs structural acceptance

The scorecard's global 0.5% screening threshold, plus local 100 kN
AND 5% support screening threshold, are **user-review diagnostics**,
not NBC 105 structural-design or code acceptance limits. A global
numerical screen within these bounds does not certify structural
equivalence; full applied-load provenance, support geometry, nodal
reactions, gravity deflections, beam actions, shell forces and
modal mass still require independent acceptance.

When comparing with ETABS, use the actual full gravity
`ETABS_SOURCE_SUPPORTS` case, never the 97-support sensitivity case.
Rerun the ETABS direct comparison *after every rebuilt OpenSees
gravity result*. A stale comparison is explicitly rejected.

Tests:
`python tests/verify_gravity_validation_scorecard.py`
`python tests/verify_gravity_comparison_bundle.py`
`python tests/verify_beam_weight_convention.py`.

**Status:** code-level evidence and safeguards only; the user's
25-storey model must still be rebuilt and rerun in the native Windows
ETABS/OpenSees environments to determine the corrected reaction totals.
