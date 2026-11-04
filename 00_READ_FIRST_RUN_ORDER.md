**First Windows test after merge:** [safe setup, launchers, checks and error reporting](docs/00_TEST_MAIN_AFTER_MERGE.md). The first full nonlinear RCC core analysis remains explicitly research-only until native and material validation.

# 00 — OpenSeesPy work order

Primary launchers are now numbered from 01 through 20 in the following recommended verification-first order. They are **not** one compulsory sequential batch; use stand-alone diagnostics when needed. The previous filenames remain forwarding aliases.

01. [`01_WORKFLOW_START.py`](01_WORKFLOW_START.py) — Main ETABS-to-OpenSees GUI
02. [`02_INPUT_READINESS.py`](02_INPUT_READINESS.py) — Input and export reconciliation
03. [`03_MATERIAL_PARAMETER_SETUP.py`](03_MATERIAL_PARAMETER_SETUP.py) — Material parameter configuration
04. [`04_LITERATURE_MATERIAL_PROFILES.py`](04_LITERATURE_MATERIAL_PROFILES.py) — Published specimen parameters
05. [`05_STEEL02_CALIBRATION.py`](05_STEEL02_CALIBRATION.py) — Steel02 experimental calibration
06. [`06_MATERIAL_DEVICE_VALIDATION.py`](06_MATERIAL_DEVICE_VALIDATION.py) — Materials, FVD and BRB benchmark tests
07. [`07_WALL_VALIDATION.py`](07_WALL_VALIDATION.py) — Shear wall numerical and experimental checks
08. [`08_COMPONENT_RESULTS.py`](08_COMPONENT_RESULTS.py) — Component result inspection
09. [`09_LITERATURE_COMPONENT_DEMO.py`](09_LITERATURE_COMPONENT_DEMO.py) — Literature component demonstrations
10. [`10_GRAVITY.py`](10_GRAVITY.py) — Gravity equilibrium and reactions
11. [`11_MODAL_ULS_SLS.py`](11_MODAL_ULS_SLS.py) — Modal ULS and SLS analysis
12. [`12_EQUIVALENT_STATIC.py`](12_EQUIVALENT_STATIC.py) — NBC 105 equivalent static forces
13. [`13_RESPONSE_SPECTRUM.py`](13_RESPONSE_SPECTRUM.py) — MRSM response spectrum analysis
14. [`14_LINEAR_TIME_HISTORY.py`](14_LINEAR_TIME_HISTORY.py) — Linear ground-motion analysis
15. [`15_BUILDING_NONLINEAR_TRIAL.py`](15_BUILDING_NONLINEAR_TRIAL.py) — Short nonlinear diagnostic trial
16. [`16_NONLINEAR_REVIEWED_MODEL.py`](16_NONLINEAR_REVIEWED_MODEL.py) — Reviewed nonlinear building model
17. [`17_BUILDING_FULL_NONLINEAR.py`](17_BUILDING_FULL_NONLINEAR.py) — Full nonlinear history (unresolved first-step failure)
18. [`18_NONLINEAR_PERFORMANCE.py`](18_NONLINEAR_PERFORMANCE.py) — Performance criteria and results
19. [`19_AUDIT_LOAD_CONNECTIONS.py`](19_AUDIT_LOAD_CONNECTIONS.py) — Load-path and connectivity audit
20. [`20_TRACE_FAILED_ELEMENT.py`](20_TRACE_FAILED_ELEMENT.py) — Trace failed solver element

**Important:** Keep the package intact. No new numerical analysis was run by this renaming. The full-building nonlinear first-step transient failure remains unresolved.

[Full program guides](docs/programs/00_PROGRAM_INDEX.md) · [Old/new path map](docs/00_WORK_ORDER_RENAME_MAP.md)

21. [`21_NLTHA_TRIAGE.py`](21_NLTHA_TRIAGE.py) — generate/review isolated first-step failure probes (no solver execution).
