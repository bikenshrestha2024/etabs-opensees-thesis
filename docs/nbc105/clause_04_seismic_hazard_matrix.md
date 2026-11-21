# NBC 105:2025 clause 4 compliance matrix (printed pp. 21-27)

Date 2026-11-21. Reference module: [`components/nbc105/clause_04_seismic_hazard.py`](../../components/nbc105/clause_04_seismic_hazard.py) ([guide](../source/components/nbc105/clause_04_seismic_hazard.py.md)). Clause text and tables were read from the printed pages of the user-supplied PDF (printed page N = PDF page N+21 up to printed p. 26 and N+23 from printed p. 27 on; Figure 4-3 page is PDF 48).

Status values: `IMPLEMENTED_AND_TESTED` (code and unit test exist, text checked against the printed page); `REFERENCE_ONLY` (the clause module implements and tests the rule, but production code does not call it; production code carries its own copy, see Findings); `USER_RESPONSIBILITY` (site data the software cannot supply); `NOT_TRANSCRIBED` (printed source not transcribed into code).

**Limits.** This matrix records software conformance of the clause 4 arithmetic only. It is not design acceptance of any building, not an ETABS or OpenSees run, and a unit-test pass is not engineering acceptance. Native ETABS/OpenSees runs are PENDING.

Tests: `T4` = `tests/test_nbc105_clause04.py`, `TP` = `tests/test_nbc105_clause04_parity.py`.

| # | Clause | Printed page | Requirement | Code location | Test | Status |
|---|---|---|---|---|---|---|
| 1 | §4.1.1 Eq. 4.1(1) | 22 | C(T) = Ch(T) Z I | `elastic_site_spectrum`; production copies: `site_spectrum_and_scaling.elastic_site_spectrum_g`, `equivalent_static/code_basis.calculate_esm`, `nbc105_dual_target.target_nltha_g` | `T4::SpectrumTests::test_c_and_cs`; `TP::SpectrumAssemblyParity` | IMPLEMENTED_AND_TESTED (production copies agree, see Findings) |
| 2 | §4.1.2 Eq. 4.1(2) | 23 | Ch(T): `1+(alpha-1)T/Ta` for T<Ta; `alpha` for Ta<=T<Tc; `alpha Tc/T` for Tc<=T<Td; `alpha Tc Td/T^2` for Td<=T<=6 | `spectral_shape_factor` (rejects T<0, NaN, T>6, unknown soil/method) | `T4::test_hand_values`, `test_ramp`, `test_continuity_all_soils`, `test_rejections`; `TP::ShapeFactorParity` | IMPLEMENTED_AND_TESTED |
| 3 | §4.1.2 Table 4-1 | 24 | Ta 0.1/0.1/0.1/0.5; Tc 0.5/0.7/1.0/2.0; Td 4.0/4.0/4.0/5.0; alpha 2.5/2.5/2.5/2.25 (soil A/B/C/D) | `TABLE_4_1`; copies in `NBC105_SOIL_PARAMETERS`, `NBC105_ESM_SOIL_PARAMETERS`, `nbc105_dual_target.SOIL` (C, D only), `reconcile.soil_c_modal_ch` (C) | `T4::test_table_4_1_transcription`; `TP::test_site_spectrum_table_matches_table_4_1`, `test_modal_nltha_*`, `test_reconcile_soil_c_helpers` | IMPLEMENTED_AND_TESTED |
| 4 | Table 4-1 footnote 1 | 24 | Ta is zero for the Equivalent Static Method | `spectral_shape_factor(method="equivalent_static")` | `T4::test_esm_ta_zero`; `TP::test_esm_ch_at_zero_is_alpha_for_all_soils`, `test_esm_code_basis_and_legacy` | IMPLEMENTED_AND_TESTED |
| 5 | Fig. 4-1 / Fig. 4-2 variant choice | 22-23 | Fig. 4-1 = ESM (flat at alpha from T=0); Fig. 4-2 = modal response spectrum, nonlinear time history, vertical loading, parts and components (full Eq. 4.1(2)) | `method` argument of `spectral_shape_factor`; production: `esm_spectral_shape_factor` (ESM), `spectral_shape_ch(..., "esm"/"dynamic")`, `ch_modal_nltha` | `TP::ShapeFactorParity` | IMPLEMENTED_AND_TESTED (the text of §4.1.2 says Fig 4-1(a)/(b); the printed figures are Fig 4-1 and Fig 4-2, see Findings) |
| 6 | §4.1.3.1 | 24 | Classify by Vs,30 when available, otherwise N_SPT | `select_soil_type` | `T4::SoilTests::test_select_soil_type` | IMPLEMENTED_AND_TESTED |
| 7 | §4.1.3.1 | 24 | Buildings higher than 40 m: Vs,30 required (optional for this thesis, USER_DECLARED 2026-11-21; requirement stays documented) | `select_soil_type` (no raise; issue `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED`; soil from N_SPT when given, else None), `MANDATORY_VS30_HEIGHT_M`; production: `calculate_esm` reports `site_subsoil_status` NOT VERIFIED | `T4::SoilTests::test_select_soil_type`; `TP::test_calculate_esm_height_over_40m_without_vs30_not_verified` | IMPLEMENTED_AND_TESTED |
| 8 | §4.1.3.2 | 24 | Vs,30 = 30 / sum(hi/Vi) over the top 30 m, with layer velocities measured at shear strain ≤ 10⁻⁵ | `vs30_from_layers` (thickness must total 30 m) | `T4::SoilTests::test_vs30_formula` | CALLER_RESPONSIBILITY; formula tested, the caller must establish and document the measurement strain. |
| 9 | Table 4-2 (Vs,30 and N_SPT, Cu) | 25 | A Vs>800; B 350<Vs<=800 (N>50, Cu>250 kPa); C 150<Vs<=350 (N 10-50, Cu 25-250); D Vs<=150 (N<10, Cu<25) | `soil_type_from_vs30`, `soil_type_from_n_spt`, `soil_type_from_cu`; production: `code_basis.soil_type_from_vs30`, `soil_type_from_n_spt` | `T4::test_vs30_boundaries`, `test_nspt_cu_boundaries`; `TP::SoilClassifierParity` (149.999, 150, 150.001, 350, 350.001, 800, 800.001; N 9.9, 10, 50, 50.1) | IMPLEMENTED_AND_TESTED |
| 10 | §4.1.3.3 | 25-26 | Listed Kathmandu-Valley municipalities and wards are Soil Type D by default unless tests to 30 m show otherwise | `default_soil_type_d`; no production caller | `T4::KathmanduTable43Tests::test_lookups` | REFERENCE_ONLY |
| 11 | Table 4-3 | 26 | 21 rows (10 Kathmandu, 7 Lalitpur, 4 Bhaktapur) with ward lists | `KATHMANDU_VALLEY_SOIL_D_SITES` | `T4::KathmanduTable43Tests::test_transcription_check` | IMPLEMENTED_AND_TESTED (printed KMC list ends "30,32,32"; kept as 32, possible misprint) |
| 12 | §4.1.4 Z (map) | 25-26 | Z is the 475-year PGA, interpolated from Figure 4-3 contours 0.25, 0.30, 0.35, 0.40 | `validate_zoning_factor` (finite, 0 < Z <= 0.4 only) | `T4::SpectrumTests::test_zoning_validation` | NOT_TRANSCRIBED (Figure 4-3 interpolation); site Z is USER_RESPONSIBILITY |
| 13 | §4.1.4 Z (Annex C) | 26 | Table C-1 of Annex C governs for listed cities and municipalities | none | none | NOT_TRANSCRIBED (Annex C Table C-1) |
| 14 | §4.1.5 Table 4-4 | 26 | Importance class I 1.0, II 1.25, III 1.5; 1.5 for class II used as disaster shelter | `importance_factor`; production code takes I as user input (`calculate_esm`, `elastic_site_spectrum_g`, `target_nltha_g`) and does not enforce Table 4-4 | `T4::SpectrumTests::test_importance`; `TP::test_importance_factor_values_supplied_by_user_not_validated` | IMPLEMENTED_AND_TESTED (clause module); USER_RESPONSIBILITY for the project I |
| 15 | §4.2 | 27 | Cs(T) = 0.20 C(T) | `serviceability_spectrum`; production: `calculate_esm` SLS branch, `reconcile.static_parameters` | `T4::test_c_and_cs`; `TP::test_calculate_esm_uls_and_sls_spectrum`, `test_reconcile_serviceability_uses_020`, `test_serviceability_020_only_in_reviewed_locations` | IMPLEMENTED_AND_TESTED |
| 16 | §4.3 | 27 | Cv(Tv) = 2/3 Z | `vertical_spectrum_coefficient`; no production code applies it | `T4::test_vertical`; `TP::test_no_production_code_applies_vertical_two_thirds_z` | REFERENCE_ONLY |
| 17 | §4.3 a)-e) | 27 | Vertical loading applies to spans >= 20 m, cantilevers > 5 m, pre-stressed horizontal members, beams supporting columns, base-isolated structures | `VERTICAL_LOADING_CASES`; production applicability review: `nbc105_horizontal_input.vertical_acceleration_review` (five matching triggers) | `T4::test_vertical`; `TP::test_vertical_review_triggers_match_clause_4_3` | IMPLEMENTED_AND_TESTED |

## Findings

Reference for every comparison: the clause module, built from the printed pages. Every comparison below was run in `TP` on the grid T = 0, 0.05, 0.1, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0 plus Ta, Tc, Td +/- 1e-9 for all four soils (values outside 0..6 dropped), and on rejection cases T < 0, NaN, inf and 6 s + 1e-9.

| Implementation | File | Compared with | Status |
|---|---|---|---|
| `esm_spectral_shape_factor` (V109) | `components/equivalent_static/code_basis.py` | ESM, soils A-D, grid | PASS on values. FINDING F1 (T > 6 s and NaN accepted) fixed |
| `esm_spectral_shape_factor` (V108) | `components/equivalent_static/legacy_code_basis.py` | ESM, soils A-D, grid | PASS on values. FINDING F1 fixed |
| `spectral_shape_ch` (methods `esm`, `dynamic`) | `components/response_spectrum/site_spectrum_and_scaling.py` | ESM and dynamic, soils A-D, grid, rejections | PASS |
| `elastic_site_spectrum_g` | same file | `elastic_site_spectrum` for both methods | PASS |
| `ch_modal_nltha`, `target_nltha_g` | `components/response_spectrum/nbc105_dual_target.py` | dynamic, soils C and D, grid; C(T)/1.4 | PASS (scope note F3) |
| `soil_c_modal_ch`, `soil_c_static_ch`, `static_parameters` | `tools/etabs_period_review/reconcile.py` | dynamic and ESM soil C, grid, ULS and SLS (0.20) coefficients | PASS |
| `soil_type_from_vs30`, `soil_type_from_n_spt` | `components/equivalent_static/code_basis.py` | Table 4-2 boundaries, clause module | PASS |
| `soil_type_from_*` | `components/equivalent_static/legacy_code_basis.py` | n/a | Not present in V108 (F4) |
| `calculate_esm` SLS `0.20*C(T)`, ULS `C/(Rmu*Omega_u)`, >40 m without Vs,30 status | `code_basis.py`, `legacy_code_basis.py` | `serviceability_spectrum`, `elastic_site_spectrum`, `select_soil_type` | PASS (soil classifier checks only in `code_basis.py`) |
| Vertical 2/3 Z | whole repository (`rg`) | n/a | No production use; applicability review has the five §4.3 triggers (PASS) |
| Importance factor | whole repository (`rg`) | Table 4-4 | Always a user input; not validated against Table 4-4 (F5) |

Findings
- F1 (fixed). `code_basis.py:243` and `legacy_code_basis.py:243` `esm_spectral_shape_factor` extrapolated Eq. 4.1(2) beyond 6 s and returned NaN for NaN input (printed p. 23 limits the equation to T <= 6 s). Before: soil C, T = 6.5 returned 2.5*1.0*4.0/6.5^2 = 0.23669; NaN returned NaN. After: ValueError for T > 6 and for non-finite T. Values for 0 <= T <= 6 are unchanged. `calculate_esm` already rejected non-finite T, so only T > 6 s changes behaviour for the ESM path.
- F2 (printed text). §4.1.2 says Fig 4-1(a)/(b), but the printed figures are Fig 4-1 (ESM, Ta = 0) and Fig 4-2 (MRSM, nonlinear time history, vertical loading, parts and components). Code follows the figures, Eq. 4.1(2) and Table 4-1. The docstrings of `esm_spectral_shape_factor` still say "Figure 4-1(a)"; left unchanged (comment only).
- F3 (scope, not a mismatch). `ch_modal_nltha` and `nbc105_dual_target.SOIL` serve soils C and D only and refuse A and B; `soil_c_*` helpers serve soil C only.
- F4 (scope). `legacy_code_basis.py` is the frozen V108 predecessor and has no soil classifiers; `code_basis.py` (V109) has them.
- F5 (user responsibility). No production code checks I against Table 4-4 (1.0, 1.25, 1.5); callers pass the project value.
- F6 (printed text). Table 4-3 and Table 4-4 both appear on a page numbered 26; the Figure 4-3 page is numbered 25; the last sentence of §4.1.4 refers to "Figure 4-4" (Figure 4-3 intended); the KMC ward list prints "32,32".
- F7 (production copies). Each production implementation keeps its own copy of the Table 4-1 parameters rather than calling the clause module; parity is guarded by `TP` only. Replacing the copies by the clause module is not done in this task.

## Project use

- The repository's soil-C target spectra are produced by `nbc105_dual_target.target_nltha_g` (`34_NBC105_RC_DUAL_C_D_TARGETS.py`), the Soil C NLTHA suite and preflight (`components/nonlinear_time_history/soil_c_*.py`) and the ETABS period review (`tools/etabs_period_review/reconcile.py`). They are compared above against Eq. 4.1(2) and Table 4-1 for soil C; that comparison covers the arithmetic only.
- Clause 4.1.3.3 makes the listed Kathmandu-Valley municipalities and wards Soil Type D by default. Soil C for a site listed in Table 4-3 requires demonstrated test results to a depth of 30 m; the default-D rule is not applied automatically anywhere in production code (row 10, REFERENCE_ONLY).
- Vs,30 testing is required by §4.1.3.1 for buildings higher than 40 m. It is optional for this thesis (USER_DECLARED 2026-11-21, [project declarations](PROJECT_DECLARATIONS.md) section 4): `select_soil_type` reports the requirement as issue `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED` instead of raising, and a soil class for such a building that rests on N_SPT remains a documented deviation from the printed clause.
- This matrix does not decide the project site, its municipality or ward, or its soil type. Those remain `USER_RESPONSIBILITY`; the project's Soil C choice must be supported by site data supplied by the user.
