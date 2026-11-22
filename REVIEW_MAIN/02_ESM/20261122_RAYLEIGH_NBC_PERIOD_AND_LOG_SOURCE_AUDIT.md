# 2026-11-22 — Source-verified Rayleigh/ESM log audit, other issues, and Clause 5 production routing

**Status:** NBC PERIOD EQUATION ROUTED TO CANONICAL CODE; PHYSICAL RAYLEIGH/ETABS EQUIVALENCE OPEN. This review inspected current active GitHub source and the **user-supplied 22 November ESM GUI log**, plus NBC 105:2025 code text; it **did not rerun Windows ETABS 23 or the private 95 m OpenSees native EDB/analysis**. Do not use this report as an engineering acceptance certificate.

**Source code:** [NBC §5 canonical](../../components/nbc105/clause_05_dynamic_characteristics.py), [Rayleigh](../../components/modal/rayleigh.py), [Rayleigh ledger](../../components/modal/rayleigh_ledger_audit.py), [ESM direct GUI](../../components/equivalent_static/calculation_and_gui.py), [source selector](../../components/inputs/project_workbooks.py), [case and workbook sources](../../docs/nbc105/clause_05_dynamic_characteristics_matrix.md).

## NBC 105:2025 verified requirements

| Code provision | Rule | Correct software contract |
|---|---|---|
| §5.1.1 Eq 5.1(1) | `T=2π sqrt(sum(Wi di²)/(g sum(Fi di)))` | all storeys; physical elastic COM lateral displacement (torsion suppressed), matched Wi/Fi and same equilibrium/stiffness; kN-m-s, `g=9.81` |
| §5.1.2 | `T_emp=(0.075/sqrt(Aw))*H**(3/4)` for concrete shear-wall building; wall `Aw=sum(Awi*(.2+(min(Lwi/H,.9))**2))` | reviewed first-storey wall grouping, openings and height |
| §5.1.3 | amplify **empirical**, not Rayleigh, by 1.25 | `T_design=min(T_R,1.25*T_emp)`; no import of eigenperiod or unverified Excel adopted values as a Rayleigh substitute |
| §5.2, Table 5-1 | `Wi=DL+.6*storage_LL+.3*other_LL+0*roof_LL` allocated between storey mid-heights | validate source ledger/model tags, heights and mass; this is **not** full `1D+1L` gravity |
| §3.2.1 | ULS high-rise ESM eligibility restrictions | 95 m current ULS ESM **comparison only**; separate dynamic method remains governing |
| §4.1.3.1 | measured `Vs,30` requirement for H>40 m | input Soil C label/municipality/Z is not a substitute for project `Vs,30` evidence |
| §5.6 | accidental eccentricity ±0.05b | full ±5% result set needs both signs when applicable; user log currently shows **E+ and E0, not E−** |

Official text: [NBC 105:2025 (Kathmandu Metropolitan electronic permit PDF)](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf), printed pp.17, 24–30, 37–39; [DUDBC code list](https://www.dudbc.gov.np/pages/building-code/).

## User's submitted log — what it establishes

- Location **Kirtipur**, soil input **C**, `Z=0.35` (reported Annex C lookup). No `Vs,30` supplied, thus site classification **NOT VERIFIED**.
- ULS source EDB path includes `ULTIMATE LOAD..._NBC105_RS_SCALED.EDB`. The reported `CROSS-STATE COMPARISON BLOCKED` message is a **correct firewall**, not a Rayleigh math fault.
- X Aw **2.07317452 m²** and Y Aw **2.20308033 m²**, grouping two 12 m walls in X and three 6 m walls in Y. Matches the model-aligned V10.7 workbook values, **not** an independent acceptance of wall effective area for actual coupling/shear behavior.
- Log states empirical ESM then **centered ULS X/Y Rayleigh**. It does not include the 25 per-floor `Wi,Fi,di` rows, their work sums, the real resulting `T_R_X, T_R_Y`, same-source mass/solver stiffness SHA or modal comparison. Therefore **the Rayleigh results shown by log messages alone cannot be independently numerically verified**.
- ULS X+ and X− each show `V=30588.941 kN`, `k≈1.5810` for E+ and E0; Y+ and Y− each show `V=26450.735 kN`, `k≈1.7110`. The identical values for different load signs/eccentricities are expected for a **pre-solver ESM force magnitude**; actual torsional member forces and reactions must be solved and compared separately.
- A total of **8 runner scripts** is reported, whereas the full X/Y×polarity±×eccentricity(E+,E−,E0) set would contain 12. The GUI default is Both ±; the supplied log is compatible with a narrower sign selection. **No E− results appear; never describe 8 as complete full eccentricity coverage.** They were created as **scripts**, not confirmed native solver-completed runs.
- Historical alternate X values in archived studies or the earlier `V=30582.206 kN` example are different source/config/period evidence, **not automatically an arithmetic conflict**. Never mix output epochs absent matching EDB, model, CSV and run SHA.

## Source-level issues corrected in this branch

1. **Automatic story input could be stale despite matching diaphragm IDs.** `recommended_story_weight_input` checked tags but not the CSV's actual heights or current `base_z_m`/master-node Z. A shifted or old ledger could be auto-selected with a misleading 'model match' label, and standalone ESM could use its story-weight data. Now the exact `verify_storey_elevations` contract is used; missing/mismatched data reject automatic selection, with optional manual path remaining explicitly review-required.
2. **Three production mathematical paths duplicated canonical Clause 5.** `components/modal/rayleigh.py` had an inline Rayleigh quotient, seismic Wi arithmetic and period minimum. `components/modal/rayleigh_ledger_audit.py` duplicated the quotient; ESM `resolve_esm_state_periods` and selected-axis GUI duplicated the period minimum. Now live paths call Clause 5 functions directly: `rayleigh_period_s`, `seismic_weight_kN`, `adopted_period_s`, `empirical_period_s` and `amplified_period_s`. No change to physical weights/loads/supports/configuration.
3. **Direct Python Rayleigh runner lacked the GUI's source limit-state firewall.** `rayleigh.run(...,limit_state='SLS')` could reach a model whose EDB was labelled ULS. Now `require_source_state` rejects it and preserves the source-state evidence. An unlabeled source remains a review gate rather than proving physical stiffness state.

Tests were authored first and deliberately failed on the old code, then run through CI. Canonical numeric test uses H=95m, Aw X/Y above; expected `T_emp_amplified_X=1.981280885026091 s`, `T_emp_amplified_Y=1.921979776706312 s`. These are source formula checks only.

## Still open — must be demonstrated on one exact current model

- **Source identity:** current EDB SHA, exported model/config SHA, exact selected assembled CSV SHA and 12 m wall opening/height provenance.
- **Rayleigh physical evidence:** each of 25 source `Wi,Fi,di`, torsion-suppressed floor COM UX/UY increments, one-step reference load factor, reaction balance, diaphragm translation spread and independent exact recomputation, with no zero/missing stories.
- **Mass/operator:** `mass_elevation_audit` is bookkeeping; wall-intermediate mesh mass lumping to the NBC mid-height ledger is not automatically equivalent to the 3D eigen mass operator. Compare with matched source ETABS and a same-domain OpenSees eigenanalysis.
- **Source support and stiffness:** 32 physical foundations, 44 shell mesh-edge points, 76 source-restraint scenario and the full native `@LC` constraints/rigid-end effects; the 768.045-kN worst 32-point gravity residual remains open ([issue #140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140)).
- **ULS/SLS and ESM/MRSM:** independent matched SLS EDB if cross-state comparison requested; ULS-only high-rise ESM for §7.5 response-spectrum *base shear* reference only where required, not a high-rise ESM design certificate; use dynamic method and preserve unscaled drifts.
- **Site hazard:** actual `Vs,30` for 95 m structure, code-consistent site class; source `Z=0.35` must be independently checked against actual municipality/Annex C. Provide both ±5% eccentricity signs, distinct load signs and solver confirmation.
- **Nonlinear readiness:** first-step X-wall nonfinite response, calibrated material/connection evidence and M0–M6 full histories unresolved.

## Regression evidence path

`tests/test_rayleigh_direct_clause5_routing.py` and `tests/verify_esm_source_selection.py`; use source workflow CI on PR before merge. A green CI is **source/logic verification**, not a fresh real-model NBC engineering acceptance.

### Known data-quality limitation in attached V10.7 model-aligned workbook

Prior independent workbook inspection found some downstream `WALL SUMMARY V6` and `12m WALL GEOMETRY AUDIT` formula cells did not carry cached numeric values. `openpyxl(data_only=True)` cannot calculate missing values; a missing cached result must not be silently read as zero or replaced by an old Excel file. The model-aligned summary's numeric Aw X/Y entries exist. **No XLSX bytes changed or uploaded to public GitHub during this work.**
