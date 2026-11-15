# 2026-11-15 — Active dependency graph: from-import submodule coverage

**Source baseline:** `a861dac7ce54363e7a4f2d4c0535def8f96cb0b5`  
**Ownership:** existing integrated audit (`tools/audit_repository_integrated.py::import_graph`)  
**Defect status:** SOURCE-CONFIRMED; fix and tests on separate audit branch; CI is the acceptance gate.  
**Engineering:** NATIVE ETABS/OPENSEES, 32/76/97 supports, NBC compliance and full NLTHA NOT VERIFIED.

## Inspected source and root cause

The previous `ast.ImportFrom` branch computed `requests = [(name, node.lineno)]` from only `node.module`. When the import is `from . import child`, `node.module is None`, so the analyzer mapped it to the package itself, producing no edge for package `__init__.py` to `child.py`. Similarly, `from components.package import module` recorded only the package, not the tracked submodule. This is a **false-negative static dependency inventory** that can hide import cycles. The pre-existing test fixture already included `from . import left` but asserted only other direct imports, allowing the omission to persist.

## Coordinated correction

For `ImportFrom`, retain the package import request and add each explicit `name.alias` only when its fully-qualified path resolves to a tracked Python module. Do **not** report missing aliases as unresolved packages, since `from package import EXPORTED_SYMBOL` can import a normal symbol, not a module. The existing eager-vs-deferred distinction, package-resolution rules and historical-snapshot exclusion remain unchanged.

## Regression and output evidence

- `tests/test_repository_integrated_audit.py::test_local_edges_relative_imports_cycles_and_dynamic_import_review` now asserts the missing `__init__.py -> left.py` edge.
- New regression verifies `from components.package import submodule, EXPORTED_CONSTANT` records the real dependency and does not falsely flag the symbol.
- New regression verifies relative `from . import child` and other package submodule edges.
- Run `python -m unittest -v tests.test_repository_integrated_audit`.
- The existing `.github/workflows/integrated-repository-audit.yml` runs those tests and publishes `audit/integrated/02_DEPENDENCIES/import_graph.json` and the exact source-index review ledger.

## Review status

This review covers the actual implementation of `import_graph`, the associated synthetic test declarations, its package dependency edge cases and the emitted graph contract. It does **not** claim complete semantic inspection of all active Python functions, nor that a static edge is a runtime defect. No original ETABS model, workbook, motion, native result or launch module is altered.
