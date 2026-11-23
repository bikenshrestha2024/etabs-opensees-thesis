# case_status.py — source documentation

**Python source:** [components/shared/case_status.py](../../../../components/shared/case_status.py)
**Git baseline content SHA:** c5721395c6663c6a0246fa43245b3e1cc40972ab
**Subsystem:** Solver, logging and response numerical utilities
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the shared implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: See subject-specific source citations. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


### Modal worker exit states

`modal_exit_status(cancelled, exit_code)` returns `CANCELLED` if the GUI stop flag was set, even when process termination yields a nonzero operating-system exit code; otherwise `FAILED` for nonzero or `COMPLETED` for zero. `CaseLedger.finish_pending` marks queued work `NOT COMPLETED`. Test `tests/verify_modal_cancel_status.py` is solver-free.


## 2026-11-14 V7 batch completion gate

`history_batch_exit_gate(ledger, exit_code, cancelled=False)` is the shared fail-closed LTHA/NLTHA GUI completion policy:

- **COMPLETED_SOLVER_ONLY** requires a zero child-process return code AND a structured `[OK] <case>:` entry for **every** requested record/orientation in `Time_History_Case_Status_V151.json`.
- **INCOMPLETE** is returned for missing/queued/in-progress/failed/truncated individual records even if Python exits 0.
- **FAILED** is returned for nonzero natural process exits; **INTERRUPTED** for deliberate operator cancellation.
- This only verifies structured solver-run accounting, **not full physical record duration, convergence at every accepted state, ETABS equivalence or NBC compliance**. Detailed output/time vectors, force transfer and end-of-record checks remain native evidence gates.
- Both linear and nonlinear GUI wrappers now use this gate for their summary log, `CASE_MANIFEST.json` solver status, and whether to auto-open/combine the saved results. Original solver source/motions and existing runs are unchanged.

CI regression: `tests/test_history_batch_completion_gate_v7.py`.


## 2026-11-23 — Optional source-provenance in shared CaseLedger

`CaseLedger(path, ids, provenance={...})` accepts an optional dictionary of
source/run identifiers, and `set_provenance(**fields)` atomically updates
the same current-run ledger. Existing LTHA/NLTHA callers without metadata
retain their original JSON format, log statuses and completion behavior.
The new MRSM caller records source model JSON SHA, stiffness state, selected
configuration digest and created unique run directory.

**A `COMPLETED` case row is a process/log status, not numeric or structural
equivalence evidence.** Consuming modules must independently reopen matching
numeric results and original source-identity records. Historical ledgers
without provenance remain readable but do not certify current-source cases.
Synthetic regression: `tests/test_mrsm_reopen_source_gate.py` plus
`tests/test_history_batch_completion_gate_v7.py`.
