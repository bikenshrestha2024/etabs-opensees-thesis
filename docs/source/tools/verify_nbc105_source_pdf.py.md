# tools/verify_nbc105_source_pdf.py — source guide

**What:** compares the numeric content of a user-supplied NBC 105:2025 PDF (or a `pdftotext -layout` text file) with the values `components/nbc105` actually returns: Table 3-1 (12 stiffness factors), Table 4-1 (16 spectrum parameters), Table 5-1 (3 live-load factors), Table 5-2 (21 system rows), Table 6-1 (7 deflection factors), and the limits in §5.1.3 (1.25), §5.5.3 (0.025 / 0.006), §8.1.1.5 (5 % damping), §9.3.2.2 (0.33–3 scaling) and §9.3.2.4 (dt rule). 48 items in all.

**When:** after any edit to a clause module constant, and whenever a different printing or edition of the standard is adopted.

**Why:** the repo's tests hold independent transcriptions, but nothing recorded which printed document they came from. This tool records the source SHA-256 and page count next to the result.

**How:** parses printed rows with regular expressions, reads the code through its public functions (not copies of the numbers), and reports `MATCH`, `MISMATCH` or `PARSE_MISS` per item. A table it cannot find is a failure, never a pass. Exit code 0 only when all items match.

**Where:** `tools/verify_nbc105_source_pdf.py`; test `tests/test_verify_nbc105_source_pdf.py` (fixture is numeric rows only). CLI: `python tools/verify_nbc105_source_pdf.py PDF --out report.json`.

**Which:** tables and numeric limits only. It does not read every sentence, does not check equations, and a full match is **not** code approval or structural acceptance. The PDF is never copied into the repository.

**Who:** software maintainer owns the tool; the thesis author owns any reading of the result.

**Observed 2026-11-24:** the 138-page printing with SHA-256 `9136fd6ca119f3536a4843c02516e791b1098e0275fa4c853c495c684c21ea1e` matched all 48 items. Older tests cite a "137-page source PDF"; the two printings are not shown to be identical.
