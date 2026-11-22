# Relative-import audit blind spot — integrated engineering/migration follow-up

**Review date:** 2026-11-22
**Baseline inspected:** main commit `9c708f448903a7e9d097d5299a5f137dd9d75890`
**Status:** Source-audit correction submitted; **native structural and saved-output migration acceptance remains open**.

## Verified source-level finding

Two different audit tools previously inspected imports using direct AST names:

- `tools/audit_cross_module_consistency.py::_interlinks` counted `import components.X` and `from components.X import name` but skipped `from ..inputs import ...` and `from . import ...`. Its `module_owner_import_links` was consequently an **undercount**.
- `tools/audit_output_writer_reader_pairs.py::_imports` recorded `node.module` without its relative level or containing package. Its `local_imports` could omit real intra-project producer/consumer dependencies, and did not identify resolvable package submodules.

The correction routes both through `tools/module_import_edges.py::import_targets`. Resolution uses the containing source package and checks actual tracked-tree-local submodule files or directories before treating a `from package import name` name as another module. Relative imports beyond the package are not fabricated. It remains **static**: computed dynamic imports, execution order and caller-to-result pairing still require separate verification.

## Tests and output contract

`tests/test_source_dependency_edges.py` covers:

1. Absolute, `..` parent-package and `.` sibling imports.
2. Avoiding false submodule edges for imported functions/variables.
3. Inclusion of a cross-owner GRAVITY → SOURCE_INPUTS edge in the module integration report.
4. Retention of the resolved source module in the output producer/consumer review queue.
5. Invalid upward import behavior from a root script.

The test was added to `.github/workflows/integrated-repository-audit.yml` and is subject to CI. Existing JSON/CSV schema and stage folders were not changed. The imported module paths are **candidates**, not evidence that a path was used at runtime.

## Measured baseline inventory (read-only Git tree)

The 2026-11-22 `main` baseline contained **3,422 Git blob paths**, of which **896 had the .py extension**. There were **383 same-blob groups** covering **461 excess identical-path instances**. Many are historical snapshots, research fixtures or mirrored results. Exact identity is not proof a copy can be removed safely. The active-only clone review is still separately tracked in [issue #142](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/142).

These numbers describe a specific commit; they must not be presented as a live count after future changes.

## Required next evidence; not performed here

- Audit deferred/dynamic import groups in real application startup and GUI callbacks; import edge visibility does not prove all modules are integrated.
- Adjudicate individual AST clone groups by calls, behavior and output parity before deleting any function or compatibility facade.
- Pair every actual writer and reader on the same source/model hash, state, units and run manifest; [issue #141](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/141) remains open.
- Produce native ETABS/OpenSees 32/76/97 pointwise reaction evidence and compare complete six-DOF force/moment resultants; [issue #140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140) remains open.
- Verify the latest 12 m X-wall native EDB and source workbook by bytes, mapped geometry and NBC 105 ULS/SLS equations.
- Reproduce first-step nonlinear wall convergence, full ground-motion runs and Windows saved-case reopening.

**Acceptance boundary:** This correction addresses one auditable graph-construction defect. No solver source inputs, stiffness, restraints, loads, result artifacts, workbook or historical archive were modified. Static regression tests cannot certify NBC 105 compliance, numerical equivalence, convergence or complete directory migration.
