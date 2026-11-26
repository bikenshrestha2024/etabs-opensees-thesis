# tools/nbc105_normative_extract.py

**Purpose.** Enumerate every normative unit of NBC 105:2025 (Clauses 1-10, Annexes A-C) into `docs/nbc105/normative_register/NORMATIVE_REGISTER.csv`, apply the human-authored `DISPOSITION_RULES.csv`, and check the register against the PDF.

**Source.** The user's NBC 105:2025 PDF (not in the repository). Printed page = PDF page - 21 up to PDF 47, PDF 48-49 are printed p.26 (Figure 4-3 map insert), PDF page - 23 from printed p.27.

**Units.** None (text processing). No ETABS or OpenSees involved.

**Commands.**
- `python tools/nbc105_normative_extract.py --pdf NBC105.pdf --extract` writes the register, `EXTRACTION_MANIFEST.json` and re-applies the rules.
- `--apply` re-applies `DISPOSITION_RULES.csv` to the stored register (no PDF needed).
- `--check [--pdf NBC105.pdf]` prints unreviewed rows, invalid dispositions and, with a PDF, hash drift (changed / missing / new). Exit code 1 on any finding.
- `--summary` regenerates `CLAUSE_SUMMARY.md`.

**Row kinds.** SHALL, SHOULD, MAY, LIMIT, STATEMENT (unclassified prose of 4+ words, kept visible), CLAUSE (numbered heading), TABLE, TABLE_ROW, TABLE_NOTE, FOOTNOTE, EQUATION, FIGURE, DEFINITION. A list item with no keyword inherits the lead-in's kind (`inherited_kind=Y`). Table C-1 is one hashed unit (753 data rows).

**No standard text is stored.** Each row has a 12-word locator, the SHA-256 of the whitespace-normalised unit, structure metadata and the review columns.

**Limits.** Heuristic parsing of `pdftotext -layout`: wrapped table cells can merge or split rows, equations are garbled glyph runs identified only by a label or position, figure-embedded text may appear as noise. Row hashes can change with another poppler version; `--check` then reports drift and a human must decide. The register is an enumeration aid, never a certification.

**Tests.** `tests/test_nbc105_normative_extract.py` (synthetic text, deterministic).
