# ETABS six-lot export consistency audit (2026-11-28)

**Status: `REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.** Machine-readable evidence: [`20261128_ETABS_LOT_CONSISTENCY_AUDIT.json`](20261128_ETABS_LOT_CONSISTENCY_AUDIT.json) (aggregates and hashes only; no raw rows, no local paths). Produced by `tools/audit_etabs_lot_consistency.py` from the real workbooks; source EDB SHA and OpenSees node map were not available, so ETABS/OpenSees equivalence is `NOT_VERIFIED`.

## Inventory (actual workbooks, read-only, every populated cell)

9 workbooks supplied: FIRST, SECOND, THIRD, FOURTH, FOURTH part 1/2/3, FIFTH, SIXTH_real. 55 worksheets in total across them, all fully scanned: 9,648,871 non-empty rows, 173,117,043 populated cells. The audit file records name, SHA-256 and worksheet inventory of each. **Beam-force workbooks 1/2/3 were not attached**; nothing was inferred for them.

Ingested as one reference: lots 1, 2, 3, 4, 5, 6 (46 reference tables, none of the required tables missing). Parts 1/2/3 of the fourth lot were used only for the overlap check.

## Findings

| Finding | Evidence | Action |
|---|---|---|
| FOURTH combined lot duplicates its three parts | 8 sheets (Element Forces Braces/Columns, Element Joint Forces Frame/Shells, Element NL Energy By Group, Element Strains/Stresses Area Shells, Integrated Wall Reactions) are byte-identical in lot 4 and parts 1-3 | Load combined OR parts, never both; the reader already rejects double ingest |
| `Joint Reactions` = `Joint Design Reactions` | 21,356 identical rows each | Keep separate ownership; do not count twice |
| 32 supports + 44 inert mesh points | 76 Base joints; derived tags equal `PROJECT_PRIMARY_32`; 44 rows zero in all six components | Preserved; the 44 are not restraints |
| Export g is 9.80665, project g is 9.81 | Σ(vertical mass)·9.80665 = 277,767.306 kN vs Dead+0.3·Live (residual -0.0076 kN); with 9.81 the residual is +94.9 kN, implied live fraction 0.30198 | **Needs your decision.** Not changed. Masses rebuilt as weight/9.81 are 0.034% lighter than ETABS masses |
| Seismic mass source | Dead + 0.3·Live; non-Base horizontal mass × 9.80665 = 275,628.40 kN | Reference for NBC 105 Table 5-1 ledger comparison; not certification |
| Base reactions equal summed joint reactions | 55 additive rows, 0 unmatched; max force residual 0.0008 kN, max moment residual 0.363 kN·m (moment transfer M = Mj + r×F) | Six-component equilibrium holds for every additive row |
| Time-history is envelope-only | 226 Max/Min rows, no step series | Cannot drive or step-compare NLTHA; envelopes are targets only and are never summed |
| Extra time-history events | 11 events/22 cases exported; Darfield, San Fernando, Tabas are outside the 8-pair Soil-C set; all 8 contract events present and paired | Do not use the extras for the 8-pair mean |
| Mixed `P-Delta` / `P Delta` case names | in the export | Match names normalised |
| No RZ mass participation | Ritz modes (15), RZ sum 0.0; UX/UY reach 90% at mode 6/8 (sums 0.988/0.985) | Torsion is not captured by this modal set; RX 0.930, RY 0.899 |
| Periods rounded to the millisecond | up to 0.43% relative error vs circular frequency | Use CircFreq, not Period |

## Acceptance register (honest status)

| Item | Status from this audit |
|---|---|
| Base mesh 44/44 mapped; 32 supports | Observed in ETABS export; OpenSees mapping not verified |
| Storey mass, rotational inertia, rigid-end zones 1200, native edge assignments 725, generated edge 411 | Not re-derivable from these workbooks (no `end_offsets_m`, no EDB); remain with the existing native gates |
| 768.045 kN / 3041.266 kN residuals | Different runs; unresolved; native rerun required |
| Six-component equilibrium | Satisfied inside ETABS export for 55 additive rows (above) |
| Eight base-force cases unreconciled | All additive rows reconcile; the eight cannot be settled from envelope rows |
| M0-M6 NLTHA, NBC 105:2025 | Not certified; THESIS_NLTHA gate unchanged |

## Reproduce

```
python tools/audit_etabs_lot_consistency.py --analysis-files <lots 1-6> --duplicate-check-files <fourth parts 1-3> --output out.json
```
