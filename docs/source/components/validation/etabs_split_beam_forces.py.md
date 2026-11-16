# ETABS split beam-force source importer

**Implementation:** components/validation/etabs_split_beam_forces.py

## Purpose
Read ETABS Element Forces - Beams force-station rows when the native full-table XLSX sheet reached the 1,048,576 row Microsoft Excel cap. Multiple smaller workbook exports can be independently SHA-256 fingerprinted, deduplicated and emitted as UTF-8 CSV without a workbook row limit.

## Inputs and output
- Input: one or more local original ETABS .xlsx files with exactly one worksheet containing Story, Unique Name, Output Case and Station columns.
- Case gate: 1. DL + LL, not seismic 0.3L preload or 1.5(DL+LL).
- CLI: python -m components.validation.etabs_split_beam_forces OUTPUT_DIR PART1.xlsx PART2.xlsx PART3.xlsx
- Output: ETABS_Beam_Forces_Consolidated.csv and ETABS_Beam_Forces_Manifest.json in a new or empty output directory.
- Both originals and extra source workbooks remain unchanged and **must not be committed publicly**.

## Engineering checks
1. Rows require source member unique ID and output station; identity includes story, combination and available step type/number.
2. Overlap duplicates are checked across every imported column; numeric differences are allowed only within 1e-6 absolute and 1e-9 relative tolerance. Conflicts fail rather than overwrite.
3. The importer checks the case and column schema across source parts, and refuses missing or linked input files.
4. A successful source import does **not** prove ETABS table coverage where other station rows were never exported, source-model hash identity, original output-axis compatibility, rigid offsets or OpenSees joint reactions.
5. No model geometry, gravity load, stiffness, mesh, original file or solver response is modified.

## Validation
Run python -m unittest tests.test_etabs_split_beam_forces. Tests cover deduplication, conflicts, case mismatch, immutable source/output behavior. Native comparison still requires corresponding OpenSees beam forces mapped through the source frame unique-ID/segment connectivity, local axes, output stations and end-offset treatment.

Related root-cause review: REVIEW_MAIN/01_GRAVITY/20261116_CONSOLIDATED_ROOT_CAUSE_AND_BEAM_FORCE_AUDIT.md.