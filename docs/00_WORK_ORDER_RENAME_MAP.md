# 00 — Work-order rename map

| Original root executable filename | New preferred filename |
|---|---|
| `01_START_ETABS_TO_OPENSEES.py` | `01_WORKFLOW_START.py` |
| `02_MODEL_INPUTS_AND_READINESS.py` | `02_INPUT_READINESS.py` |
| `14_MATERIAL_PARAMETER_SETUP.py` | `03_MATERIAL_PARAMETER_SETUP.py` |
| `15_LITERATURE_MATERIAL_PROFILES.py` | `04_LITERATURE_MATERIAL_PROFILES.py` |
| `13_STEEL02_CALIBRATION.py` | `05_STEEL02_CALIBRATION.py` |
| `11_MATERIAL_DEVICE_VALIDATION.py` | `06_MATERIAL_DEVICE_VALIDATION.py` |
| `10_WALL_VALIDATION.py` | `07_WALL_VALIDATION.py` |
| `16_COMPONENT_RESULTS.py` | `08_COMPONENT_RESULTS.py` |
| `17_LITERATURE_COMPONENT_DEMO.py` | `09_LITERATURE_COMPONENT_DEMO.py` |
| `03_GRAVITY.py` | `10_GRAVITY.py` |
| `04_MODAL_ULS_SLS.py` | `11_MODAL_ULS_SLS.py` |
| `05_EQUIVALENT_STATIC.py` | `12_EQUIVALENT_STATIC.py` |
| `06_RESPONSE_SPECTRUM.py` | `13_RESPONSE_SPECTRUM.py` |
| `07_LINEAR_TIME_HISTORY.py` | `14_LINEAR_TIME_HISTORY.py` |
| `08_BUILDING_NONLINEAR_TRIAL.py` | `15_BUILDING_NONLINEAR_TRIAL.py` |
| `09_NONLINEAR_REVIEWED_MODEL.py` | `16_NONLINEAR_REVIEWED_MODEL.py` |
| `18_BUILDING_FULL_NONLINEAR.py` | `17_BUILDING_FULL_NONLINEAR.py` |
| `12_NONLINEAR_PERFORMANCE.py` | `18_NONLINEAR_PERFORMANCE.py` |
| `20_AUDIT_LOAD_CONNECTIONS.py` | `19_AUDIT_LOAD_CONNECTIONS.py` |
| `21_TRACE_FAILED_ELEMENT.py` | `20_TRACE_FAILED_ELEMENT.py` |

Each new file uses the original file's Git blob unchanged; previous paths now contain a forwarding launcher. Preserved pre-change branch: [backup/pre-workorder-rename-20261103](https://github.com/bikenshrestha2024/opensees-nbc105-research/tree/backup/pre-workorder-rename-20261103). No internal modules, input histories or archived evidence were renamed. Native OpenSeesPy integration regression tests have not been run.
