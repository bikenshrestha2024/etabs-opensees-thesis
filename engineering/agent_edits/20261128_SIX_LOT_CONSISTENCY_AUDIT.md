# Six-lot ETABS consistency audit, 2026-11-28

Editor: Anthropic Claude (Claude Code, Sonnet 5.5, session recorded in commit trailer). Base/head SHA: see the commit. Branch: main (requested explicitly by the user).

Read-first triad and existing reader (`components/inputs/etabs_table_bundle.py`, support filter, assignment audit) reviewed; no existing method rewritten. Added `components/validation/etabs_lot_consistency.py`, `tools/audit_etabs_lot_consistency.py`, tests, three source guides, registry row, README link and the evidence files under `docs/validation/`.

Actual workbook inspection: all nine supplied workbooks streamed with openpyxl read-only (55 sheets, 173,117,043 cells); six distinct lots ingested through the repo reader; results in the evidence JSON. Raw workbooks, rows and local paths are not committed.

Not changed: model, solver, supports, gravity (1.0D+1.0L), NBC Table 5-1 ledger, `GRAVITY_M_S2` (9.81 vs export 9.80665 reported for a decision). Not verified: native ETABS/OpenSees equivalence, 768.045 kN residual, rigid end zones, NLTHA M0-M6, NBC certification. Beam workbooks 1/2/3 were not supplied.

Tests: `tests/test_etabs_lot_consistency.py` (21 passed), `tests/test_current_etabs_table_bundle.py`, `tests/test_documentation_coverage.py` (48 passed, 7 skipped before the evidence file existed); component README and documentation coverage gates clean.
