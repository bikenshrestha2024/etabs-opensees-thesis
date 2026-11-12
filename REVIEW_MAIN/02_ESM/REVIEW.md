> **12 November 2026 — ESM UI, combined categorized exports and ETABS mapping safety:** [Latest evidence and correction record](20261112_ESM_GUI_EXPORT_CASE_MAPPING_AND_JOINT_GATES.md). Applied-force charts are not recovered ETABS story shear; native source EDB identity and 6m/12m Aw grouping remain open. The ESM review snapshot is deliberately copy-only and non-certified.

# ESM review — NBC 105:2025 Aw, periods and applicability
**RV-ESM-001 Aw-X opening mismatch:** P0 OPEN_HIGH
**RV-ESM-002 ESM case provenance / source identity:** P0 OPEN_HIGH
**RV-ESM-003 code eligibility, site class and period:** P0 OPEN_HIGH

## Quantified discrepancy (supplied November 11 logs)
| Basis | Aw-X (m²) | Aw-Y (m²) | Authority |
|---|---:|---:|---|
| Original ETABS-linked Excel calculation | 1.9582936288 | 2.2030803324 | Adopted research workbook method only, subject to source verification |
| OpenSees continuous-pier geometric diagnostic | 1.9306371191 | 2.2030803324 | Diagnostic **not** NBC accepted |
| OpenSees gross projected wall contribution | 3.1097618 | 2.2030803324 | Not opening-adjusted |
| X excluded projected contribution | 1.1791247 | 0 | Difference in projection terms, **not** simply a physical opening area |

Excel vs diagnostic X delta = 0.0276565097 m² (~1.412% of Excel Aw). Y agrees within rounding. Root cause is NOT established by percent closeness.

## Professional assessment
The numerical `continuous-pier` algorithm discounts wall branches not continuously reaching the base through openings. The user's Excel method handles segment widths around four nominal 2-m spandrel/opening positions differently. A wall segment above a doorway can couple two piers and contribute lateral strength/stiffness, but cannot be counted uncritically as a full uninterrupted base pier; appropriate equivalent pier lengths depend on connectivity, opening location and effective flexure-shear behavior. This is precisely why gross projection, continuous-pier diagnostic and Excel Aw differ. IS 13920:2016 ductile wall/opening detailing is a different question from the empirical NBC 105 §5.1 wall-area period index; do not substitute a detailing clause for its expression.

ETABS Direct wall audit reportedly found 375 wall objects of 600-mm main section and 100 area spandrels; 0 explicit opening area objects, and mapping four 2-m positions to nearest X walls **3 m away**. This nearest-wall assignment is a *potential geometric mapping weakness*, not proof of correct wall opening locations. Direct model must verify every pier, web/flange, wall gap and coupling beam against physical plans and source object connectivity.

**T1:** Excel-adopted X=2.0385674 s, Y=1.9219798 s are *design action periods*, not measured ETABS eigensolutions; preliminary OpenSees Rayleigh estimates near 3.8984/5.5904 s represent independent directional calculations; period differences demand stiffness/mass review. Never overwrite spreadsheet adopted values with geometric diagnostics without review.

## Code gates
NBC 105:2025 §5.1 / project workbook Aw convention must be checked with wall openings, first-storey lengths and physical base continuity; §3.2.1 limits eligible ESM for this tall/irregular building; use as comparative research, not claimed design-method acceptance. For buildings >40 m, verify measured Vs30 and actual site classification under §4.1.3.1. Verify code edition/table numbering from official PDF before claiming any certified acceptance.

## Next review evidence
1. Source EDB plus signed walls (plan/section), geometries, opening coordinates, pier/spandrel list, actual X/Y wall projected lengths and t.
2. Original workbook B4/B14/B15 formulas and hashes with exact source model; independently reconstruct each Aw term and compare to OpenSees contributions; produce before/after CSV and plan plot.
3. Modal X/Y periods and Rayleigh X/Y by storey from matched mass/stiffness, plus ESM/MRSM result differences. Human sign-off on adopted Aw and acceptance.
