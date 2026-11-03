# 00 — Numbered program index

All **20 root program launchers** have work-order names. Material/component validation precedes nonlinear building work. The program numbers are navigational and do not certify structural validity.

| Step | Launcher | Guide | Function |
|---|---|---|---|
| 01 | [`01_WORKFLOW_START.py`](../../01_WORKFLOW_START.py) | [Guide](01_WORKFLOW_START.md) | Main ETABS-to-OpenSees GUI |
| 02 | [`02_INPUT_READINESS.py`](../../02_INPUT_READINESS.py) | [Guide](02_INPUT_READINESS.md) | Input and export reconciliation |
| 03 | [`03_MATERIAL_PARAMETER_SETUP.py`](../../03_MATERIAL_PARAMETER_SETUP.py) | [Guide](03_MATERIAL_PARAMETER_SETUP.md) | Material parameter configuration |
| 04 | [`04_LITERATURE_MATERIAL_PROFILES.py`](../../04_LITERATURE_MATERIAL_PROFILES.py) | [Guide](04_LITERATURE_MATERIAL_PROFILES.md) | Published specimen parameters |
| 05 | [`05_STEEL02_CALIBRATION.py`](../../05_STEEL02_CALIBRATION.py) | [Guide](05_STEEL02_CALIBRATION.md) | Steel02 experimental calibration |
| 06 | [`06_MATERIAL_DEVICE_VALIDATION.py`](../../06_MATERIAL_DEVICE_VALIDATION.py) | [Guide](06_MATERIAL_DEVICE_VALIDATION.md) | Materials, FVD and BRB benchmark tests |
| 07 | [`07_WALL_VALIDATION.py`](../../07_WALL_VALIDATION.py) | [Guide](07_WALL_VALIDATION.md) | Shear wall numerical and experimental checks |
| 08 | [`08_COMPONENT_RESULTS.py`](../../08_COMPONENT_RESULTS.py) | [Guide](08_COMPONENT_RESULTS.md) | Component result inspection |
| 09 | [`09_LITERATURE_COMPONENT_DEMO.py`](../../09_LITERATURE_COMPONENT_DEMO.py) | [Guide](09_LITERATURE_COMPONENT_DEMO.md) | Literature component demonstrations |
| 10 | [`10_GRAVITY.py`](../../10_GRAVITY.py) | [Guide](10_GRAVITY.md) | Gravity equilibrium and reactions |
| 11 | [`11_MODAL_ULS_SLS.py`](../../11_MODAL_ULS_SLS.py) | [Guide](11_MODAL_ULS_SLS.md) | Modal ULS and SLS analysis |
| 12 | [`12_EQUIVALENT_STATIC.py`](../../12_EQUIVALENT_STATIC.py) | [Guide](12_EQUIVALENT_STATIC.md) | NBC 105 equivalent static forces |
| 13 | [`13_RESPONSE_SPECTRUM.py`](../../13_RESPONSE_SPECTRUM.py) | [Guide](13_RESPONSE_SPECTRUM.md) | MRSM response spectrum analysis |
| 14 | [`14_LINEAR_TIME_HISTORY.py`](../../14_LINEAR_TIME_HISTORY.py) | [Guide](14_LINEAR_TIME_HISTORY.md) | Linear ground-motion analysis |
| 15 | [`15_BUILDING_NONLINEAR_TRIAL.py`](../../15_BUILDING_NONLINEAR_TRIAL.py) | [Guide](15_BUILDING_NONLINEAR_TRIAL.md) | Short nonlinear diagnostic trial |
| 16 | [`16_NONLINEAR_REVIEWED_MODEL.py`](../../16_NONLINEAR_REVIEWED_MODEL.py) | [Guide](16_NONLINEAR_REVIEWED_MODEL.md) | Reviewed nonlinear building model |
| 17 | [`17_BUILDING_FULL_NONLINEAR.py`](../../17_BUILDING_FULL_NONLINEAR.py) | [Guide](17_BUILDING_FULL_NONLINEAR.md) | Full nonlinear history (unresolved first-step failure) |
| 18 | [`18_NONLINEAR_PERFORMANCE.py`](../../18_NONLINEAR_PERFORMANCE.py) | [Guide](18_NONLINEAR_PERFORMANCE.md) | Performance criteria and results |
| 19 | [`19_AUDIT_LOAD_CONNECTIONS.py`](../../19_AUDIT_LOAD_CONNECTIONS.py) | [Guide](19_AUDIT_LOAD_CONNECTIONS.md) | Load-path and connectivity audit |
| 20 | [`20_TRACE_FAILED_ELEMENT.py`](../../20_TRACE_FAILED_ELEMENT.py) | [Guide](20_TRACE_FAILED_ELEMENT.md) | Trace failed solver element |

Legacy filenames remain functional as launch aliases. Underlying components, external records and saved outputs have not been renamed. The nonlinear transient failure is still an open issue.

[File migration map](../00_WORK_ORDER_RENAME_MAP.md) · [Organization policy](../00_REPOSITORY_ORGANIZATION.md)
