# Real semantic inspection continuation — current review pass

Supplement to [the frozen baseline review ledger](ledger/README.md). This is **not** an automated blanket review of all active files.

| Path | Source actually examined | Important finding |
|---|---|---|
| `components/nonlinear_time_history/failure_evidence.py` | Whole source; `_numbers`, `snapshot_failed_step` | Post-failure node/element queries and source AREA tag map are diagnostic only; no native first causal step established |
| `components/nonlinear_time_history/thesis_quality.py` | Lines 100–175, `generate_isolation_configs` and `review_isolation_runs` | Four 0.005s research probes; not completed records; new separate-process runner wraps existing workflow |
| `components/nonlinear_time_history/soil_c_nltha_suite.py` | Register/source preflight, Loma special handling, first ~80 and last ~75 lines | Input fingerprints/motion policy screens are not independently verified SeismoMatch scaling logs or geotechnical classification |
| `components/nonlinear_time_history/variant_comparison.py` | Source manifest/aggregation and ending (~1–60, 105–184) | Numerical research comparison is not a source-validated optimum or completed native case |
| `components/nonlinear_time_history/soil_c_run_matrix.py` | Configuration creation and outputs, lines 40–167 | Generates 112 configurations and 224 planned orientations, no earthquake solved |
| `29_NATIVE_DEVICE_BENCHMARK.py` | Isolated setup and recorder calls in first ~100 lines | FVD/BRB reference parameters are illustrative, not specimen-matched force/stroke/cyclic validation |
| `21_NLTHA_TRIAGE.py` | Complete launcher | Generates independent probe configs / reviews outcomes but does not itself run solver |
| `35_SOIL_C_NLTHA_PREFLIGHT.py` | Complete launcher | Read-only eight-pair input preflight, no nonlinear structural solver |

All these are additional inspected source portions; do not overwrite the historical baseline CSV without creating a new versioned review snapshot and exact source-hash ledger.
