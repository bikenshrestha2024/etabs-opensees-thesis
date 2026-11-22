# material_draft.py — source documentation

**Python source:** [components/nonlinear_time_history/material_draft.py](../../../../components/nonlinear_time_history/material_draft.py)
**Git baseline content SHA:** 36e79406d917f92931ea5e347b9dc13a4a8d8a5f
**Subsystem:** Nonlinear transient model and research constitutive laws
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the nonlinear_time_history implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R03 R04 R05 R06. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 single-source correctness fix

Research draft generation now defaults to `PEER_2015_12_SINGLE_SOURCE`. For this basis it reads `peer_single_source()` from `material_source_sets.py` for the actual **PEER 2015/12 Appendix B.3** ConcreteCM/SteelMPF card. The printed Menegotto–Pinto transition `a1=18.5` and `R0=20` are converted to OpenSees-normalized `cR1=18.5/20=0.925`, while `cR2=0.0015` remains from that card. It no longer overwrites the single-paper values with an unrelated transition profile selected in the UI. Research file records full parameter table, separate 3D element source and explicit missing calibration/rebar/device inputs. This only resolves *source consistency*; it does not validate the 3D E-SFI element against the report's original 2D experiment.

Regression: `tests/verify_peer_material_draft_isolation.py` proves no source-file mutation, reference parameters and unapproved status; `tests/verify_one_storey_wall_probe.py` tests panel source geometry and provenance.


## 2026-11-22 — direct PEER Appendix B.3 literature-baseline policy

The user's thesis uses directly cited published constitutive inputs as a **research** baseline and reports source-specific parameter sensitivity; separate project material testing is **not** a prerequisite for attempting exploratory NLTHA. The PEER RW-A15-P10-S78 web FSAM reinforcement ratios are now directly adopted as `rho_x=rho_y=0.0074`, with published `nu=0.8` and dowel `alpha=0.01`. Its **distinct** boundary values (`rho_x=0.0082, rho_y=0.0587`) remain recorded, NOT applied to arbitrary wall panels without a verified region map. In the isolated PEER research draft, the former invented `20 mm @ 200 mm` bar proxy no longer controls these web values; mixed/nominal sensitivity bases remain labeled assumptions. See [the full page-specific source/units table and methodological distinction](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/docs/engineering/20261122_DIRECT_PEER_LITERATURE_NLTHA_PARAMETERS.md).

Source-level tests: `tests/test_peer_direct_literature_fsam_transfer_20261122.py`. This does not certify that the 25-storey X-wall first step converged, establish actual M0–M6 device input, or set `approved_for_nltha=true`.
