# Active output writer ownership audit

Source: `tools/audit_output_stage_ownership.py`, which uses the existing AST inventory in `tools/audit_live_output_writers.py`.

This script inspects every active Python file returned by the established source scanner and partitions possible output writes across gravity, ESM, modal, MRSM, linear and nonlinear time histories, validation, model and cross-cutting modules. It creates a **review queue** for sources that contain both write operations and legacy path literals, with filenames and line numbers.

```powershell
python tools/audit_output_stage_ownership.py --strict
python tools/audit_output_stage_ownership.py --report-dir audit/output-ownership
```

Run the report locally; do not commit reports containing private source locations. The CI contract rejects (1) missing stage-owner guards in gravity/LTHA/NLTHA GUI producers, (2) ESM producer calls that omit explicit stage routing, and (3) active Python parsing errors. Unreviewed legacy candidates are **reported**, not automatically judged defective: a legacy read for compatibility is legitimate, but a new legacy write is not.

**Explicit limitation:** AST enumeration is neither a complete dataflow/call graph nor a runtime producer/consumer verification. Writers passed a dynamic output path need native Windows trials; a lower legacy literal count is not an acceptance proof. New source adapters, ETABS COM scripts, time-history runners and saved evidence must be manually checked with source hashes and each stage's authoritative run directory. `--strict` does not pretend to certify all ~600 Python modules.

[REF `components/inputs/output_layout.py`; `components/inputs/output_contract.py`; `AGENTS.md` stage ownership requirements.]


## 2026-11-24 — AST-declared run-stage call inventory

The existing scanner now inventories direct calls to `create_case_run`, `owned_run_destination` and `analysis_output_folder` across **all active source files** returned by the shared `tools/audit_live_output_writers.source_files` enumerator (root entry scripts, `components/`, `src/`, `tools/`; archives/tests excluded by that scanner). Each `declared_run_stage_calls` entry contains source-relative file, AST line, API, owner module, declared literal stage or `null` for a dynamic expression, and a review-only status. `CROSS_OWNER_REVIEW` indicates a declared output stage different from the containing module's ordinary owner; `DYNAMIC_STAGE_REVIEW` indicates a stage expression the AST cannot evaluate; `LEGACY_DEFAULT_REVIEW` flags calls intentionally/defaulting to legacy results; `SHARED_OWNER_REVIEW` marks input/UI/tool modules without a single intrinsic analysis stage. `OWNER_MATCHED` means only that the **declared literal** matches the expected module owner.

The JSON also includes `cross_owner_run_stage_review` and `dynamic_run_stage_review`, and `--report-dir` writes `declared_run_stage_calls.csv` beside the existing JSON and legacy review CSV. No file moves, numeric case changes, GUI launch or native solver execution occur. The prior `--strict` semantics are preserved: known mandatory path guards and syntax errors are enforcement failures; cross-owner or dynamic declarations are **not** because the Gravity module can legitimately create an ETABS-export run and shared code can route to several modules.

**Limits:** This is not full dataflow. Calls via aliases, attribute dispatch, runtime indirection, callbacks or argument wrappers may evade direct AST classification; a literal stage match is not a verified writer or proof that readers use the same path. Further source-level caller/reader tracing and Windows tests remain required. CI includes the synthetic `test_static_run_stage_call_inventory_covers_all_modules_and_dynamic_stages` regression in `tests/test_crossmodule_output_stage_ownership.py`. Run the report to a local output directory; generated reports can include project-specific paths in later extensions and should not be committed.
