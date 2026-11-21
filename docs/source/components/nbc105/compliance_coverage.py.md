# NBC 105:2025 source and engineering coverage auditor

**Source:** `components/nbc105/compliance_coverage.py`

**Authority:** Uploaded NBC 105:2025 Second Revision. Printed contents pp. xiv–xx, main Clauses 1–10 (printed pp. 1–52), and Annex A RC detailing (pp. 53–80), Annex B steel detailing (pp. 81–99), Annex C municipal zoning factors (p. 100 onward). The 137-page and 138-page uploaded PDFs have different physical PDF-page indices; **printed page and subclause identify the rule**.

**Purpose:** Source-index coverage, NOT full compliance. Earlier files contained detailed requirement matrices only for Clauses 1 and 4; short matrices for 2, 3 and 6–10 were insufficient to make an exhaustive claim. This module checks that each of the 235 identified section headings/table references is present in the versioned `docs/nbc105/source_coverage_register.json`, has a source page, canonical module owner, source-status provenance, and explicit evidence requirement. Annexes cannot falsely inherit a numeric clause module.

**Public API:** `read_source_index()`, `audit_source_index(rows)`, `source_index_path()`. Strict validation rejects duplicate/missing IDs, false module claims, missing test references, invalid printed pages, unsupported review states, and omission of any required annex/section.

**Current status:** `NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN`. Every row is explicitly `HEADING_INDEXED_REQUIREMENT_TEXT_NOT_EXHAUSTIVELY_VERIFIED`; this is a *heading-level audit skeleton* and not a line-by-line enumeration of every normative sentence, figure note, table footnote or detail. Neither unit tests nor manually typed approvals can authorize full building acceptance.

**Invocation:** `python -m components.nbc105 --audit`. Returns structured JSON and deliberately exits **2** while coverage and native engineering proof remain incomplete. No private model data uploaded.

**Test:** `tests/test_nbc105_full_source_coverage_gate.py`.
