# Source consistency, duplication and integration review — 2026-11-22

**Repository:** `bikenshrestha2024/etabs-opensees-thesis`, `main`  
**Audit classification:** STATIC IMPLEMENTATION WORK COMPLETED IN PART; NATIVE ENGINEERING ACCEPTANCE OPEN  
**Source:** GitHub-hosted `tools/audit_repository_integrated.py` and
`tools/audit_cross_module_consistency.py` outputs, verified code changes.

## 1. Source tree inventory and findings

The integrated baseline at `3debde49` inspected 3,408 tracked files,
including 676 active source/test Python files. Its static report recorded
0 unresolved explicit local imports, 1,141 potential write calls, 724
potential read calls, and 95 legacy output-path literals. It remains
`BLOCKED` on source attestation, legacy output, import cycles and native
gravity/NLTHA/NBC engineering gates. The report does **not** equate
file inventory with a line-by-line semantic review.

The new current-active scan (root launchers plus components/src/tools,
not tests or historical copies) reported **394 active Python source
files**, 0 parse errors, **2 shadowed top-level definitions** and
**33 cross-file AST-identical function-body candidate groups** at its
first run. These 2 shadowed definitions were both B01–B04 benchmark
dispatchers in:
- `tools/verification_studio/ETABS_OpenSees_Verification_Studio.py`
- `tools/verification_studio/ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py`

They were renamed explicitly to `_run_legacy_case`; the assignment
`_run_legacy_case = _run_case` was removed. Tests now assert exactly
one legacy dispatcher and one public dispatcher in each file and run
both built-in self-tests without invoking native ETABS. This removes
shadowing without changing the B01–B12 public benchmark set.

The clone inventory also identified four identical
`_runtime_repo_root` implementations in Gravity, input autofill, MRSM
and exploratory GUI. Their core behavior is now centralized in
`components/shared/repository_paths.py`, while existing compatibility
wrappers and facades retain their function names and arguments.
`tests/test_facade_runtime_context.py` verifies direct imports,
root-level facade execution and exported runtime relocation.

**Remaining clone groups:** require *per-function* semantics review.
Some are source hashing utilities, numerical formula wrappers or GUI
interaction handlers; matching AST does not make them safe to delete
or share. Existing archived exact blob copies are intentionally
preserved for provenance. The current clone count should be read
from the latest CI artifact after these refactors, not copied from
the historical 33-group baseline.

## 2. Provenance and latest reference corrections

`components/inputs/aw_sources.py` previously accepted identical EDB
path text even when `source_edb_sha256` was absent, the EDB was missing
or bytes had changed. Source evidence is now accepted for automatic
ETABS-linked Aw only when the current EDB file exists and has a valid
SHA-256 matching the provenance record. Explicitly registered verified
references take priority over newer unregistered files. Symlinked and
missing provenance records are not followed. The tests check
identical-content copies, changed EDB bytes, missing digest, missing
EDB and registry precedence.

**Current named thesis reference:** `NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7.xlsx`.
This is a *candidate*, not authority by filename: adoption also
requires exact source EDB identity, two connected 12 m X walls with
verified openings, three solid 6 m Y wall lines, ULS/SLS and workbook
cell/numerical review. The code's current static scanner found no
older named V10_0–V10_6 workbook literals in its active source tree.
Other historical workbooks remain permitted as labelled comparisons.

## 3. Module folders, README navigation and output policy

All 13 active component folders now contain READMEs generated against
the actual source file inventory, with direct links to every current
`*.py` file. `components/README.md` is their central index. The
repository's root README links it. A new
`tools/audit_component_readmes.py --check` gate detects missing and
stale module links, and is wired into CI.

Module ownership/data flow:
`SOURCE_INPUTS -> MODEL -> GRAVITY/MODAL -> ESM/MRSM -> LTHA/NLTHA ->
VALIDATION -> GUI`, with NBC105, SECTIONS and SHARED supplying
reference rules and common services. This is a responsibility map,
not a guarantee of native runtime equivalence. All module imports,
clones, writer/reader candidates and version literals are inventoried
in `audit/module_consistency/`.

**Do not rename existing physical directories or duplicate outputs:**
`components/inputs/output_layout.py` and `output_contract.py`
remain canonical, including the distinct historical
`02_MODEL` and `02_GRAVITY` stage names. New contract-aware runs
retain immutable source SHA/state/case identifiers; legacy saved
result paths remain read-only aliases until writer + reader parity tests pass.

## 4. Verification and remaining engineering blockers

Static tests/CI checks are necessary but cannot execute private Windows
ETABS COM or independently establish native ETABS/OpenSees parity.

| Gate | Status | Required evidence |
|---|---|---|
| Active syntax/import inventory | Tests available; inspect latest CI | Full tracked and runtime-path evidence |
| Top-level name-shadowing | Two known cases refactored; rerun strict scan | All current definitions unshadowed |
| 33 prior clone groups | Partial refactor, remainder under review | Group-by-group equivalence and compatibility |
| Source EDB/workbook authority | Stricter SHA and registration checks in code | Run against actual private EDB/XLSX |
| Output/README layout | Indexed and CI-guarded | Windows saved-case reopen; no loss or duplication |
| 32/76/97 gravity | Not accepted | Matched nodal support distribution and stiffness/edge constraints |
| NBC 105 ESM/MRSM | Not exhaustive | Clause/table/annex source and native numerical parity |
| NLTHA | Not accepted | First-step X-wall recovery and full-length case matrix |
| Full production migration | Incomplete | Every actual writer and consumer exercised with source hashes |

The 3,041.266 kN gross-shell support mismatch and the later
768.045 kN ETABS-elastic maximum difference remain **physical unresolved
blockers**. No code cleanup is permitted to cosmetically change reaction
vectors, collapse support identities or label gross-equilibrium agreement
as structural equivalence.

## 5. Reproducible static checks

```powershell
git pull origin main
python -m unittest tests.test_cross_module_consistency_audit tests.test_component_readme_catalog tests.verify_module_boundaries tests.test_verification_studio_dispatch_contract tests.test_facade_runtime_context -v
python tools/audit_cross_module_consistency.py --repo . --report-dir audit/module_consistency --fail-on-parse --fail-on-shadowed
python tools/audit_component_readmes.py --root . --output audit/component_catalog.json --check
python tools/audit_output_writer_reader_pairs.py --repo . --report-dir audit/output_pairs --fail-on-parse
```

These commands are read-only except for **new diagnostic reports** in
`audit/`. No old EDB/XLSX, solver outputs or historical snapshots are
deleted, overwritten or uploaded.

For the complete input/output and native verification gates, refer to
[active integration policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md)
and [output structure policy](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md).
