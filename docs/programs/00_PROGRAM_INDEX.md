# 00 — Program index and execution map

This numbered catalog documents the existing V167 launchers **without renaming or moving any executable**. Numeric identifiers sort workflows; they do **not** mean every program must run in sequence. The current building NLTHA first-step transient failure remains unresolved.

| ID | Entry point | Individual guide |
|---|---|---|
| 01 | [`01_START_ETABS_TO_OPENSEES.py`](../../01_START_ETABS_TO_OPENSEES.py) | [01 guide](01_START_ETABS_TO_OPENSEES.md) |
| 02 | [`02_MODEL_INPUTS_AND_READINESS.py`](../../02_MODEL_INPUTS_AND_READINESS.py) | [02 guide](02_MODEL_INPUTS_AND_READINESS.md) |
| 03 | [`03_GRAVITY.py`](../../03_GRAVITY.py) | [03 guide](03_GRAVITY.md) |
| 04 | [`04_MODAL_ULS_SLS.py`](../../04_MODAL_ULS_SLS.py) | [04 guide](04_MODAL_ULS_SLS.md) |
| 05 | [`05_EQUIVALENT_STATIC.py`](../../05_EQUIVALENT_STATIC.py) | [05 guide](05_EQUIVALENT_STATIC.md) |
| 06 | [`06_RESPONSE_SPECTRUM.py`](../../06_RESPONSE_SPECTRUM.py) | [06 guide](06_RESPONSE_SPECTRUM.md) |
| 07 | [`07_LINEAR_TIME_HISTORY.py`](../../07_LINEAR_TIME_HISTORY.py) | [07 guide](07_LINEAR_TIME_HISTORY.md) |
| 08 | [`08_BUILDING_NONLINEAR_TRIAL.py`](../../08_BUILDING_NONLINEAR_TRIAL.py) | [08 guide](08_BUILDING_NONLINEAR_TRIAL.md) |
| 09 | [`09_NONLINEAR_REVIEWED_MODEL.py`](../../09_NONLINEAR_REVIEWED_MODEL.py) | [09 guide](09_NONLINEAR_REVIEWED_MODEL.md) |
| 10 | [`10_WALL_VALIDATION.py`](../../10_WALL_VALIDATION.py) | [10 guide](10_WALL_VALIDATION.md) |
| 11 | [`11_MATERIAL_DEVICE_VALIDATION.py`](../../11_MATERIAL_DEVICE_VALIDATION.py) | [11 guide](11_MATERIAL_DEVICE_VALIDATION.md) |
| 12 | [`12_NONLINEAR_PERFORMANCE.py`](../../12_NONLINEAR_PERFORMANCE.py) | [12 guide](12_NONLINEAR_PERFORMANCE.md) |
| 13 | [`13_STEEL02_CALIBRATION.py`](../../13_STEEL02_CALIBRATION.py) | [13 guide](13_STEEL02_CALIBRATION.md) |
| 14 | [`14_MATERIAL_PARAMETER_SETUP.py`](../../14_MATERIAL_PARAMETER_SETUP.py) | [14 guide](14_MATERIAL_PARAMETER_SETUP.md) |
| 15 | [`15_LITERATURE_MATERIAL_PROFILES.py`](../../15_LITERATURE_MATERIAL_PROFILES.py) | [15 guide](15_LITERATURE_MATERIAL_PROFILES.md) |
| 16 | [`16_COMPONENT_RESULTS.py`](../../16_COMPONENT_RESULTS.py) | [16 guide](16_COMPONENT_RESULTS.md) |
| 17 | [`17_LITERATURE_COMPONENT_DEMO.py`](../../17_LITERATURE_COMPONENT_DEMO.py) | [17 guide](17_LITERATURE_COMPONENT_DEMO.md) |
| 18 | [`18_BUILDING_FULL_NONLINEAR.py`](../../18_BUILDING_FULL_NONLINEAR.py) | [18 guide](18_BUILDING_FULL_NONLINEAR.md) |
| 20 | [`20_AUDIT_LOAD_CONNECTIONS.py`](../../20_AUDIT_LOAD_CONNECTIONS.py) | [20 guide](20_AUDIT_LOAD_CONNECTIONS.md) |
| 21 | [`21_TRACE_FAILED_ELEMENT.py`](../../21_TRACE_FAILED_ELEMENT.py) | [21 guide](21_TRACE_FAILED_ELEMENT.md) |

**Reserved:** 19 is deliberately vacant; do not create a fake launcher. 00 is reserved for navigation, conventions and release handoff.

## Run progression
Export reconciliation -> gravity -> modal -> equivalent static -> response spectrum -> linear histories -> isolated material, device and wall benchmarks -> short nonlinear diagnostics -> complete nonlinear records -> postprocessing and model-to-model comparisons. Skip progression when a verification gate fails.

## Important compatibility files
`RUN_ETABS_TO_OPENSEES.py` backs launcher 01; `RUN_LITERATURE_DEMO.py` backs launcher 17. The `OpenSees_*_V###.py` files and `components/` modules may be dynamically imported. Their names and paths remain unchanged until imports, relative paths, and regression runs have been audited.

[Organization policy](../00_REPOSITORY_ORGANIZATION.md) · [Existing run order](../../00_READ_FIRST_RUN_ORDER.md) · [V167 baseline](../../START_HERE_V167.md)
