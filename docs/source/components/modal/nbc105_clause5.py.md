# nbc105_clause5.py — source documentation

**Python source:** [components/modal/nbc105_clause5.py](../../../../components/modal/nbc105_clause5.py)
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** Modal analysis and numerical damping
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Pure-Python single source of truth for NBC 105:2025 clause 5 (printed pp. 28-30): §5.1 lesser-of rule, §5.1.1 Rayleigh period, §5.1.2 empirical period (kt table, concrete shear-wall Aw with Lwi/H capped at 0.9, building height and basement rule), §5.1.3 amplification fixed at 1.25, §5.2 Table 5-1 seismic weight (roof live load always zero). A missing Rayleigh period gives an adopted period of None with status INCOMPLETE, never the empirical value. A factor other than 1.25 raises ValueError, or is reported through `period_factor_deviation`. `storey_index_for_elevation(z_m, floor_elevations_m)` applies the §5.2 mid-height rule (Wi between the mid-heights of adjacent storeys) to the assembly story-weight ledger; nodes at or below the first floor stay with floor 1 so total weight is preserved. A period is a design-input calculation, not engineering acceptance.

## Source, inputs, units
Heights and wall lengths in m, wall areas in m², weights and forces in kN, displacements in m, periods in s. Eq. 5.1(1), the shear-wall kt equation (kt = 0.075/sqrt(Aw), Aw = sum_{i=1..Nw}[Awi{0.2+(Lwi/H)^2}]) and the Figure 5-1 height rule are verified against the printed pages 28-30 of NBC 105:2025 (user-supplied PDF). Page tags: §5.1 and §5.1.1 p. 28; §5.1.2 kt list, H definition, Figure 5-1 and the Aw summation p. 29; Lwi and Nw p. 30; §5.1.3, §5.2 and Table 5-1 p. 30. See the [clause 5 compliance matrix](../../../validation/NBC105_CLAUSE5_COMPLIANCE_MATRIX.md).

## Outputs and failure conditions
Returns floats or the adopted-period dict. Non-finite or non-positive height, Awi, Lwi, Aw, empirical or Rayleigh inputs, unknown system strings, unequal Rayleigh array lengths, and non-positive Rayleigh sums raise ValueError. The basement is excluded from H only when the caller declares the Figure 5-1 condition true.

## Research and standards
NBC 105:2025 clause 5. See [period and material provenance](../../../NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md) and the [research reference register](../../../00_RESEARCH_REFERENCES.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_clause5.py -q` (hand-computed expected values) and `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
