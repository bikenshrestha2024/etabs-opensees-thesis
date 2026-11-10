# V4 architecture navigation — migration without duplicate engines

**Status:** Current-source crosswalk, not authorization to move files. Source baseline: `main@a7e26466c`.

## Locate the current implementation

| Human workflow | Current source implementation to inspect | V4 target boundary | Rule |
|---|---|---|---|
| Project ETABS export | `OpenSees_Complete_Export_V118.py` | ETABS adapters | Reuse original OAPI extraction; source EDB read-only |
| Assembly | `components/model/assembly.py` | OpenSees model assembly | Preserve nodes, sections, stiffness, constraints and gravity |
| Gravity solver | `components/gravity/solver_stack.py` | Gravity analysis | Support strategy does not redefine applied loads |
| Gravity evidence | `components/gravity/evidence_workflow.py` and `components/gravity/comparison_bundle.py` | Comparison/evidence | Keep separate solver equilibrium and ETABS acceptance |
| ESM GUI/calculation | `components/equivalent_static/calculation_and_gui.py` | ESM | Review PR #15 before changes; preserve original Excel Aw/T method |
| ESM evidence | `components/equivalent_static/evidence_bundle.py` | ESM evidence | Do not create a second packager |
| Modal | `components/modal/analysis.py` | Modal | Do not substitute eigen T1 for adopted Rayleigh/Excel T1 |
| MRSM | `components/response_spectrum/model_analysis.py` | MRSM | Review PR #15; compare CQC and ETABS equivalent cases |
| Output-folder GUI | `components/ui/output_folder.py` | Shared GUI | Extend instead of creating another folder-opening utility |
| Seismic ZIPs | `components/validation/seismic_review_bundle.py` | Shared evidence | Reuse existing SHA dedup and avoid ZIP recursion |
| Shared recorders | `components/shared/response_recorders.py` | Shared results | Preserve response definitions, units and load cases |
| Model-independent research | `src/thesis_core/neutral_model.py` | Neutral schema | Prototype; no migration of full 3-D structure yet |
| Standalone benchmark | `src/opensees_engine/standalone.py` | Independent OpenSees | Benchmark-only; not an accepted full high-rise replacement |

The active module register is `engineering/registry/CANONICAL_MODULES.csv`. It is authoritative for current ownership labels **only after engineering review**; existing entries explicitly mark several paths as NOT_REVIEWED.

## Human navigation versus Python import boundaries

The V4 numbered directories (ETABS, Excel, OpenSees, Python, Comparison, Thesis Research, Documentation, AI Development, Tests, Tools) are **proposed documentation/navigation sections**. Do not immediately copy each existing Python implementation into these directories. This repository already contains `components/`, `src/`, working root launchers, engineering rules, and an existing core registry.

Recommended migration procedure:

1. Generate and inspect `docs/architecture/generated/REPOSITORY_FILE_INVENTORY.csv`, `IMPORT_GRAPH.json`, `DYNAMIC_REFERENCE_AUDIT.csv`, `GUI_ACTION_INVENTORY.csv`, `EXACT_DUPLICATE_CANDIDATES.json` and `AST_DUPLICATE_CANDIDATES.json` on a local clone.
2. Check every runtime string path, dynamic importer, user command line, GUI callback, historical launcher and tests for a candidate module.
3. Identify a canonical owner and create **one** import-compatibility wrapper only if migration tests pass.
4. Compare numerical outputs against source-identified baselines. Never infer success from the existing tiny gravity equilibrium error.
5. Maintain the 32 filtered, 76 source and 97 support configurations as distinct named cases.
6. Review on Windows/Spyder/ETABS v23 before merging. Keep first-step X-wall element 110280 unresolved pending native evidence.

## V4 audit command

```powershell
python -m unittest discover -s tests -p verify_repository_structure_audit_v4.py -v
python tools/audit_repository_structure_v4.py --output docs/architecture/generated
```

GitHub Actions also uploads the read-only `repository-v4-audit` artifact. The inventory is an architectural static-screening report; it does not prove source-equivalence, successful modal/RSA execution, wall hysteresis validity, or NBC acceptance.

**Avoid premature changes:** Do not move `components/`, `Research_Components/`, `Saved_Project_V156/` or root launchers based solely on this file. PR #15 contains pending GUI autofill changes and must be reconciled before touching the same files.
