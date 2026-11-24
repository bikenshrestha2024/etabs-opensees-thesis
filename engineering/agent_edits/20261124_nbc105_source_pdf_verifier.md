# 2026-11-24 — NBC 105:2025 printed-source verifier

- Editor: Claude Code (claude.ai session), model Claude Sonnet 5.5 (self-reported, not forensic proof)
- Base SHA: 74c18a6 on `main`
- Added: `tools/verify_nbc105_source_pdf.py`, `tests/test_verify_nbc105_source_pdf.py`, `docs/source/tools/verify_nbc105_source_pdf.py.md`. No clause module, solver or physics code changed.
- Source checked: user-uploaded NBC 105:2025 PDF, 138 pages, SHA-256 9136fd6ca119f3536a4843c02516e791b1098e0275fa4c853c495c684c21ea1e (PDF not committed). 48 printed table/limit items all MATCH the code. Clauses 8 and 9 text was also read in full and matches `clause_08`/`clause_09` behaviour; §5.5.3 drift and §5.6 accidental eccentricity numbering matches the repo (the printed 8.1.3.1/9.3.3.1 reference to "5.6" for drift is the standard's own cross-reference error).
- Tests executed (Linux, Python 3.13, openseespy 3.8.0.0): `pytest tests` -> 1711 passed, 57 skipped (tkinter/comtypes/plotly absent), 1 failed: `verify_review_ledger::test_baseline_complete`, caused by the shallow clone lacking baseline SHA 66c5c97, not by this change.
- Not done / NOT_VERIFIED: full-sentence clause review, equations, the 25-storey building NLTHA (needs the private ETABS export on Windows), ETABS_OPENSEES_MATCHED, CODE_ACCEPTED. 32 supports + 44 mesh points, 1D+1L gravity and Table 5-1 seismic weight untouched.
