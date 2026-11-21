# clause_04_seismic_hazard.py — source documentation

**Python source:** [components/nbc105/clause_04_seismic_hazard.py](../../../../components/nbc105/clause_04_seismic_hazard.py)
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** NBC 105:2025 clause modules
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Pure-Python implementation of NBC 105:2025 clause 4 (printed pp. 22-27): Eq. 4.1(1) `C(T) = Ch(T) Z I`; Eq. 4.1(2) spectral shape factor with the Table 4-1 parameters for soil A-D (`spectral_shape_factor`, method `"equivalent_static"` with Ta = 0 per the Table 4-1 footnote, or `"dynamic"` for modal response spectrum, nonlinear time history, vertical loading and parts and components); Table 4-4 importance factor (`importance_factor`, 1.5 for a class II disaster shelter); Eq. 4.2(1) `Cs = 0.20 C` (`serviceability_spectrum`); Eq. 4.3(1) `Cv = 2/3 Z` (`vertical_spectrum_coefficient`) with the five §4.3 conditions in `VERTICAL_LOADING_CASES`; §4.1.3.2 `vs30_from_layers`; Table 4-2 classifiers `soil_type_from_vs30`, `soil_type_from_n_spt`, `soil_type_from_cu`; `select_soil_type` (Vs,30 preferred; required by §4.1.3.1 above 40 m but optional for this thesis, USER_DECLARED 2026-11-21, so a missing Vs,30 is reported as issue `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED`, never raised; `soil` comes from N_SPT when given, else None); Table 4-3 as `KATHMANDU_VALLEY_SOIL_D_SITES` with `default_soil_type_d`. `validate_zoning_factor` only range-checks Z (0 < Z <= 0.4); Table C-1 of Annex C and Figure 4-3 interpolation are not transcribed, so the caller supplies Z. The module is not yet called by production code; parity with the existing implementations is audited separately. A spectrum value is a design-input calculation, not engineering acceptance.

## Source, inputs, units
Periods in s, Vs,30 in m/s, layer thickness and building height in m, Cu in kPa, N_SPT in blows/30 cm; Z, Ch, I, C dimensionless. Transcribed 2026-11-21 from page images of the user-supplied PDF (PDF pages 42-50). Page tags: Eq. 4.1(1) p. 22; Eq. 4.1(2) p. 23; Table 4-1, §4.1.3.1-4.1.3.2 p. 24; Table 4-2 and §4.1.3.3 p. 25; Table 4-3, §4.1.4 and Table 4-4 p. 26; §4.2 and §4.3 p. 27. Printed-page notes: Table 4-3 and Table 4-4 are both on a page numbered 26; the Figure 4-3 page is numbered 25 (rotated); the last sentence of §4.1.4 says "Figure 4-4" where Figure 4-3 is meant. Table 4-3 prints the Kathmandu Metropolitan City wards as "...,30,32,32"; the duplicate is stored once as ward 32 and may be a misprint.

## Outputs and failure conditions
Floats, soil letters, or the `select_soil_type` dict `{soil, basis, issues}`. T < 0, NaN, T > 6 s (never extrapolated), unknown soil or method, non-finite or non-positive inputs, Z outside (0, 0.4], layer thicknesses not summing to 30 m, and an unknown importance class raise ValueError. `default_soil_type_d` returns False for sites not in Table 4-3 (not listed is not a soil finding) and raises ValueError when a partially listed municipality is queried without a ward. Table 4-2 gives no N_SPT or Cu value for soil A, so those classifiers never return A.

## Research and standards
NBC 105:2025 clause 4. See the [research reference register](../../../00_RESEARCH_REFERENCES.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_clause04.py -q` (hand-computed expected values and a Table 4-3 transcription check) and `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
