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
