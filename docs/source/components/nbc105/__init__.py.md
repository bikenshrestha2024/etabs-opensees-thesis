# __init__.py — source documentation

**Python source:** [components/nbc105/__init__.py](../../../../components/nbc105/__init__.py)
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** NBC 105:2025 clause modules
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Package marker for `components/nbc105/`: one module per NBC 105:2025 main clause plus `constants.py`. Contains only a docstring.

## Source, inputs, units
None.

## Outputs and failure conditions
None.

## Research and standards
NBC 105:2025. See the [clause 5 compliance matrix](../../../nbc105/clause_05_dynamic_characteristics_matrix.md).

## Regression acceptance
Imported by `tests/test_nbc105_constants.py` and `tests/test_nbc105_clause5.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
