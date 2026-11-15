# 2026-11-15 agent change record — modal count semantics

- Editor: ChatGPT / GPT-6; connected GitHub source and CI artifacts.
- Current branch baseline: `d37685aaf0f2e74e4e4113436260805ba9fb1670`.
- Source actually inspected: `components/shared/eigen_solver.py` (all `solve_eigen`, sparse eigen setup), `components/modal/analysis.py` (period estimate and modal run input contract), `components/response_spectrum/model_analysis.py` (MRSM preflight and modal caller), `tests/verify_modal_solver_and_paths.py` and relevant source-guide/governance files.
- Change classification: EXTEND existing shared helper, no separate physics solver.
- Preserved: all source EDB/XLSX, global model kN-m-s, gravity profile, NBC adopted parameters, geometry, eigen equations, solver/fallback, all old report paths.
- CI gate: `tests.test_modal_mode_count_contract` + integrated inventory; native ETABS/OpenSees remains NOT_VERIFIED.
- Note: 535-file AST scanning and risk queue is broad static discovery; detailed manual semantic review of every function remains INCOMPLETE.
