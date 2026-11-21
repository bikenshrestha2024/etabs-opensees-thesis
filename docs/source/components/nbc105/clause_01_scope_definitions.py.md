# clause_01_scope_definitions.py — source documentation

**Python source:** [components/nbc105/clause_01_scope_definitions.py](../../../../components/nbc105/clause_01_scope_definitions.py)
**Git baseline content SHA:** NEW (added 2026-11-21; not in the baseline)
**Subsystem:** NBC 105:2025 clause modules
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Pure-Python data and helpers for NBC 105:2025 clause 1 (printed pp. 1-9): the scope applicability of §1.2 (`SCOPE_MATERIALS`, `SPECIALIST_LITERATURE_SYSTEMS`, `SCOPE_HEIGHT_LIMIT_M` = None because no height limit is printed, `scope_check`); the printed notation list of §1.4 as 68 `Notation` rows (symbol, printed symbol, meaning as printed, unit, unit basis, printed page; `notation`, `notation_page_counts`, `printed_gravity_m_s2` = 9.81 from printed p. 7); and the numeric thresholds printed inside §1.3 definitions: dual system 25 percent (`dual_system_frame_share`, `dual_system_frame_share_ok`), soft story 70 and 80 percent (`is_soft_story`), flexible diaphragm 2 times (`is_flexible_diaphragm`), design basis earthquake 2/3 of MCE (`design_basis_earthquake_from_mce`), ductility factor, overstrength factor and eccentricity ratios, and the commonly taken 5 percent response-spectrum damping constant. Prose-only definitions are not coded; they are `DEFINITION_ONLY` rows of the [clause 1 matrix](../../../nbc105/clause_01_scope_definitions_matrix.md). `pdf_page_for_printed` maps printed pp. 1-9 to PDF pages 22-30. No production code calls the module yet; it is the audited reference and the parity guard for g (`constants.GRAVITY_M_S2`, `reconcile.G`) and for the soft-story check in `components/validation/response_checks.py`.

## Source, inputs, units
Transcribed 2026-11-21 from page images of the user-supplied PDF (PDF pages 22-30; the foot numbers 1 to 9 were checked). The printed notation has no unit column: only g (m/s^2) and H (m) print a unit; the other units are derived from §1.5 (kg, m, s, Pa, N) and flagged `SI_DERIVED`, loads whose unit cannot be fixed are `NOT_STATED`. Threshold helpers take any consistent unit (stiffness, deformation, shear) and use strict `<` / `>` where the text says "less than" / "more than" and `>=` for "at least". Printed-page notes: Wi is printed "Seismic weight at level I;"; Aw is "Area of Web" here but an effective wall area in §5.1.2 (matrix finding F2).

## Outputs and failure conditions
`scope_check` returns a dict with status `IN_SCOPE`, `SPECIALIST_LITERATURE` or `MATERIAL_NOT_LISTED` (not an exclusion, the clause lists covered materials only). `notation` raises KeyError for a symbol that is not printed (for example Ta). Non-finite, non-positive, boolean or wrong-length inputs, an empty material string, a non-bool system flag and a printed page outside 1..9 raise ValueError. Soft-story `three_above` must hold exactly three positive stiffnesses; without it only the 70 percent test is applied.

## Research and standards
NBC 105:2025 clause 1. See the [research reference register](../../../00_RESEARCH_REFERENCES.md).

## Regression acceptance
`python -m pytest tests/test_nbc105_clause01.py tests/test_nbc105_clause01_parity.py -q` (notation pinned page by page, scope, thresholds on both sides of each limit, rejections, parity) and `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees run. See [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)
