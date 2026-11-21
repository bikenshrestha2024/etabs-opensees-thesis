# clause_05_dynamic_characteristics.py — source documentation

**Python source:** [components/nbc105/clause_05_dynamic_characteristics.py](../../../../components/nbc105/clause_05_dynamic_characteristics.py)
(moved 2026-11-21 from `components/modal/nbc105_clause5.py`, which remains as a re-export shim, see its [guide](../modal/nbc105_clause5.py.md))
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** NBC 105:2025 clause modules
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Pure-Python shared implementation of NBC 105:2025 clause 5 (printed pp. 28-30): §5.1 lesser-of rule, §5.1.1 Rayleigh period, §5.1.2 empirical period (kt table, concrete shear-wall Aw with Lwi/H capped at 0.9, building height and basement rule), §5.1.3 amplification fixed at 1.25, §5.2 Table 5-1 seismic weight (roof live load always zero). A missing Rayleigh period gives an adopted period of None with status INCOMPLETE, never the empirical value. A factor other than 1.25 raises ValueError, or is reported through `period_factor_deviation`. `storey_index_for_elevation(z_m, floor_elevations_m)` applies the §5.2 mid-height rule (Wi between the mid-heights of adjacent storeys) to the assembly story-weight ledger; nodes at or below the first floor stay with floor 1 so total weight is preserved. Production-routed helpers are `empirical_period_s`, `amplified_period_s`, `period_factor_deviation`, `effective_wall_area_m2` (via `grouped_wall_aw.py`) and `storey_index_for_elevation`; `adopted_period_s`, `rayleigh_period_s`, `building_height_m` and `seismic_weight_kN` are reference implementations with unit tests only (call sites apply the lesser-of rule, Eq. 5.1(1), H and Table 5-1 inline). Non-finite elevations are rejected. A period is a design-input calculation, not engineering acceptance.

## Source, inputs, units
Heights and wall lengths in m, wall areas in m², weights and forces in kN, displacements in m, periods in s. Eq. 5.1(1), the shear-wall kt equation (kt = 0.075/sqrt(Aw), Aw = sum_{i=1..Nw}[Awi{0.2+(Lwi/H)^2}]) and the Figure 5-1 height rule are verified against the printed pages 28-30 of NBC 105:2025 (user-supplied PDF). Page tags: §5.1 and §5.1.1 p. 28; §5.1.2 kt list, H definition, Figure 5-1 and the Aw summation p. 29; Lwi and Nw p. 30; §5.1.3, §5.2 and Table 5-1 p. 30. See the [clause 5 compliance matrix](../../../nbc105/clause_05_dynamic_characteristics_matrix.md).

## Outputs and failure conditions
Returns floats or the adopted-period dict. Non-finite or non-positive height, Awi, Lwi, Aw, empirical or Rayleigh inputs, unknown system strings, unequal Rayleigh array lengths, and non-positive Rayleigh sums raise ValueError. The basement is excluded from H only when the caller declares the Figure 5-1 condition true.

## Research and standards
NBC 105:2025 clause 5. See [period and material provenance](../../../NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md) and the [research reference register](../../../00_RESEARCH_REFERENCES.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_clause5.py -q` (hand-computed expected values) and `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-21 extension — Clause 5 beyond §5.2

The canonical module now also includes **all 21 rows of Table 5-2** (source printed p. 32) with row-numbered Rμ, Ωu and Ωs; §5.4.1 weak/soft-storey checks; §5.4.2 torsional and re-entrant thresholds; §5.5 ULS horizontal deflection multiplier, SRSS building separation and drift limits; and §5.6 ±5% accidental eccentricity.

New regression file: `tests/test_nbc105_clause5_remaining.py`. Conditions at 80%, 70%, 1.5 and 2.5 equality are explicitly tested to avoid treating strict inequalities as inclusive. **Scope caution:** a source table lookup does not verify that this thesis model qualifies for the selected structural system and its ductile detailing. The actual ETABS drift/irregularity reports and 25-storey system identification remain native-project evidence gates. The printed table of contents gives §§5.3–5.6 on pp. 30–37; older references to §5.7 for accidental torsion are not the physical §5.6 heading. Certain internal cross-references in the printed code are inconsistent and are preserved in the audit rather than silently corrected.
