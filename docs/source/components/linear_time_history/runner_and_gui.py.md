# runner_and_gui.py — source documentation

**Python source:** [components/linear_time_history/runner_and_gui.py](../../../../components/linear_time_history/runner_and_gui.py)
**Git baseline content SHA:** 53ed247701837cbc823065a7c25d483617022541
**Subsystem:** Linear transient response
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the linear_time_history implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-22: clear input errors before numeric conversion

The GUI now runs a pure `parse_linear_gui_numeric_inputs` preflight **before constructing a run directory or calling `_read_inputs`**. It validates the current source's ULS/SLS against the user-selected state before parsing any number; the user screenshot selected SLS against a ULS source. Empty `Rayleigh period 1/2`, `T1 X/Y`, `Tn X/Y`, mode count or scale input is reported using the actual UI label instead of exposing `could not convert string to float: ''`. Validations reject NaN, infinities, nonpositive periods, damping above 5%, and identical Rayleigh calibration periods. A purely X-only diagnostic may leave Y T1/Tn blank; paired 3D cannot.

No source-unverified Rayleigh/modal periods are invented. For ULS exported EDB select **ULS**; for SLS select a real SLS export with its own source-matched modal and Rayleigh inputs. A syntactically valid configuration is not evidence that NBC §8.1.1 P-Delta initialization, motions and native stiffness/mass equivalence are accepted.
