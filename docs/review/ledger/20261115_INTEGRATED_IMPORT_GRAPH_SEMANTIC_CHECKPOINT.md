# Current-head targeted semantic checkpoint — dependency import graph

Baseline main Git SHA: `a861dac7ce54363e7a4f2d4c0535def8f96cb0b5`. Review purpose: add actual inspected scope to the existing frozen baseline, **not** rewrite historical ledger or mark uninspected AST units reviewed.

| Source | Inspected code scope | Correctness question | Finding | Test evidence |
| --- | --- | --- | --- | --- |
| `tools/audit_repository_integrated.py` | `as_module`, `import_graph`: direct/relative `ImportFrom` branch, import target resolution, eager/deferred edge logic | Does `from . import child` create a real tracked import edge? | Missing alias-derived edges for tracked modules; fixed in branch | Existing and new synthetic `tests.test_repository_integrated_audit` |
| `tests/test_repository_integrated_audit.py` | Whole current test module, with emphasis on import graph fixtures and assertions | Would regressions catch missing alias-derived edges and symbol false positives? | Existing fixture did not assert `__init__ -> left`; assertions added | CI on exact branch |
| `src/thesis_core/__init__.py` | Entire short file | Real package-relative importing pattern exists | Uses `from .neutral_model import...` (already covered by old code) | Source context only, not a runtime bench |

No physical engineering model units, source files or dynamically loaded GUI plugins have been accepted by this inspection. All other function-level entries remain as recorded in the automatic `audit/integrated/08_SEMANTIC_REVIEW/function_review_register.csv` with `NOT_REVIEWED` status. Specific tool change requires GitHub CI on branch SHA before source-level status is upgraded to TESTED.
