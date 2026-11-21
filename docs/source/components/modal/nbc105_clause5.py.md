# nbc105_clause5.py — source documentation

**Python source:** [components/modal/nbc105_clause5.py](../../../../components/modal/nbc105_clause5.py)
**Git baseline content SHA:** shim (module moved 2026-11-21)
**Subsystem:** Modal analysis and numerical damping
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Backward-compatible re-export shim. The implementation moved to `components/nbc105/clause_05_dynamic_characteristics.py` ([guide](../nbc105/clause_05_dynamic_characteristics.py.md)). Every public name of that module (functions and constants, its `__all__`) is available here as the same object. New code imports from the new path.

## Source, inputs, units
See the [moved module guide](../nbc105/clause_05_dynamic_characteristics.py.md).

## Outputs and failure conditions
None of its own.

## Research and standards
NBC 105:2025 clause 5. See the [clause 5 compliance matrix](../../../nbc105/clause_05_dynamic_characteristics_matrix.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_constants.py -q` (shim identity test). Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
