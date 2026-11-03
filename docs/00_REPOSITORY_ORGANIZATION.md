# 00 — Repository organization and numbered naming policy

## In-force policy (nonbreaking)
- Retain all V167 entry points `01_*.py` through `18_*.py`, plus `20_*.py` and `21_*.py`, in the root. `19` is intentionally unused.
- Provide matching numbered Markdown guides under `docs/programs/`; reserve `00_PROGRAM_INDEX.md` for navigation.
- Number workflow **entry points** only. Do not prefix Python package implementation modules with digits: such names cannot be imported with ordinary Python `import` statements.
- Never bulk rename versioned module imports, source exports, historical manifests, data records, or validation snapshots on an untested branch.
- Track version history with Git commits and release tags; use `V###` file suffixes for historical evidence, not as a substitute for a current-source manifest.

## Proposed staged directory architecture (not yet a performed move)
```text
README.md
00_READ_FIRST_RUN_ORDER.md
01_START_ETABS_TO_OPENSEES.py ... 18_BUILDING_FULL_NONLINEAR.py
20_AUDIT_LOAD_CONNECTIONS.py
21_TRACE_FAILED_ELEMENT.py
components/                  # importable active backend (keep Python names)
Research_Components/         # material/component studies
Calibration_Steel02/         # research calibration
Material_Catalog/            # parameter profiles and provenance
docs/
  00_REPOSITORY_ORGANIZATION.md
  programs/00_PROGRAM_INDEX.md
  programs/01_...md ... 21_...md
  archive/                   # future relocation of legacy markdown only
benchmarks/                  # benchmarks and independent comparisons
tests/                       # lightweight verification
Input_Records_V141/          # checked motion records; preserve metadata
Saved_Project_V156/          # preserved old export, not current build
```

## Safe migration procedure
1. Inventory all 1,560 tracked paths at V167 and identify Python imports, dynamic import strings, GUI entry points, relative file paths, and Windows-specific paths.
2. Create a dedicated refactor branch and capture exact before/after file hashes. Record one-to-one old/new path mappings.
3. Move one group at a time, update every call site, resource path, tests, and README. Check case-sensitive paths on GitHub and case-insensitive paths on Windows.
4. Run `python -m compileall -q components`, existing test scripts, launcher smoke tests (without running a full earthquake case), and independent validation checks; only then merge.
5. Preserve archived results and all V167 evidence. Do not delete source material or claim a nonlinear analysis succeeded based on documentation changes.

## Priority engineering improvements
1. Fix the known nonlinear first-step non-finite `localForce` error and map failed element 110280 to its true source type, nodes and geometry.
2. Reconcile gravity loads, shell/frame connectivity, rigid diaphragm constraints, concentrated mass and ULS/SLS options against ETABS.
3. Diagnose the RSA missing `components/model/assembly.py` resolution reported in the Windows runtime; check working-directory assumptions and source/runtime mixing.
4. Provide a cancellable eigen solver process with a timeout and reproducible logs; avoid claiming Python-level cancellation of blocking native calls.
5. Validate full-length bidirectional ground motions, record units, time step sensitivity, eccentricity variants and P-Delta sensitivity.
6. Add wall-opening fidelity, RC core boundary elements, FVD/BRB per-device force/velocity/stroke/energy outputs, and test comparisons.
7. Add `pytest`/CI smoke checks that do not require an unavailable licensed ETABS or native solver, and mark unavailable tests as skipped.

## Verification status
This change creates documentation only. It does not reorganize executable paths, run OpenSeesPy, resolve the first-step failure, or validate thesis results.
