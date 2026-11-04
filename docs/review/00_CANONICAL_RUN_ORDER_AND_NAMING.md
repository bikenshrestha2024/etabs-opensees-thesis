# 00 — Canonical execution map and safe naming

This map is an **engineering dependency order**, not an automatic run-all batch.
It supersedes casual filename sorting and is designed to preserve old scripts
until tests establish that their imports and outputs can be migrated safely.

## 00–09 evidence sequence

| Stage | Canonical entry | Required output before progression |
|---|---|---|
| 00 Provenance | `34_NBC105_RC_DUAL_C_D_TARGETS.py`, `35_SOIL_C_NLTHA_PREFLIGHT.py` | Soil C target/record SHA, proper Z/I/Omega and 8 complete A/B pairs; YX planned; Gorkha/Loma notes |
| 01 Import/geometry | `01_WORKFLOW_START.py`, `02_INPUT_READINESS.py`, `19_AUDIT_LOAD_CONNECTIONS.py` | Verified ETABS export, wall openings, diaphragms, source mass, real member assignments |
| 02 Materials | `03_MATERIAL_PARAMETER_SETUP.py` to `09_LITERATURE_COMPONENT_DEMO.py` | Experimental source cards, 3D wall, FVD/BRB native device check, actual rebar register |
| 03 Gravity/PDelta | `10_GRAVITY.py`, `20_TRACE_FAILED_ELEMENT.py` | Converged preload, mass/reaction balance and valid geometrical nonlinearity |
| 04 Modal/time step | `11_MODAL_ULS_SLS.py`, `32_NBC105_PAIR_SPECTRUM_AUDIT.py` | Real T1 and Tn90 X/Y and damping mode selection; record dt and 0.05–6 s coverage |
| 05 Linear cross-check | `12_EQUIVALENT_STATIC.py`, `13_RESPONSE_SPECTRUM.py`, `14_LINEAR_TIME_HISTORY.py` | Structural model and dynamic response cross-check, not a replacement for NLTHA |
| 06 Isolated nonlinear | `15_BUILDING_NONLINEAR_TRIAL.py`, `21_NLTHA_TRIAGE.py` | ZERO/X/Y probes, earliest X-wall failure traced, no artificial convergence claims |
| 07 Production NLTHA | `16_NONLINEAR_REVIEWED_MODEL.py`, `17_BUILDING_FULL_NONLINEAR.py` | 8 motion pairs, each XY/YX in separate fresh domains, full nonlinear accepted-state record |
| 08 Model comparison | `27_COMPARE_OUTRIGGERS.py`, `36_SOIL_C_NLTHA_RUN_MATRIX.py` | 112 configs × 2 orientations = 224 **intended** analyses (ULS/SLS, M0–M6), comparisons only from completed cases |
| 09 Interpretation | `18_NONLINEAR_PERFORMANCE.py` | physical acceptance tables, drift/torsion/member limits, FVD/BRB forces and energy, actual thesis plots |

## Root numbering policy

- `01–20` canonical code paths are listed in [the original 01–20 mapping](../../00_READ_FIRST_RUN_ORDER.md).
- **Historical aliases currently duplicate numeric prefixes** (for example, `01_START_ETABS_TO_OPENSEES.py` versus `01_WORKFLOW_START.py`, and `17_LITERATURE_COMPONENT_DEMO.py` versus `17_BUILDING_FULL_NONLINEAR.py`). Sorting root file names alphabetically is **not** a verified analysis order.
- **Do not mechanically rename historical aliases or internal `components/` imports**. A safe migration requires an import/call graph, launcher smoke tests, known Windows references and retained source hashes.
- All *new* engineering code goes into stable named packages under `components/`, not `V171, V172` root forks; new numbered launchers require the guide and test.
- Historical results belong in immutable versioned archives; source files and experiment provenance must not be rewritten to improve appearance.
- Source guide naming: `docs/source/<same Python path>.md`; launcher guide naming `docs/programs/<same stem>.md`. Machine-readable result artifacts go in local analysis output folders rather than root GitHub.

## How to update the review inventory

```powershell
python tools/audit_active_repository.py --output "D:/Thesis/Review/Active_Repository_Inventory.json" --fail-on-missing-canonical
python tests/verify_active_repository_audit.py
```

The JSON contains **module names, code line counts, SHA256, top-level symbol/line map, imports, syntax exceptions, missing individual guides, canonical launcher existence and duplicate-number aliases**. It is a static coverage register, not actual semantic line review, experimental calibration or NBC compliance.

For each module, after the static index, add a review ledger item with: exact lines, structural hypothesis, unit conventions, source clause/DOI, native test, accepted model state, reviewer and remaining blocker.

[Full physical code review](00_ACTIVE_CODE_ENGINEERING_REVIEW.md) · [RTFC prompt](../../.github/prompts/soil-c-nltha-rtfc.prompt.md)
