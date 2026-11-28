# ETABS analysis-lot consistency diagnostics

**Canonical source:** [`components/validation/etabs_lot_consistency.py`](../../../../components/validation/etabs_lot_consistency.py)
**Run it with:** [`tools/audit_etabs_lot_consistency.py`](../../../../tools/audit_etabs_lot_consistency.py)
**Evidence:** [`docs/validation/20261128_ETABS_LOT_CONSISTENCY_AUDIT.md`](../../../validation/20261128_ETABS_LOT_CONSISTENCY_AUDIT.md)

## Function and evidence boundary

Reference-only checks over ETABS analysis-export rows already ingested by `components/inputs/etabs_table_bundle.py` (SI-normalised: kN, m, kg). Nothing edits a model, workbook or OpenSees input. Results are `ETABS_OPENSEES_MATCHED: NOT_VERIFIED`; a derived support tag is an observed ordering rule, not a CSI API restraint.

| Function | What it establishes | Input |
|---|---|---|
| `derive_primary_support_tags` | Base joints ranked by (X, Y); the joints with nonzero FZ in `1. DL + LL` are the 32 supports and the other 44 carry exactly zero in all six components | joint table, one case of `Joint Reactions` |
| `seismic_mass_source_identity` | `sum(UZ)*g` against Dead + f·Live for each candidate g; implied live fraction; non-Base horizontal mass as seismic weight | `Assembled Joint Masses`, joint table, Dead/Live sums |
| `base_reaction_equilibrium` | Six-component Base Reactions against summed joint reactions with moment transfer `M = Mj + r x F`; Max/Min envelope rows are counted, never passed or failed | `Base Reactions`, `Joint Reactions`, joint table |
| `time_history_step_availability` | Whether `NonModHist` rows are a step series or Max/Min envelopes only | any table with `Case Type` and `Step Type` |
| `classify_time_history_cases` | Event pairing (`X` / `X-1`), contract-set coverage, events beyond the 8-pair Soil-C set, mixed `P-Delta` / `P Delta` spelling | case names |
| `modal_participation_diagnostics` | Torsional (RZ) participation, mass-participation target mode, export period rounding | modal tables |
| `table_data_identity` | Two tables hold the same data rows (worksheet row ignored) | two row iterables |
| `classify_lot_overlap` | A combined lot that repeats its split parts byte for byte | `audit_analysis_workbooks` result |
| `time_history_reference_envelopes` | Per-case ETABS base-shear, roof CM displacement and story-drift envelopes as OpenSees comparison targets | `Base Reactions`, `Diaphragm CM Displacements`, `Story Drifts` |
| `lot_consistency_report` | Runs the above and lists findings with severity | a source with `.analysis["tables"]` and `.rows(table, case=)` |

`AnalysisReferenceRows` reads the SQLite store written by `read_analysis_reference`; `CombinedReference` offers the same interface.

## Invariants kept

* 32 physical supports and 44 inert shear-wall mesh points are reported, never converted into 44 restraints.
* Full gravity (`1. DL + LL`) and seismic mass (Dead + 0.3 Live in this export; NBC 105:2025 Table 5-1 classification) stay separate ledgers.
* `g` is reported, not changed: the project value is `components.nbc105.constants.GRAVITY_M_S2`; the export-implied value is a finding.
* Envelope rows are never summed as if additive.

## Findings on the real six-lot export

See the evidence report. Highest-impact: export `g` is 9.80665 while the project uses 9.81; time-history tables are envelope-only; Darfield, San Fernando and Tabas are not in the 8-pair set; Ritz modes carry zero RZ participation.
