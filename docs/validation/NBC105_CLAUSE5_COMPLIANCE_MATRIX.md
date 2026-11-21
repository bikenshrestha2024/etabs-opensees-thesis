# NBC 105:2025 clause 5 compliance matrix (printed pp. 28-30)

Date 2026-11-21. Source of truth in code: [`components/modal/nbc105_clause5.py`](../../components/modal/nbc105_clause5.py) ([guide](../source/components/modal/nbc105_clause5.py.md)). Clause text, including Eq. 5.1(1), the shear-wall kt equation and the Figure 5-1 height rule, was verified against the printed pages 28-30 of NBC 105:2025 (user-supplied PDF).

Status values: `IMPLEMENTED_AND_TESTED` (code and unit test exist, clause text checked against the printed page); `CALLER_RESPONSIBILITY` (the module cannot judge it; the caller or the ETABS/assembly ledger must supply it correctly).

**Limits.** This matrix records software conformance of the period arithmetic only. It is not design acceptance of any building, not an ETABS or OpenSees run, and a unit-test pass is not engineering acceptance. Native ETABS/OpenSees runs are PENDING.

Tests: `T5` = `tests/test_nbc105_clause5.py`, `TC` = `tests/test_nbc105_clause5_callsites.py`.

| # | Clause | Printed page | Requirement | Code location | Test | Status |
|---|---|---|---|---|---|---|
| 1 | §5.1 | 28 | Adopted period is the lesser of Rayleigh and the amplified empirical period; missing Rayleigh gives no adopted period | `adopted_period_s` | `T5::test_adopted_is_lesser_of_rayleigh_and_amplified`, `T5::test_adopted_none_without_rayleigh`, `TC::test_estimate_matches_clause5_module` | IMPLEMENTED_AND_TESTED |
| 2 | §5.1.1 Eq. 5.1(1) | 28 | T = 2 pi sqrt(sum(Wi di^2) / (g sum(Fi di))) | `rayleigh_period_s`; `components/modal/rayleigh.py` reconstruction | `T5::test_rayleigh_single_dof_equals_2pi_sqrt_m_over_k` | IMPLEMENTED_AND_TESTED |
| 3 | §5.1.2 Eq. 5.1(2) | 29 | Temp = kt H^0.75 | `empirical_period_s` | `T5::test_empirical_concrete_mrf` | IMPLEMENTED_AND_TESTED |
| 4 | §5.1.2 kt list | 29 | 0.075 concrete MRF; 0.085 steel MRF; 0.075 steel EBF; 0.05 other | `KT_BY_SYSTEM` | `T5::test_kt_table` | IMPLEMENTED_AND_TESTED |
| 5 | §5.1.2 shear-wall kt | 29 | kt = 0.075/sqrt(Aw), Aw = sum_{i=1..Nw}[Awi{0.2+(Lwi/H)^2}] | `effective_wall_area_m2`, `empirical_period_s` | `T5::test_empirical_shear_wall_uses_aw`, `TC::test_estimate_matches_clause5_module` | IMPLEMENTED_AND_TESTED |
| 6 | §5.1.2 H definition, Figure 5-1 | 29 | H is base to roof | `building_height_m` | `T5::test_building_height_basement_rules` | IMPLEMENTED_AND_TESTED |
| 7 | §5.1.2 Awi | 30 | Awi is the first-storey effective wall cross-section area of wall i | `effective_wall_area_m2` argument `Awi_m2`; callers: `components/inputs/aw_sources.py`, `grouped_wall_aw.py` | `T5::test_aw_rejects_nonpositive` | IMPLEMENTED_AND_TESTED (value supplied by caller, see 15) |
| 8 | §5.1.2 Lwi | 30 | Lwi is the first-storey wall length in the considered direction; Lwi/H <= 0.9 | `effective_wall_area_m2`, `LWI_OVER_H_MAX` | `T5::test_aw_clamps_lwi_over_h_at_0_9` | IMPLEMENTED_AND_TESTED |
| 9 | §5.1.2 Nw | 30 | Nw is the number of walls in the considered direction (X and Y evaluated separately) | `nbc105_period_estimate` (separate `wall_aw_x_m2`, `wall_aw_y_m2`) | `TC::test_estimate_matches_clause5_module` | IMPLEMENTED_AND_TESTED |
| 10 | §5.1.3 | 30 | Amplification 1.25; any other value is rejected or reported as a DEVIATION, never applied | `amplified_period_s`, `period_factor_deviation`; routed in `analysis.py`, `rayleigh.py`, `analysis_autofill.workbook_adopted_period`, `equivalent_static/calculation_and_gui.py` | `T5::test_amplification_is_1_25_and_other_rejected`, `T5::test_period_factor_deviation_message`, `TC::test_autofill_reports_deviation_for_factor_1_5` | IMPLEMENTED_AND_TESTED |
| 11 | §5.1.3 scope | 30 | 1.25 applies to the §5.1.2 approximate period only, never to the Rayleigh period | `adopted_period_s` (factor applied to the empirical value only) | `T5::test_adopted_is_lesser_of_rayleigh_and_amplified` | IMPLEMENTED_AND_TESTED |
| 12 | §5.2 Table 5-1 | 30 | Seismic weight = dead + 0.60 storage live + 0.30 other live + 0 roof live | `seismic_weight_kN`, `LIVE_LOAD_FACTORS` | `T5::test_seismic_weight_table_5_1_roof_zero` | IMPLEMENTED_AND_TESTED |
| 13 | §5.2 Wi (cited in §5.1.1) | 28, 30 | Wi is dead plus factored live load between the mid-heights of the adjacent storeys | `storey_index_for_elevation` in the clause 5 module; used by the story ledger in `components/model/assembly.py` (loop after `story_rows`). Nodes below the first floor stay with floor 1 so total weight is preserved; 0.6/0.3/0 factors unchanged. Exports must be re-assembled; previously saved CSVs are unchanged | `T5::StoreyIndexTests`; `callsites::AssemblyUsesMidHeightRule` | IMPLEMENTED_AND_TESTED |
| 14 | §5.1.2 / Figure 5-1 basement | 29 | H excludes the basement only if the basement walls are connected with the ground-floor slab OR fitted between the building columns; otherwise the basement is included | `building_height_m(basement_excluded=...)` defaults to included; `components/inputs/analysis_autofill.py` takes H = max node z - base_z_m with no basement judgement | `T5::test_building_height_basement_rules` (function only) | CALLER_RESPONSIBILITY |
| 15 | §5.1.2 wall grouping around openings | 29-30 | Which walls count in Aw and their effective Awi and Lwi around openings | `components/inputs/grouped_wall_aw.py` and `aw_sources.py` give illustrative or workbook values; no geometry inference | none | CALLER_RESPONSIBILITY |

## Call sites routed through the module

`components/modal/analysis.py` (`nbc105_period_estimate`), `components/modal/rayleigh.py` (empirical and amplified values in the Rayleigh audit and workbook), `components/inputs/analysis_autofill.py` (`workbook_adopted_period`), `components/equivalent_static/calculation_and_gui.py` (four sites; tkinter code checked with `python -m py_compile` only), `components/inputs/grouped_wall_aw.py` (single-wall factor). The response-spectrum period defaults reach the module through `nbc105_period_estimate`.
