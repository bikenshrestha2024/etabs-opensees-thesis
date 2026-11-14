# Post-V6 completeness audit: missed items and corrected history gate (2026-11-14)

**Scope:** targeted source inspection of current main following PR #59; not a full native Windows run or line-by-line proof of every module. Source files examined: `components/inputs/output_contract.py`, `tools/audit_stage_output_migration.py`, `components/inputs/output_layout.py`, `components/shared/case_status.py`, `components/linear_time_history/runner_and_gui.py`, `components/nonlinear_time_history/runner_and_gui.py`, `components/response_spectrum/model_analysis.py`, `components/response_spectrum/reports.py`, `components/equivalent_static/calculation_and_gui.py`, `components/validation/case_review.py`, `components/validation/saved_case_identity.py`, `components/modal/gui_and_reports.py`.

## Concrete source-level defect corrected in V7

Both LTHA and NLTHA workers previously set canonical run status `COMPLETED_SOLVER_ONLY` when the child returned code 0. However `components/shared/case_status.py` already maintained an authoritative individual case ledger with `COMPLETED`, `TRUNCATED`, `NOT COMPLETED` and in-progress states. The wrappers did not check this ledger before showing the batch success label or auto-opening outputs.

**V7 fix:** introduce `history_batch_exit_gate` and call it after each worker's `finish_pending`. A zero exit with even one incomplete or truncated record/orientation now yields `INCOMPLETE`. No record/orientation silently becomes completed. Cancellation and nonzero exits are represented separately. Only fully structured `[OK]`-complete suites are labelled `COMPLETED_SOLVER_ONLY`; that status still requires full duration/time-vector/native convergence checks.

## Remaining unclosed or only partially verified items

| ID | Priority | Finding | Next acceptance evidence |
|---|---|---|---|
| H-01 | P0 | Structured `[OK]` messages may not independently guarantee complete requested motion duration | Independently compare each saved accepted-time vector, start/end time, expected record dt/duration, missing states and truncation status |
| G-01 | P0 | 32/76/97 support-set reactions and wall–slab–beam gravity transfer still differ despite matching global total | Exact ETABS/native OpenSees restraint DOFs, reaction vectors and mesh-recovered forces |
| M-01 | P0 | MESH_04/08/16 convergence proof still lacks independently solved forces/reactions | Separate solver runs and mesh sensitivity/convergence criteria |
| S-01 | P0 | Conventional slab ULS/SLS 0.25/0.35 bending stiffness source decision does not itself prove correct generated OpenSees shell sections | Native ETABS/OpenSees section-command audit with physical load/mass preservation |
| E-01 | P1 | ESM complete canonical production writer+reader migration remains open; exit-0 evidence validation is now implemented | Case-by-case V111 scripts, source-matched workbook/ZIP and GUI navigation on Windows |
| R-01 | P1 | MRSM case completeness now checks six result files/identities, but native CQC/base shear/drift correctness is untested | Full ULS/SLS MRSM native runs with modal mass, force scaling and model SHA comparison |
| O-01 | P1 | Per-case manifests/Excel output audit validate metadata, **not** all nested ZIP members, absolute path references or live GUI selectors | End-to-end native Windows output reopening, ZIP audit, original source hashes |
| N-01 | P0 | Core-wall nonlinear constitutive calibration, brace hinges/outtrigger joint equivalence and FVD/BRB device testing remain open | Native verified nonlinear material/connection tests, zero-motion and full-record NLTHA acceptance |
| P-01 | P0 | Mandatory P-Delta preload states, mass basis and any initial seismic load transfer must be separately demonstrated | Both signed initial cases, nonlinear state transfer and no double-counting evidence |

## Required project governance

Never treat a passing Python unit test, an organized ZIP, an isolated shell convergence study or an ETABS/OpenSees globally matched force sum as sufficient structural validation. Do not upload local confidential EDB/Excel/ground motions. Continue to use the same canonical stage registry, immutable case manifests and local REVIEW folders for unresolved issues.

**Status:** V7 is a genuine software status-integrity fix. All other entries remain open, not falsely marked complete.
