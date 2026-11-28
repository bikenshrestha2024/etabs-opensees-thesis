# Beam-force shard audit, 2026-11-28

Editor: Anthropic Claude (Claude Code, Sonnet 5.5; self-reported, see commit trailer).

The three beam workbooks (`Beam_Forces_Element_1/2/3_latest.xlsx`) were supplied after the six-lot audit. Read-first contract reviewed; the existing beam reference reader was not changed. Added `components/validation/etabs_beam_force_shards.py`, `tools/audit_beam_force_shards.py`, tests, three source guides, a registry row, a README link and evidence under `docs/validation/`.

Actual workbook inspection: all three streamed with openpyxl read-only (2,574,846 data rows), each sheet cell scanned, then audited through the repository tool; the second-lot frame table was used for the beam-to-frame check. Raw rows and local paths are not committed.

Result: three Excel-row-limited shards of one table; union 750 elements, 2,388,500 unique rows, complete case/station grid; 186,346 boundary rows repeat with identical values; every beam is in the frame table on the same story. Not established: OpenSees equivalence, rigid-end offsets, beam time-history (envelopes only), NLTHA, NBC certification. No model, solver, gravity, g (9.81) or NBC ledger change.

Tests: `tests/test_etabs_beam_force_shards.py` 9 passed; full suite 2050 passed with the same two failures that also occur without these changes (`test_linear_th_directional_autofill`, `verify_review_ledger` baseline).
