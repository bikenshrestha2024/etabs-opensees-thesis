# initial_pdelta.py — source documentation

**Python source:** [components/model/initial_pdelta.py](../../../../components/model/initial_pdelta.py)
**Git baseline content SHA:** f2c2200198bd3b10de8de487dcb97ace4ad51bd5
**Subsystem:** ETABS geometry/mass/constraint and model assembly
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the model implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R10 R12. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-23 — selected foundation case and signed-check cache safety

A source review found a substantive inconsistency: `ensure_initial_checks` built the selected foundation profile through `build_complete_model`, but `run_gravity_stage` and signed horizontal reaction sums still enumerated the **original 76 source restraint IDs**. For the user-confirmed primary `PHYSICAL_32` case, 44 original IDs are shear-wall mesh transfer joints, not additional physical foundations.

The implementation now calls `solver_reaction_support_tags(built, selected_case)` after every fresh-domain build. Those **actual assembled foundation support tags** are used for both gravity and signed horizontal reaction accounting. The result records selected support profile, actual tag count and an SHA-256 of the tag list. It does not modify node fixities, wall mesh edge constraints, source models or the adopted analysis equations; native MPC/source-equivalence remains `NOT_VERIFIED`.

The formerly shared SHA-256 key concatenated source and model bytes without source boundaries and did not fingerprint selected foundation case, seismic-mass policy or ULS/SLS initial-stiffness basis. `_initial_pdelta_fingerprint` now hashes each named input/source independently, then includes all three policy selectors. Old cached results are deliberately invalidated; a result is reused only when all four signed X/Y cases are converged and carry the current exact cache key and policy metadata. New result JSON is written atomically using `components.inputs.output_contract.atomic_json` after all four cases finish. Per-case `build_elapsed_s`, `gravity_elapsed_s` and `lateral_elapsed_s` are saved for the 12-case performance baseline.

**Initial combination selection:** Default initial signed reference stiffness is ULS, even if a subsequent ESM/modal run uses SLS. Set `OPENSEES_INITIAL_PDELTA_LIMIT_STATE` explicitly for a separately reviewed initial-state study; it never silently inherits `OPENSEES_LIMIT_STATE`.

**Important:** One selected export folder still contains a single shared `OpenSees_IS16700_Initial_PDelta_Results.json`. This cache contract is designed for the current sequential runner, **not** uncontrolled concurrent writers. No parallel ESM execution or restored OpenSees domain is enabled. Rebuild the exported `OpenSees_Runtime_V118` from the current repository before re-running; an old copied runtime cannot benefit from this change. Changing the source cache invalidates the old signed-check evidence and may cause one expensive cold run. Rerun and compare native ETABS 32-joint support cuts before asserting engineering acceptance.

Synthetic regression: `tests/test_initial_pdelta_profile_cache_20261123.py`. Native ETABS and source-matched Windows OpenSees are pending.
