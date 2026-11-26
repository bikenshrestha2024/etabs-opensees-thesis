# tools/nbc105_crossref_audit.py

**Purpose.** Find every cross-reference the NBC 105:2025 prints inside its own text (clause, section, Table, Figure, Equation, Annex) and keep a reviewed classification in `docs/nbc105/CROSS_REFERENCE_REGISTER.csv` (human-readable copy: `CROSS_REFERENCE_REGISTER.md`). Classes: `VALID`, `MISDIRECTED_CORRECT_TARGET_IS_X` (column `correct_target`), `AMBIGUOUS` (both targets named).

**Source.** The user's NBC 105:2025 PDF (not in the repository); the standard's text is not copied, only the matched phrase, a short locator and the SHA-256 of the printed line. Printed page numbers come from `tools/nbc105_normative_extract.py`.

**Units.** None (text processing). No ETABS or OpenSees involved.

**Commands.**
- `python tools/nbc105_crossref_audit.py --check` validates the CSV (every row classified, rationale present, MISDIRECTED has a corrected citation, targets exist in the normative register, the named code and docs files carry the corrected citation) and scans components, tools and docs for a drift limit sent to 5.6. No PDF needed.
- `--check --pdf NBC105.pdf` also re-extracts the references and fails on any printed reference that is not classified.
- `--extract --pdf NBC105.pdf [--merge]` lists unclassified references; `--merge` appends them as `UNCLASSIFIED` rows, which `--check` rejects until reviewed.
- `--markdown` regenerates the `.md` register.

**Findings (59 references).** MISDIRECTED: 2.4.2 "section 5.6" -> 5.5.1; 8.1.3.1 and 9.3.3.1 "clause 5.6" (drift limits) -> 5.5.3; 4.1.2 "Figure 4-1(b)" (MRSM curves) -> Figure 4-2; 4.1.4 "Figure 4-4" (zoning map) -> Figure 4-3. AMBIGUOUS: 9.2.5 "clause 4.1.2" (4.1.1 defines C(T), 4.1.2 only Ch(T)). The rest are VALID.

**Limits.** Equations are numbered inside image text, so equation targets are verified by hand, not against the register. References whose keyword is absent (a bare "(5.2)") are not detected. Does not decide engineering acceptance.

**Tests.** `tests/test_nbc105_followup_crossref_audit.py` (uses the PDF automatically when `NBC105_PDF` or the default upload path exists).

[Module documentation index](../00_SOURCE_GUIDE_INDEX.md)
