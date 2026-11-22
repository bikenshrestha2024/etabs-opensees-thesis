# gui_and_reports.py — source documentation

**Python source:** [components/modal/gui_and_reports.py](../../../../components/modal/gui_and_reports.py)
**Git baseline content SHA:** 7abb5e4d8b606507639b71149478bdf9fc5d8799
**Subsystem:** Modal analysis and numerical damping
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the modal implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## Modal GUI process cancellation (2026-11-04)

The shared `panel` already has a **Stop selected batch** control; avoid duplicating it. In the worker, after `proc.wait()`, check the saved cancellation flag **before** reading any generated modal JSON or interpreting a nonzero exit code. Label an operator cancellation `CANCELLED` and skip queued ULS/SLS states; clear the process pointer in `finally`. `components.shared.case_status.modal_exit_status` is tested by `tests/verify_modal_cancel_status.py`. This is UI lifecycle integrity, not an eigenvalue validation or proof that an external executable terminated without child processes.


## 2026-11-15 verified context contract source review

NBC 105 modal child runner source and original input workbook import previously derived helper/project root using Path(__file__).parent, dependent on direct-module vs root exec facade context. Source-aware root used for both. Mode selection, actual original workbook, Ritz/eigen etc remain unchanged; native ETABS/OpenSees equivalence not verified.

Scope of tests: synthetic direct-module import, exec-root facade, exported-runtime facade path consistency in `tests/test_facade_runtime_context.py`. No native ETABS/OpenSees, source workbook or full engineering model was executed in these path-only regressions.

## 2026-11-22 — modal Rayleigh periods are external GUI inputs

The modal dialog variables tr_x and tr_y are externally supplied reference periods that the GUI passes to nbc105_period_estimate. The eigenvalue/mass audit DOES NOT perform a new NBC §5.1.1 Wi-Fi-di Rayleigh analysis, nor does it independently verify the provenance of an entered period. The generated runner now records EXTERNAL_GUI_INPUT_NOT_COMPUTED_BY_MODAL_SOLVER, exports modal_model_basis_audit, and prints [MODAL MODEL BASIS] so the 76 source restraint IDs, 32 physical foundations, mesh transfer and active stiffness basis cannot be conflated.

The workbook NBC Summary now distinguishes source-based model restraint count, stiffness policy, Rayleigh input origin, successful numerical mass coverage, and native physical engineering acceptance. Source model is not modified. This fixes misleading reporting but does NOT repair the known original 768.045-kN pointwise ETABS-elastic reaction residual.

## 2026-11-22 — foundation and seismic-mass operator controls

Modal GUI now offers the shared `PHYSICAL_32`, `SOURCE_76`, `WALL_BASE_97` case selector and `SOURCE_DISTRIBUTED` vs optional `STORY_LUMPED_NBC` dynamic mass operator. Generated modal runner freezes settings to avoid reused GUI state changing a previous run, then validates model builder's returned actual support tags and `support_case_evidence` to detect an old copied runtime. These settings affect actual modal eigenphysics; historical periods, mass participation, Rayleigh external input and native ETABS validation remain separate.
