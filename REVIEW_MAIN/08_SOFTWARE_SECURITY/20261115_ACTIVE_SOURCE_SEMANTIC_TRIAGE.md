# Active source semantic review coverage — evidence and limits (2026-11-15)

## Source identity and breadth

The existing integrated CI produced a **source-only ZIP** for commit `4e837643a11345c99e0bbec3f4e4eea674f7fbf2` (the current later documentation-only main revision is tracked separately). This source-only ZIP was opened locally and its **533 active Python files** inspected via AST. The existing integrated Git-index report lists **3,939 source review units**, comprising module-level units plus named definitions, with `semantic_review_completed_count=0` by design. Their source SHA, line span and risk signals are available in `audit/integrated/08_SEMANTIC_REVIEW/function_review_register.csv`.

A separate conservative AST triage performed on the same active snapshot indexed **3,407 named class/function/async definitions**. It identified **19 candidate calls to integer conversion involving numerical or modeling-related expressions** and **133 exception handlers whose first statement is `pass` or `continue`**. These are **occurrences**, not 19 confirmed numerical bugs or 133 proven silenced engineering failures. Some risk candidates are legitimate `ceil`/rounding, print/reporting, GUI cleanup or solver return-code conversion.

## Targeted semantics completed on this pass

- Reviewed actual mesh assembly, selected 4/8/16 staging and workbook export code and the existing synthetic regression suite.
- Confirmed non-integral input truncation across those layers as a **coordinated numerical-model identity defect**, fixed and tested with exact-value validation.
- Inspected live `AGENTS.md` coding contract, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, source guides and numbered-launcher source ownership. The change does not rewrite original ETABS source files or alter the governing NBC 105:2025 design basis.
- Existing CI inventories source, import graph, facade contracts, writer paths and archived Git-object duplication; these remain *static* discovery results, not semantic approval of every function.

## Prioritization and next investigation queue (not proven bugs)

| Priority | Inspection target | Evidence needed |
| --- | --- | --- |
| P0 | `components/nonlinear_time_history/runner_and_gui.py`, `components/gravity/solver_stack.py` | Check all accepted time samples, nonfinite first-step event, solver return codes, real localForce and failure trace |
| P0 | `components/model/assembly.py`, `components/gravity/support_scenarios.py` | Verify 32 original supports vs 76/97 mesh nodes, slab/beam/wall load transfer and native ETABS reactions |
| P1 | `components/linear_time_history/runner_and_gui.py` | Confirm dt and duration, ceil-based sample count, recorded last sample, cross-model signed loads |
| P1 | `components/equivalent_static/calculation_and_gui.py`, `components/response_spectrum/` | Source workbook SHA and chosen Aw/T1; governing NBC 105:2025 factor/units, seismic-mass separation and ETABS comparison |
| P1 | `components/ui/application.py` and GUI wrappers | Inspect broad exception-handling paths for swallowed errors with real Windows/Spyder test fixtures |
| P1 | `components/gravity/load_path_formulas.py` | Verify no formula sheet is mistaken for solver element force and no floating mesh identity accepted |
| P2 | Archived and historical source snapshots | Preserve Git object hashes, dependencies, license/provenance, historical readers; never execute or delete by name alone |

## Honest acceptance gates

**Static source coverage:** inventory and parser gate. **Function-by-function semantics:** incomplete (3,939 generated units are not signed off). **Targeted mesh input contract:** source review completed and locally tested; native validation pending. **Gravity ETABS/OpenSees equivalence:** unverified. **NLTHA:** first-step X-wall and full records unresolved. **Governing NBC 105:2025 code compliance:** unverified, requires real accepted model evidence and code interpretation.

No single CI green checkmark proves a full semantic engineering review. An archive of the active code and this triage evidence allows future reviews to work from the actual same source SHA without repeatedly rediscovering paths.


## Verified current revision and source-wide triage

The current verified integrated CI snapshot is `950a221adc5b3438f9981ca3c0e96a00d6df88e7` with **3,058 tracked files, 534 active Python files, and 3,959 module/function/class review units**. The independently generated AST review-priority scan over the **actual 534 active files at the same revision** identified **3,425 named definitions**, **19 candidate integer-cast sites** and **133 potential suppressed-exception handler sites**. These are *inspection candidates*, not 152 proven defects. Only the mesh discretization and finite-gravity/transient acceptance issues in the linked targeted review documents were independently confirmed and corrected during this pass. [Passing integrated workflow](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43698880921). The audit still reports **zero completed semantic review units**, so no complete-codebase approval is asserted.


## Provenance-tag quality-gate finding (2026-11-15)

[NLTHA Python quality run 43699270193](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43699270193) found one missing mandatory code-reference tag in the newly added public function `components/gravity/mesh_cases.py::validated_mesh_size`, as required by `docs/REF_TAG_CONVENTION.md`. The numerical regression tests and integrated audit passed. This documentation defect was corrected on `main` at [commit `64f2d2a`](https://github.com/bikenshrestha2024/etabs-opensees-thesis/commit/64f2d2a529067c9c5b947786cb87845d40361c8f) by tagging the existing source guide without changing numerical behavior. The NLTHA Python quality workflow must be rerun on the corrected source before declaring that gate passed.
