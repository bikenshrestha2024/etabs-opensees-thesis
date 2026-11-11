# 00 — Numbered program index

The table lists the current canonical launchers. Numeric IDs are stable navigation labels; gaps are intentional. Material/component validation precedes nonlinear building work. The program numbers are navigational and do not certify structural validity.

| Step | Launcher | Guide | Function |
|---|---|---|---|
| 01 | [`01_WORKFLOW_START.py`](../../01_WORKFLOW_START.py) | [Guide](01_WORKFLOW_START.md) | Original ordered main ETABS-to-OpenSees GUI (retain `01.py` compatibility alias) |
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
| 21 | [`21_NLTHA_TRIAGE.py`](../../21_NLTHA_TRIAGE.py) | [Guide](21_NLTHA_TRIAGE.md) | NLTHA isolated diagnostic configuration and evidence review |

| 22 | [`22_NBC105_INPUT_SYNC.py`](../../22_NBC105_INPUT_SYNC.py) | [Guide](22_NBC105_OPENSEES_FIRST_INPUT_SYNC.md) | Synchronize NBC inputs from current OpenSees and reviewed sources |
| 27 | [`27_COMPARE_OUTRIGGERS.py`](../../27_COMPARE_OUTRIGGERS.py) | [Guide](27_M0_M6_OUTRIGGER_COMPARISON.md) | Compare completed M0-M6 cases with identity and completion gates |
| 29 | [`29_NATIVE_DEVICE_BENCHMARK.py`](../../29_NATIVE_DEVICE_BENCHMARK.py) | [Guide](29_NATIVE_FVD_BRB_RECORDER_VALIDATION.md) | Native FVD/BRB recorder benchmark |
| 30 | [`30_CALIBRATE_FVD_FROM_TEST.py`](../../30_CALIBRATE_FVD_FROM_TEST.py) | [Guide](30_FVD_EXPERIMENTAL_CALIBRATION.md) | Fit FVD parameters to supplied experimental data |
| 32 | [`32_NBC105_PAIR_SPECTRUM_AUDIT.py`](../../32_NBC105_PAIR_SPECTRUM_AUDIT.py) | [Guide](32_NBC105_PAIR_SPECTRUM_AUDIT.md) | Audit paired motion spectra and scaling evidence |
| 33 | [`33_NBC105_VERTICAL_APPLICABILITY_REVIEW.py`](../../33_NBC105_VERTICAL_APPLICABILITY_REVIEW.py) | [Guide](33_NBC105_XY_YX_VERTICAL_AND_SCALE_GUIDE.md) | Review XY/YX and vertical-action applicability |
| 34 | [`34_NBC105_RC_DUAL_C_D_TARGETS.py`](../../34_NBC105_RC_DUAL_C_D_TARGETS.py) | [Guide](34_NBC105_RC_DUAL_SOIL_C_D_TARGETS.md) | Generate distinct RC-dual Soil C and D targets |
| 35 | [`35_SOIL_C_NLTHA_PREFLIGHT.py`](../../35_SOIL_C_NLTHA_PREFLIGHT.py) | [Guide](35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md) | Preflight Soil C motion and model evidence |
| 36 | [`36_SOIL_C_NLTHA_RUN_MATRIX.py`](../../36_SOIL_C_NLTHA_RUN_MATRIX.py) | [Guide](36_SOIL_C_M0_M6_RUN_MATRIX.md) | Plan the Soil C M0-M6 run matrix; does not run analyses |
| 37 | [`37_THESIS_EVIDENCE_DASHBOARD.py`](../../37_THESIS_EVIDENCE_DASHBOARD.py) | [Guide](37_THESIS_EVIDENCE_DASHBOARD.md) | Inspect evidence status and hashes; does not approve results |

Legacy filenames remain functional as launch aliases. Underlying components, external records and saved outputs have not been renamed. The nonlinear transient failure is still an open issue.

The machine-readable launcher list is `CANONICAL` in [the inventory tool](../../tools/audit_active_repository.py). The documentation regression checks this table against that list and checks its local links.

[File migration map](../00_WORK_ORDER_RENAME_MAP.md) · [Organization policy](../00_REPOSITORY_ORGANIZATION.md)


## Current active-source review

[Engineering P0–P2 source review](../review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md) and [canonical 00–09 execution map](../review/00_CANONICAL_RUN_ORDER_AND_NAMING.md) explain why root filenames with duplicate numbers must not be sorted as an executable research sequence. [Static analysis inventory](../../tools/audit_active_repository.py) is not physical or native solver validation.
