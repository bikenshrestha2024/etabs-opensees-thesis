# annex_c_zoning.py — source documentation

**Python source:** [components/nbc105/annex_c_zoning.py](../../../../components/nbc105/annex_c_zoning.py)
**Data:** [docs/nbc105/annex_c/TABLE_C1_PROJECT_ROWS.csv](../../../nbc105/annex_c/TABLE_C1_PROJECT_ROWS.csv)
**Git baseline content SHA:** NEW (added 2026-11-26)
**Subsystem:** NBC 105:2025 clause modules (Annex C)
**Priority:** P1 — Annex C is the only annex required now (owner declaration, PROJECT_DECLARATIONS.md section 6)

## Responsibilities and contracts
Transcribes only the Table C-1 rows the project needs and exposes them with hash verification. Table C-1 (printed pp. 100-114, columns SN, District, Local Units, PGA) gives the seismic zoning factor Z; printed 4.1.4 (p. 26) says the Table value is taken, not interpolated from Figure 4-3, for listed municipalities. The CSV holds the column header, the project row (serial 346, Kathmandu, Kirtipur Nagarpalika, printed p. 106, 0.35), the complete Kathmandu district block 340-350 (all 0.35) and two rows with other values (326 Kapilbastu 0.4, 335 Kaski 0.3) that prove the value column alignment. Each row has the printed page, the PDF page (129), the printed text and a SHA-256 of the whitespace-normalised text. Figure 4-3 (page numbered 25, PDF page 48; legend contours 0.25, 0.30, 0.35, 0.40) is recorded as NOT used by the project. All other rows (753 in the table) are EXTERNAL_DATA_REQUIRED and out of project scope.

Functions: `load_table_c1_project_rows` (verifies hashes, header, page, value set), `table_c1_value` (raises `TableC1DataRequired` for any untranscribed unit; never guesses), `project_zoning_factor` (Z = 0.35, serial 346, `figure_4_3_used` False).

## Source, inputs, units
Dimensionless Z (fraction of g). Names are compared on the printed spelling ("Kirtipur Nagarpalika"; Table 4-3 prints the same unit as "Kirtipur Municipality").

## Outputs and failure conditions
`TableC1IntegrityError` for a changed row, wrong page or column label, value outside 0.25/0.30/0.35/0.40 or a missing project row. Tests: `tests/test_nbc105_followup_annex_c.py` (includes an optional cross-check against the PDF text layer).

## Research and standards
NBC 105:2025 Annex C and clause 4.1.4. Source-to-code review only; not a hazard study.
