# Shared repository path resolution

Source: [repository_paths.py](../../../../components/shared/repository_paths.py).

`runtime_repo_root(module_file, component_source=None)` is the single
source-independent resolver used by compatible interfaces in Gravity,
input autofill, MRSM, and exploratory GUI modules. It is designed for:

- Direct imports, where `module_file` is the real
  `components/<family>/<file>.py` path.
- Root compatibility launchers that exec-load the component and explicitly
  set `_component_source` to its actual path.
- Exported runtime copies, where the same layout exists under a new
  project-owned root.

It intentionally does not consult the process working directory, the most
recent user-selected output folder, or an ETABS result path. A new folder
selection therefore cannot redirect module imports or cross-link a different
source model. It does not inspect EDB/Excel bytes or establish numerical
equivalence.

Compatibility contract tests: `tests/test_facade_runtime_context.py`.
Retain the small `_runtime_repo_root()` wrappers only for callers whose
external entrypoint depends on their existing names, while all wrappers
delegate to this single implementation. No native solver is run by this
helper.
