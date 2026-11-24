# 2026-11-24 — opt-in final relaxed tolerance + failure-report print safety

- Editor: Claude Code (claude.ai session), model Claude Sonnet 5.5 (self-reported, not forensic proof)
- Base SHA: 5b055f0 on `main`
- Edited: `components/nonlinear_time_history/runner_and_gui.py` (retry loop), `components/nonlinear_time_history/building_exploratory.py` (`_safe_print`, `validate_convergence_settings`, config wiring), `docs/source/components/nonlinear_time_history/building_exploratory.py.md`; added `tests/test_nltha_relaxed_final_tolerance_20261124.py`.
- Evidence read (user's run `EXPLORATORY_FRAME_NL_20261124_204907`, copy in a private folder, not committed): stall at t=2.38594 s after 488 accepted rows; return code -3 for all four algorithms at depth 5; failed-test norms 1.08e-7 to 2.4e-4 vs 1e-7; no non-finite values; peak drift 0.16 %; INCOMPLETE.json recorded OSError 22 from print() instead of the RuntimeError.
- Tests: new file 6 passed (fails before the change: 4 failed, 2 passed); with tkinter shim, 180 NLTHA-related tests passed; full suite 1711 passed, 1 failed (`verify_review_ledger`, shallow clone), 58 skipped (tkinter etc.).
- Native: real-model trial (0.02 s, 5 accepted steps, 0 failed attempts, gravity PASS 286419.76 kN, T1 2.0055 s) ran in a Linux container from a copy of the export. Default behaviour is unchanged; the relaxed tolerance is opt-in.
- Gates: SOURCE_CHECKED partial; NUMERICALLY_CONVERGED only for the 0.02 s trial; ETABS_OPENSEES_MATCHED / EXPERIMENT_VALIDATED / CODE_ACCEPTED NOT_VERIFIED. 32 supports + 44 mesh points, 1D+1L gravity benchmark and Table 5-1 seismic weight untouched; gravity profile in this run was AS_CONFIGURED (Live 0.3), flagged review-required by the code.
