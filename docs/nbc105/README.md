# NBC 105:2025 clause package: index and clause register

Date 2026-11-21. Authority: NBC 105:2025 Seismic Design of Buildings in Nepal (DUDBC), user-supplied PDF. This index tracks which main clauses have a code module, a compliance matrix and tests. It is a software-conformance register, not design acceptance of any building. A unit-test pass is not engineering acceptance, and no native ETABS or OpenSees run is implied.

Related: [project declarations](PROJECT_DECLARATIONS.md) (g = 9.81 per printed p. 7, superseding the 9.80665 decision; Vs,30 optional with the clause 4.1.3 requirement documented), [wall grouping (Aw) method](WALL_GROUPING_AW_METHOD.md), [constants guide](../source/components/nbc105/constants.py.md).

[Independent 21 November review](INDEPENDENT_REVIEW_20261121.md) records the reviewed GitHub commit, reproduced integration gaps and Windows test results.

## Naming convention

| Artifact | Path pattern |
|---|---|
| Clause module | `components/nbc105/clause_NN_<slug>.py` |
| Compliance matrix | `docs/nbc105/clause_NN_<slug>_matrix.md` |
| Tests | `tests/test_nbc105_clauseNN.py` (clause 1 is `tests/test_nbc105_clause01.py`, clause 4 is `tests/test_nbc105_clause04.py`; clause 5 predates the convention and uses `tests/test_nbc105_clause5.py`) |
| Module guide | `docs/source/components/nbc105/clause_NN_<slug>.py.md` |

`NN` is the two-digit main clause number. Shared constants live in `components/nbc105/constants.py`.

## Clause register (titles and printed pages from the PDF contents list, printed pp. xiv-xx)

Status: the ten main clauses have dedicated modules, and identified ESM, MRSM, linear-history, NLTHA-preflight and drift calculation callers are routed to them. **This is not exhaustive clause-text compliance**, and the source matrices still contain legacy summary wording. Clause 5 now includes tested §§5.1–5.6 reference rules; physical-model validity remains open. Annex A and Annex B have new narrowly scoped pure reference helpers, while Annex C municipality-wide validation remains open. See the [235-heading source index and evidence gates](EXHAUSTIVE_REQUIREMENTS_ACCEPTANCE_REGISTER_20261121.md); it is not a sentence-by-sentence normative source audit.

| Clause | Title | Printed page | Status | Module | Matrix |
|---|---|---|---|---|---|
| 1 | Title, Scope, Definitions and Notations | 1 | CLAUSE_1 | [clause_01_scope_definitions.py](../../components/nbc105/clause_01_scope_definitions.py) | [matrix](clause_01_scope_definitions_matrix.md) |
| 2 | General Principles | 10 | REFERENCE_MODULE_CALLERS_OPEN | [clause_02_general_principles.py](../../components/nbc105/clause_02_general_principles.py) | [matrix](clause_02_general_principles_matrix.md) |
| 3 | Scope of Analysis | 17 | REFERENCE_MODULE_CALLERS_OPEN | [clause_03_scope_of_analysis.py](../../components/nbc105/clause_03_scope_of_analysis.py) | [matrix](clause_03_scope_of_analysis_matrix.md) |
| 4 | Seismic Hazard | 21 | CLAUSE_4 | [clause_04_seismic_hazard.py](../../components/nbc105/clause_04_seismic_hazard.py) | [matrix](clause_04_seismic_hazard_matrix.md) |
| 5 | Dynamic Characteristics of Structures | 28 | CLAUSE_5 | [clause_05_dynamic_characteristics.py](../../components/nbc105/clause_05_dynamic_characteristics.py) | [matrix](clause_05_dynamic_characteristics_matrix.md) |
| 6 | Equivalent Static Method | 38 | REFERENCE_MODULE_CALLERS_OPEN | [clause_06_equivalent_static.py](../../components/nbc105/clause_06_equivalent_static.py) | [matrix](clause_06_equivalent_static_matrix.md) |
| 7 | Modal Response Spectrum Method | 40 | REFERENCE_MODULE_CALLERS_OPEN | [clause_07_modal_response_spectrum.py](../../components/nbc105/clause_07_modal_response_spectrum.py) | [matrix](clause_07_modal_response_spectrum_matrix.md) |
| 8 | Elastic Time History Analysis | 42 | REFERENCE_MODULE_CALLERS_OPEN | [clause_08_elastic_time_history.py](../../components/nbc105/clause_08_elastic_time_history.py) | [matrix](clause_08_elastic_time_history_matrix.md) |
| 9 | Non-linear Static and Dynamic Analysis | 44 | REFERENCE_MODULE_CALLERS_OPEN | [clause_09_nonlinear_analysis.py](../../components/nbc105/clause_09_nonlinear_analysis.py) | [matrix](clause_09_nonlinear_analysis_matrix.md) |
| 10 | Parts and Components | 49 | REFERENCE_MODULE_CALLERS_OPEN | [clause_10_parts_and_components.py](../../components/nbc105/clause_10_parts_and_components.py) | [matrix](clause_10_parts_and_components_matrix.md) |
| Annex A | Design and Detailing of Reinforced Concrete Structures for Earthquake Loads | 53 | PARTIAL_REFERENCE_ONLY_FULL_DETAILING_OPEN | [annex_a_rc_detailing.py](../../components/nbc105/annex_a_rc_detailing.py) | [source index](source_coverage_register.json) |
| Annex B | Design and Detailing of Steel Structures for Earthquake Loads | 81 | PARTIAL_REFERENCE_ONLY_FULL_DETAILING_OPEN | [annex_b_steel_detailing.py](../../components/nbc105/annex_b_steel_detailing.py) | [source index](source_coverage_register.json) |
| Annex C | Seismic Zoning Factor for Cities/Municipalities | 100 | FULL_MUNICIPALITY_DATA_AUDIT_OPEN | | [source index](source_coverage_register.json) |

Sub-clause titles recorded where they matter to the two active clauses (contents list): 3.6 Load Combinations for Limit State Method (p. 19); 3.7 Load Combinations for Working Stress Method (p. 21); 3.8 Increase in Allowable Bearing Pressure (p. 21); 4.1 Elastic Site Spectra for Horizontal Loading (p. 21) with 4.1.1 to 4.1.5 (pp. 21, 22, 24, 26, 26); 4.2 Elastic Site Spectra for Serviceability Limit State (p. 27); 4.3 Elastic Site Spectra for Vertical Loading (p. 27); 5.1 Periods of Vibration (p. 28); 5.2 Seismic Weight (p. 30); 5.3 Selection of Structural System (p. 30). Existing code that already touches other clauses (for example the nonlinear time-history audit for clause 9.3) is not part of this register until it is audited line by line against the printed pages and given a matrix.

## November 2026 source-module checkpoint

Clauses 2, 3, 6–10 are source-grounded pure Python reference implementations with numerical and fail-closed checks, not finished solver/GUI refactoring. Clause 7 still lacks a full missing-mass solver and close-frequency grouping; Clause 9 still lacks validated nonlinear histories and wall convergence. Table 10-1 is implemented as 2.5 at equal periods, linearly reducing to 1.0 at a 0.5 s absolute difference; the printed equality at 0.5 s is unstated and the continuous limit was selected with an explicit engineering note. All original physical-model acceptance gates remain OPEN.

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

## Single rule owner and production caller integration

Each of the ten numbered main clauses is a **separate Python module** under `components/nbc105/clause_NN_*.py`. `dispatch.py` and `python -m components.nbc105` expose operations without duplicating rules. Use `python -m components.nbc105 --list` to enumerate allowed operations. The existing settings viewer now exposes a local **NBC clauses 1–10** calculator dialog. Any calculation returns a non-certification status.

**Migrated active call paths:** `components/equivalent_static/code_basis.py` delegates §3.2.1 method eligibility and §3.4 cracked stiffness to Clause 3 and §6 base shear, coefficient, storey force and `k` to Clause 6. `components/response_spectrum/model_analysis.py` delegates modal design coefficients and force-only scalar scaling to Clause 7. `components/linear_time_history/runner_and_gui.py` uses Clause 8 for response aggregation. `components/nonlinear_time_history/nbc105_2025_audit.py` delegates pair scaling/period window/time-step to Clause 9 and record count rule to Clause 8. `components/validation/response_checks.py` delegates design drift limits to Clause 5. All remaining complex case integrations and native engineering evidence are separate acceptance gates.

The local evidence checker `python -m components.nbc105.acceptance /path/to/V107_ACCEPTANCE.json` independently recomputes the X/Y RS shear matching and reports **full acceptance blocked** for absent Rayleigh, mass, drift, support, soil and nonlinear evidence. It neither uploads private ETABS data nor accepts a user-provided `PASS` label.

## Exhaustive compliance audit — latest evidence gates

Run `python -m components.nbc105 --audit` to obtain the 235 indexed printed section headings and hard-stop source/production/native evidence gates; the command deliberately exits 2 because indexing a heading does not prove every normative sentence or detailing rule. The same mandatory source and Annex A/B/C gates are reported by `python -m components.nbc105.acceptance <local acceptance JSON>`. The current native model, support reactions, full Rayleigh COM displacements and completed nonlinear histories are not independently validated. The [acceptance register](EXHAUSTIVE_REQUIREMENTS_ACCEPTANCE_REGISTER_20261121.md) defines the missing evidence and limited source-reference scope.

## 2026-11-22 — Usable input contracts for every exposed clause operation

The settings dialog now obtains a **named JSON input template** from the
actual exported Python signature for every Clause 1–10 and Annex A/B rule.
For example, Clause 5 `accidental_eccentricities_m` displays:

```json
{"building_width_m": null}
```

Enter a verified building width in **metres**; the reference function
calculates the signed ±5% eccentricities (it does not modify ETABS). An
empty `{}` is not an adequate input to this function. The dispatcher now
reports the missing/extra argument name rather than the generic
"input signature mismatch" error. Switching operations refreshes the
correct template and retains per-operation edits during the current dialog.

CLI argument contract:

```powershell
python -m components.nbc105 --list
python -m components.nbc105 --describe --clause 5 --operation accidental_eccentricities_m
python -m components.nbc105 --clause 5 --operation accidental_eccentricities_m --json "{\\"building_width_m\\":24.0}"
python -m components.nbc105 --audit
```

The dialog's **Source coverage (open gates)** button presents every indexed
Clause 1–10 and Annex A/B/C heading and its printed page, source-review
status and acceptance state. This is a heading-level inventory; the
full-text normative review, local site/hazard inputs, numerical parity,
member detailing and native building design checks remain separate.

**Not implemented/certified as a comprehensive NBC digital rules engine:**
the exhaustive normative sentence/figure/table/footnote mapping, all
Annex C local zoning rows, every production integration and signed native
structural acceptance. These omissions must continue to fail closed.
Regression tests are under
`tests/test_nbc105_operation_input_contracts.py`; CI workflow runs them,
but an unobserved CI run is not reported as passing.
