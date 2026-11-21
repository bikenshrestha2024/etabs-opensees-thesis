# constants.py — source documentation

**Python source:** [components/nbc105/constants.py](../../../../components/nbc105/constants.py)
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** NBC 105:2025 clause modules
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Single definition of the gravity acceleration used where a weight is converted to a mass or a mass to a weight and where an Acc(g) record or a Cd(T) ordinate in g is converted to m/s^2: `GRAVITY_M_S2 = 9.81` m/s^2, the value printed in the NBC 105:2025 notation list (printed p. 7, "g ... to be taken as 9.81 m/s^2"; USER_DECLARED 2026-11-21). `NBC_NOTATION_GRAVITY_M_S2 = 9.81` is the printed value and equals it. `SUPERSEDED_GRAVITY_M_S2 = 9.80665` is the earlier same-day decision (standard gravity), superseded and kept only so that results saved with it are recognised and rejected on import; no calculation uses it. `PRINTED_PAGE_OFFSET = 21` is the PDF-page offset for printed pages up to 26 only (PDF page = printed page + 21); from printed p. 27 on the offset is 23 because the Figure 4-3 page and a duplicate page numbered 26 intervene, so verify the foot number of each page. Restoring 9.81 lowers mass = W/g by 0.0341 % relative to 9.80665.

Routed through `GRAVITY_M_S2`: Eq. 5.1(1) in `components/modal/rayleigh.py` and `components/nbc105/clause_05_dynamic_characteristics.py` (`rayleigh_period_s`), `components/modal/rayleigh_ledger_audit.py`, `components/modal/rayleigh_mass_audit.py`, the weight-to-mass conversion in `components/model/assembly.py`, `components/sections/area_elements.py`, `components/gravity/load_path_formulas.py`, the mass-to-weight conversion in `components/validation/irregularity_review.py`, the Acc(g) to m/s^2 conversions in the time-history and response-spectrum code, and `tools/etabs_period_review/reconcile.py`. The three single-file Verification Studio tools carry a standalone 9.81 literal pinned equal to the constant by test.

## Source, inputs, units
m/s^2 and dimensionless page offset. No inputs.

## Outputs and failure conditions
Module-level constants only. `tests/test_nbc105_constants.py` pins the values, scans the weight/mass files for a numeric gravity literal and fails on any 9.80665 or 9806.65 literal in `components/` or `tools/` outside `constants.py`.

## Research and standards
NBC 105:2025 notation list, printed p. 7. See the [clause 5 compliance matrix](../../../nbc105/clause_05_dynamic_characteristics_matrix.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_constants.py -q` and `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
