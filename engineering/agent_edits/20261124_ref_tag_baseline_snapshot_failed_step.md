# 2026-11-24 — ref-tag baseline shrink for `snapshot_failed_step`

- Editor: Claude Code (claude.ai session), model Claude Sonnet 5.5 (self-reported, not forensic proof)
- Base/head SHA: d672d1cb8246b4503f699dfaba8bb5a108343743, branch `main`
- Edited path: `tests/data/ref_tag_baseline.json` (one entry removed by `python tests/verify_ref_tags.py --write-baseline`)
- Reason: `components/nonlinear_time_history/failure_evidence.py::snapshot_failed_step` gained its `[REF ...]` tag in the latest commit, so `tests/verify_ref_tags.py::test_baseline_only_shrinks` failed until the baseline shrank.
- Tests executed (Linux container, Python 3.13, openseespy 3.8.0.0): `pytest tests` -> 1707 passed, 57 skipped (tkinter/comtypes/plotly missing), 2 failed before this edit; `verify_ref_tags.py` 4 passed after it. `verify_review_ledger.py::test_baseline_complete` still fails here only because the clone is shallow (`git ls-tree` on baseline SHA 66c5c97 is absent); not a code defect.
- Native smoke: literature RC portal NLTHA (El Centro, dt 0.0025 s) completed 12,465 steps, 0 fallbacks. This is NOT the 25-storey building and not ETABS equivalence.
- Scientific gates: SOURCE_CHECKED / NUMERICALLY_CONVERGED (portal only) / ETABS_OPENSEES_MATCHED / EXPERIMENT_VALIDATED / CODE_ACCEPTED all NOT_VERIFIED for the building. 32 supports + 44 mesh points, 1D+1L gravity and NBC Table 5-1 seismic weight untouched.
