# NBC 105:2025 normative register guide

Date 2026-11-21. Status: NOT CERTIFIED. This register is a source-to-code review of the wording of the standard. It is not engineering acceptance of any building, and a unit-test pass is not code compliance.

## What it is

`docs/nbc105/normative_register/NORMATIVE_REGISTER.csv` has one row per normative unit of NBC 105:2025 (Clauses 1 to 10, Annexes A to C): sentences, list items, equations, tables and table rows, table notes, footnotes, figures and definitions. 1417 rows. Each row has an id (for example `N5-0123`), clause, subclause, printed page, kind, a 12-word locator, a SHA-256 of the whitespace-normalised unit, and the review columns. No standard text is stored.

Review columns: `disposition` (exactly one value below), `implementation_ref` (`path::symbol`), `test_ref` (`path::test_name`), `evidence_note` (what the code does and what the user must supply), `finding` (difference or ambiguity between code and print), `rule` (which line of `DISPOSITION_RULES.csv` set the row).

## Dispositions

| Value | Meaning |
|---|---|
| IMPLEMENTED_AND_TESTED | a code symbol implements the rule and a real unit test exercises it |
| IMPLEMENTED_UNTESTED | code exists, no direct unit test |
| MANUAL_PROJECT_CHECK | compliance depends on project evidence; the note names it |
| PROJECT_NOT_APPLICABLE | not applicable to the declared project; the note gives the reason |
| DEFINITION_ONLY | definition, symbol list, heading or explanation without its own requirement |
| EXTERNAL_DATA_REQUIRED | needs data not transcribed here (Figure 4-3 contours, Table C-1) |
| DEFERRED_DESIGN_PHASE | applies to the project but its design is deferred to a later phase by the owner (Annex B steel design after the nonlinear time-history analysis works); open work, never accepted |
| UNVERIFIED_GAP | not reviewed or not resolved; always visible and blocks the gate |

Project reasons used: 25-storey, about 95 m RC dual wall-frame with damped outriggers, Kathmandu (Kirtipur), no basement, no steel moment/braced frame as the primary system (the outrigger braces are steel members, so Annex B is DEFERRED_DESIGN_PHASE, see declarations section 6), no masonry, no base isolation (see [project declarations](PROJECT_DECLARATIONS.md); these are user declarations, not verified here).

## Workflow

1. `python tools/nbc105_normative_extract.py --pdf <NBC105.pdf> --extract` regenerates the register (deterministic) and the manifest.
2. Dispositions come from `DISPOSITION_RULES.csv` (selectors `id:`, `loc:<clause>|<locator prefix>`, `sub:`, `table:`, `kind:`; the most specific rule wins). `--apply` re-applies them.
3. `--check [--pdf ...]` lists unreviewed rows, invalid dispositions and hash drift. `--summary` writes `normative_register/CLAUSE_SUMMARY.md`.
4. `python -m components.nbc105 --audit` shows the gate (`components/nbc105/normative_register.py`).

## Gate

`BLOCKED_NOT_CERTIFIED` if any row is blank or UNVERIFIED_GAP, a disposition or reference is invalid, a reference does not resolve to a real file and symbol, the register is unreadable or its row count differs from the manifest. Otherwise `REGISTER_REVIEWED_EXTERNAL_GATES_OPEN`. `certified` is always false.

## Current counts (1417 rows)

| Disposition | Rows |
|---|---|
| DEFINITION_ONLY | 559 |
| IMPLEMENTED_AND_TESTED | 369 |
| MANUAL_PROJECT_CHECK | 293 |
| PROJECT_NOT_APPLICABLE | 24 |
| DEFERRED_DESIGN_PHASE | 156 |
| EXTERNAL_DATA_REQUIRED | 11 |
| IMPLEMENTED_UNTESTED | 5 |
| UNVERIFIED_GAP | 0 |
| blank | 0 |

Per clause counts: [CLAUSE_SUMMARY.md](normative_register/CLAUSE_SUMMARY.md).

## External gates (always open)

1. Independent human sign-off of this register and of the design.
2. Native ETABS and OpenSees evidence (modal, drift, torsion, Rayleigh, NLTHA convergence).
3. Project wall and connection designs: Annex A beams, columns, joints, wall shear (A.5.2), coupling beam diagonals (A.5.5.2(b)), construction joints, splices, and the connection and anchor details of Clause 10.4.

## Limits

Extraction is heuristic on `pdftotext -layout`; equations are garbled glyph runs identified by label. Equations of Annex A and B that are not coded were read from the text layer and, where noted, the page image; they have no code comparison. Row hashes can change with another poppler version (`--check` reports drift). Annex A figure numbers repeat Clause 4 figure numbers; rows are separated by clause code.
