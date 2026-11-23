# site_spectrum_and_scaling.py — source documentation

**Python source:** [components/response_spectrum/site_spectrum_and_scaling.py](../../../../components/response_spectrum/site_spectrum_and_scaling.py)
**Git baseline content SHA:** bcdbcf14c5dc7e6a7c8c6164df105f92c32e9724
**Subsystem:** Modal response spectrum and NBC scaling
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the response_spectrum implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-23 — selected-source NBC adopted period synchronization

The standalone site-spectrum GUI previously called generic populate_site without an export folder, so it could load a legacy default or leave NBC-adopted T1 X/Y blank even when MRSM had the right source-matched values.

launch_spectrum_gui(parent, folder) now accepts the active export folder. The main ETABS→OpenSees workflow passes its current selected export, and the site-spectrum tool provides a source path, Browse, and Refresh periods. A standalone launch does not import a guessed default folder. populate_site() calls the same mrsm_period_defaults() used by Model MRSM.

Period semantics remain distinct:
- T1_X/T1_Y: NBC §5.1.3 adopted design periods; min(Rayleigh, 1.25 × empirical) or explicitly attributed source/state-matched workbook references (research comparison only when fresh Rayleigh evidence is unavailable).
- Tn_X/Tn_Y: periods of first modes reaching 90% directional cumulative modal mass, drawn only from a model-SHA/state-matching saved modal result.
- No eigenperiod is substituted for adopted T1. Missing evidence leaves fields blank with diagnostic explanation; neither a successful modal run nor a ZIP proves ETABS physical equivalence.

No building solver is run by this UI. Regression: tests/test_site_spectrum_period_autofill_20261123.py.
