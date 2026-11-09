# Confirmed ETABS native beam self-weight correction gate — 2026-11-09

## Independent evidence from user's ETABS assignment workbook

Original workbook was inspected locally; its binary was NOT committed to GitHub.
SHA256: `a92cbf4dd9950dc22944e017cc6a5a8c855bc725561f984f5685389a888a0793`.

`Material List by Object Type` (kN):
| Type | Native ETABS |
| --- | ---: |
| Column | 56733.8677 |
| Beam | **45331.6105** |
| Wall | 52934.3649 |
| Floor | 44986.7124 |
| Brace | 1280.7584 |
| Structural self weight total | **201267.3139** |

Source OpenSees gross beam = `53984.05488 kN`; recorded original
source-beam end offsets yield clear-beam candidate `45331.6105284 kN`.
Thus gross beam excess `8652.44438 kN`, and difference between native
ETABS beam material weight and computed clear candidate is about
`0.0000284 kN` due to printed source material rounding. No other
structural material category has a comparable gross-weight discrepancy.

The workbook's `Frame Assigns - End Len Offsets` explicitly contains a
`Self Weight Option` field. For **all 750 beams** it is `Auto`.
The source workbook has 750 beam `8 (Top Center)` insertions and 350
`Top` floor slab insertions. Centered RCC solid overlap geometry therefore
cannot be assumed exact and its 19358.527 kN diagnostic union must NOT
be applied automatically. Exact 750/750 original beam IDs and BOTH
original end offsets were verified against the existing OpenSees source
beam audit from the current gravity V04 evidence archive.

There is only one nonzero native pattern self-weight multiplier:
`Self Weight = 1.0`. Source `Load Set` values are Floor Finish
1.5 kN/m2, Partition 1.5 kN/m2, Live 4.0 kN/m2.

## Code changes and activation

The base ETABS physical material quantity is now independent evidence
that OpenSees gross beam self-weight is too high **for this specific
source model**. `components/validation/etabs_assignment_gravity_audit.py`
reads and hashes the assignment workbook without changing it. It tests
the native beam Material List, original object IDs, lengths, offsets,
beam count, and source self-weight multiplier and creates
`ETABS_Native_Assignment_Gravity_Quantity_Audit.json`.

Existing default `GROSS_SECTION_LENGTH` remains unchanged until the
analyst explicitly selects the native-verified `ETABS_BEAM_CLEAR_LENGTH`
policy in the source model configuration **before generating a fresh
OpenSees model**:

```json
{
  "etabs_beam_weight_policy": "ETABS_BEAM_CLEAR_LENGTH",
  "etabs_clear_beam_weight_confirmed": true,
  "joint_volume_weight_policy": "AUDIT_ONLY",
  "etabs_native_assignment_workbook_path": "C:/Users/User/Downloads/Assignment ETABS Storey 3 Outrigger Belt Truss Cap Truss ULS Case.xlsx"
}
```

These are the relevant keys to merge into the existing configuration,
NOT a complete replacement of that configuration! An alternative to the
path key is setting the environment variable
`ETABS_GRAVITY_ASSIGNMENT_WORKBOOK`. The exporter checks the original
750 ETABS beam identities, lengths and end offsets, the selected native
material quantity, and the explicit reviewer flag BEFORE a corrected
source model can be emitted. If the check fails, it raises an error and
does not create the corrected model. It writes the source proof and
`ETABS_Beam_Weight_Candidate_Gross_Source.json` beside the new export.

**Do not overwrite or relabel old gravity runs.** Export the newly
verified model to a new output directory, re-run the 32-support gravity
diagnostic, and compare the real 32 node reactions and displacement.
The current observed OpenSees total 320019.758231 kN should reduce by
about 8652.444352 kN if the model contains otherwise identical load
assignments, giving about 311367.313880 kN. This is a calculated
expectation, NOT a recorded solver result.

The source proof is a structural material-quantity check, not proof
of correct 32-node reaction redistribution, ShellMITC4 slab load
transfer, wall base restraint equivalence, modal properties, cyclic
wall modeling, or NLTHA convergence. The native-matched beam policy
must be reflected consistently in seismic mass, then modal and
nonlinear preflight analyses must be rerun on the NEW converted model.

## Regression tests

```powershell
python tests/verify_etabs_assignment_gravity_audit.py
python tests/verify_gravity_joint_weight_reconciliation.py
python tests/verify_gravity_source_load_reconciliation.py
```

Tests are CI-registered. CSI ETABS v23 native COM execution, fresh gravity
rerun and M0–M6 nonlinear model certification remain unverified.
