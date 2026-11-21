# NBC 105:2025 clause package: index and clause register

Date 2026-11-21. Authority: NBC 105:2025 Seismic Design of Buildings in Nepal (DUDBC), user-supplied PDF. This index tracks which main clauses have a code module, a compliance matrix and tests. It is a software-conformance register, not design acceptance of any building. A unit-test pass is not engineering acceptance, and no native ETABS or OpenSees run is implied.

Related: [project declarations](PROJECT_DECLARATIONS.md), [wall grouping (Aw) method](WALL_GROUPING_AW_METHOD.md), [constants guide](../source/components/nbc105/constants.py.md).

## Naming convention

| Artifact | Path pattern |
|---|---|
| Clause module | `components/nbc105/clause_NN_<slug>.py` |
| Compliance matrix | `docs/nbc105/clause_NN_<slug>_matrix.md` |
| Tests | `tests/test_nbc105_clauseNN.py` (clause 4 is `tests/test_nbc105_clause04.py`; clause 5 predates the convention and uses `tests/test_nbc105_clause5.py`) |
| Module guide | `docs/source/components/nbc105/clause_NN_<slug>.py.md` |

`NN` is the two-digit main clause number. Shared constants live in `components/nbc105/constants.py`.

## Clause register (titles and printed pages from the PDF contents list, printed pp. xiv-xx)

Status: `CLAUSE_4` and `CLAUSE_5` mean module + matrix + tests. All others are `NOT_STARTED`.

| Clause | Title | Printed page | Status | Module | Matrix |
|---|---|---|---|---|---|
| 1 | Title, Scope, Definitions and Notations | 1 | NOT_STARTED | | |
| 2 | General Principles | 10 | NOT_STARTED | | |
| 3 | Scope of Analysis | 17 | NOT_STARTED | | |
| 4 | Seismic Hazard | 21 | CLAUSE_4 | [clause_04_seismic_hazard.py](../../components/nbc105/clause_04_seismic_hazard.py) | [matrix](clause_04_seismic_hazard_matrix.md) |
| 5 | Dynamic Characteristics of Structures | 28 | CLAUSE_5 | [clause_05_dynamic_characteristics.py](../../components/nbc105/clause_05_dynamic_characteristics.py) | [matrix](clause_05_dynamic_characteristics_matrix.md) |
| 6 | Equivalent Static Method | 38 | NOT_STARTED | | |
| 7 | Modal Response Spectrum Method | 40 | NOT_STARTED | | |
| 8 | Elastic Time History Analysis | 42 | NOT_STARTED | | |
| 9 | Non-linear Static and Dynamic Analysis | 44 | NOT_STARTED | | |
| 10 | Parts and Components | 49 | NOT_STARTED | | |
| Annex A | Design and Detailing of Reinforced Concrete Structures for Earthquake Loads | 53 | NOT_STARTED | | |
| Annex B | Design and Detailing of Steel Structures for Earthquake Loads | 81 | NOT_STARTED | | |
| Annex C | Seismic Zoning Factor for Cities/Municipalities | 100 | NOT_STARTED | | |

Sub-clause titles recorded where they matter to the two active clauses (contents list): 3.6 Load Combinations for Limit State Method (p. 19); 3.7 Load Combinations for Working Stress Method (p. 21); 3.8 Increase in Allowable Bearing Pressure (p. 21); 4.1 Elastic Site Spectra for Horizontal Loading (p. 21) with 4.1.1 to 4.1.5 (pp. 21, 22, 24, 26, 26); 4.2 Elastic Site Spectra for Serviceability Limit State (p. 27); 4.3 Elastic Site Spectra for Vertical Loading (p. 27); 5.1 Periods of Vibration (p. 28); 5.2 Seismic Weight (p. 30); 5.3 Selection of Structural System (p. 30). Existing code that already touches other clauses (for example the nonlinear time-history audit for clause 9.3) is not part of this register until it is audited line by line against the printed pages and given a matrix.

## Procedure to add a clause

1. Read the clause's printed pages in the PDF (see page offset below). Use the page images; do not transcribe from memory.
2. Transcribe the rules, equations, tables and footnotes into the clause matrix (`docs/nbc105/clause_NN_<slug>_matrix.md`), one row per requirement with the printed page. Note printed-page oddities (duplicated page numbers, wrong cross-references) instead of silently fixing them.
3. Write the module `components/nbc105/clause_NN_<slug>.py` with `[REF NBC105-2025 §x, printed p. N]` tags, an `__all__`, finite-input validation, and no extrapolation outside the printed range.
4. Write hand-computed tests in `tests/test_nbc105_clauseNN.py`: values worked by hand from the printed formulas, boundary cases at every table threshold, and rejected inputs.
5. Write parity tests against every existing implementation of the same rule in the repository (a mismatch is a finding; fix only what the printed text proves wrong, and list before/after numbers).
6. Fill in the matrix columns (code location, test id, status) and the open items.
7. Add the registry row to `CANONICAL_MODULES.csv`, the module guide under `docs/source/components/nbc105/`, the source-guide index entry, and update the register above.
8. Add a section to `engineering/agent_edits/20261121_nbc105_package_clause4.md` (or a new dated note for later work) with the actual edits, numeric changes, verification commands and model label (UNKNOWN if not available).
9. Run `python -m pytest -q` and `python tests/verify_ref_tags.py`.

## Page-offset method

Printed page N is PDF page N + 21 for the body up to printed p. 26 (printed p. 1 is PDF page 22; the contents list is on PDF pages 15-21, roman-numbered xiv to xx). From printed p. 27 on the offset is 23 (printed p. 27 is PDF 50, printed p. 29 is PDF 52). The offset for p. <= 26 is recorded as `PRINTED_PAGE_OFFSET = 21` in `components/nbc105/constants.py`. Verify the offset on every page you read by checking the number printed at the page foot, and record any page where it differs (the clause 4 audit found two tables printed on a page numbered 26, and the Figure 4-3 page numbered 25).
