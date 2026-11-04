# RTFC templates for this engineering repository

Use exactly these four uppercase sections, in order:

1. **ROLE** — specialist perspective and responsibility
2. **TASK** — exact file/defect/action
3. **FORMAT** — structured artifacts, tests and evidence to return
4. **CONSTRAINTS** — engineering invariants, source privacy and prohibitions

This is a compact AI brief; **not** an OpenSees parameter specification and never a substitute for native NLTHA verification.

| Sequence | Template | Expected use |
|---|---|---|
| 00 | [Project contract](00_PROJECT_ENGINEERING_RTFC.md) | Every substantial repo change |
| 01 | [Core-wall first-step triage](01_X_WALL_FAILURE_RTFC.md) | P0 solver pathology |
| 02 | [Soil C ground motions](02_SOIL_C_RECORDS_RTFC.md) | Soil C target, pair scaling and input |
| 03 | [RC and devices](03_MATERIALS_WALL_FVD_BRB_RTFC.md) | Calibration and experimental evidence |
| 04 | [M0–M6 comparisons](04_M0_M6_COMPARISON_RTFC.md) | Full 8-pair nonlinear matrix |

**Usage:** Open only the prompt relevant to the specific task. Add exact file paths, current error, expected behavior and data location; avoid pasting entire repository or private model contents into chat.

**Priorities and sources:** [AGENTS](../../AGENTS.md) · [Stage 35](../programs/35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md) · [Stage 36](../programs/36_SOIL_C_M0_M6_RUN_MATRIX.md) · [Stage 37](../programs/37_SOIL_C_NLTHA_JSON_SCHEMA.md) · [NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
