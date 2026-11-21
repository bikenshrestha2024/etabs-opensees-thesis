# 2026-11-21 semantic attestation source identity reconciliation

**Scope:** Resolve only the four stale attestations present on `main` before the NBC clause routing change. The source-level register is **not** a comprehensive code review or native structural-engineering certificate.

Procedure: fetched exact Git blob content by historical blob SHA and the current file content from the feature branch; extracted each top-level attested function between `def NAME` and the next top-level definition/decorator; compared the entire function body exactly. No private data touched.

| Source symbol | Previous blob | Current blob | Exact function comparison | Ledger disposition |
|---|---|---|---|---|
| `components/gravity/load_path_formulas.py::export` | `47dd7296e6b71bf32b1bac9f3032015a402308e3` | `ab82c51fb752c80d50a540842da93c11e6e92743` | identical (51 extracted lines) | Retain existing source-level review with current file blob |
| `components/inputs/project_workbooks.py::read_explicit_excel_calculation` | `c247664a6b7c4aa02e9aed7ea4bbca5f58ffc297` | `d0879ac0973b33b92149be7a5cb72626241a752c` | identical (85 extracted lines) | Retain existing source-level review with current file blob |
| `components/nonlinear_time_history/soil_c_run_matrix.py::create_configs` | `e4b08f59d747c8d491f5fbcddc9b80aec759cf2d` | `c9f95ca6392bc821399d993b14b05464ba80bb6f` | **changed** `path_factor_for_g_input_m_s2` from numeric literal `9.80665` to `GRAVITY_M_S2` | Withdraw earlier attestation; require a new source and units review |
| `components/gravity/gui_and_reports.py::_runner_source` | `d91b42658817be3c951cccbbb19f0e2f6d727e54` | `63a238b61b091b2a8493a1c31dede5e34a92452a` | **changed** extra `stiffness_basis` and `model_config_sha256` source metadata propagation before reactions | Withdraw earlier attestation; require a new full runner-path review |

The underlying earlier review documents and tests remain in the repository. This change only fixes **stale review status**. It neither claims changes in the two withdrawn functions are good or bad nor addresses the P0 support-reaction discrepancy, nonlinear wall initial step, missing-mass correction or 224 cases.

**Verification required:** mandatory `tools/audit_repository_integrated.py --fail-on-static-blockers` check and `tests/verify_ref_tags.py` on exact branch head. Even when stale-attestation errors clear, legacy output naming and static import cycles may remain open, and native physics gates must remain open.
