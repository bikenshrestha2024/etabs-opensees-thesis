# Active module integration, source authority and duplication audit
**Review date:** 2026-11-22  
**Status:** STATIC SOURCE INTEGRATION IMPROVEMENTS COMMITTED; NATIVE ENGINEERING ACCEPTANCE OPEN

## 1. Scope and primary audit command

`tools/audit_cross_module_consistency.py` performs an AST-level scan of
all active root Python entrypoints and the active `components/`, `src/`,
and `tools/` source trees. It does not analyze archived snapshots as
production code, execute ETABS COM, run OpenSees, modify user documents,
or delete/move any files.

```powershell
python tools/audit_cross_module_consistency.py --repo . --report-dir audit/module_consistency --fail-on-parse
python -m unittest tests.test_cross_module_consistency_audit tests.verify_gravity_case_reaction_registry -v
```

The report folder contains **01_ALL_MODULE_CONSISTENCY.json**,
**02_SHADOWED_DEFINITIONS.csv**, **03_DUPLICATE_FUNCTION_CANDIDATES.csv**,
**04_INTERMODULE_IMPORTS.csv**, and **05_WORKBOOK_VERSION_REFERENCES.csv**.
All results are read-only source metadata, without source workbook contents.
`--fail-on-shadowed` is an optional stricter review gate; pre-existing
duplicate symbol candidates should first be triaged and resolved, not erased.

## 2. Responsibility and data lineage

| Owner | Reads authoritative input from | Produces/validates | Downstream consumers |
|---|---|---|---|
| SOURCE_INPUTS (`components/inputs`) | ETABS source EDB manifest, exact export XLSX/CSV, SHA256-protected source selection | Provenance, model-aligned section/area/Aw, gravity/load profiles | MODEL, NBC105, ESM, Modal, MRSM, LTHA, NLTHA |
| MODEL (`components/model`) | Identified EDB export, supported material/geometry policies, versioned configuration | Model assembly, stiffness, mass, constraints, load ledger | All solvers and verification |
| GRAVITY | Immutable model + full gravity load ledger + 32/76/97 support policy | Solver result, support reactions, source reconciliation | Validation, seismic initial state |
| NBC105 | Current adopted NBC 105:2025 rules plus verified project values | Code-reference calculations and explicit open compliance gates | ESM/MRSM, UI/engineering evidence |
| ESM (`components/equivalent_static`) | NBC, earthquake loads, model and site inputs | Equivalent static seismic actions | MRSM scaling, response reviews |
| MODAL | Assembled source-matched stiffness/mass/constraints | Eigenmodes, effective mass participation, period/damping evidence | MRSM, LTHA, NLTHA |
| MRSM (`components/response_spectrum`) | Modal + NBC spectra + ESM scaling + model identity | Scaled response spectra and response outputs | Structural checks and comparisons |
| LTHA / NLTHA | Model, verified motions, damping, mass, gravity preload | Time histories and performance evidence | Response validation, thesis M0–M6 comparisons |
| SECTIONS | Source materials, section assignments and modifiers | Cross-section/element definitions | MODEL and response checks |
| VALIDATION | Matching ETABS/OpenSees case identity and native exports | Reaction, drift, force, torsion, evidence comparisons | GUI, REVIEW and thesis acceptance |
| GUI | Calls above modules and reads their published manifests | Navigation, status, filters and figures | User — never source authority |
| SHARED, CORE_OR_ADAPTER, TOOLING | Core helpers and package contracts | Reusable functions/audit evidence | All applicable modules |

Actual import edges appear in the generated `04_INTERMODULE_IMPORTS.csv`;
this table is a desired responsibility map, **not proof** that every runtime
consumer is currently connected or scientifically validated.

## 3. Source-reference selection rules — no stale workbook by filename

1. First select an **actual source EDB** using the active project manifest and
   exact SHA256, not a similarly named working copy. Preserve the original.
2. The analyzed ETABS full export (including compressed XLSX) and separate
   `Assignment Export` are different roles; beam-force split workbooks may
   include several sheets/parts. Preserve all row counts and source hashes.
3. For the selected thesis geometry, X is **two connected 12 m structural-wall
   lines** with verified openings and Y is three solid 6 m wall lines.
   `components/inputs/model_aligned_reference.py`,
   `aw_sources.py`, `grouped_wall_aw.py` and
   `opensees_nbc_sync.py` must reject mismatched model fingerprints.
4. `NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7.xlsx` is the user's latest
   specifically named candidate reference; **the filename alone is not proof**
   that its formulas, walls or source EDB correspond to the active model.
   Old V10_6/V10_5 worksheet references must be reviewed and may be retained
   only as historical fixtures, not silently promoted as current.
5. Every ETABS/ESM/MRSM/gravity output consumer must verify the selected
   source/model SHA, load state, units, support policy and actual result file
   before interpreting data. `NOT_VERIFIED` cannot be treated as a pass.
6. `SOLVER_FINISHED`, `GLOBAL_EQUILIBRIUM_PASS`, and
   `NODAL_REACTION_EQUIVALENCE` are independent flags. A zero total
   imbalance does not clear 3,041 kN (gross shell) or 768 kN (ETABS-elastic)
   pointwise discrepancies.

## 4. Directory and output ownership — no blind migration

Current shared layout remains defined exclusively in
`components/inputs/output_layout.py` and
`components/inputs/output_contract.py`:

```text
<ETABS_EXPORT_ROOT>/
  00_SOURCE_MANIFEST/                     source EDB identity and exact inputs
  01_ETABS_EXPORT/                        ETABS source tables / raw evidence
  02_MODEL/                               model conversion and input variants
  02_GRAVITY/                             gravity run and support comparison
  03_ESM/                                 ESM runs
  04_MODAL/                               modal runs
  05_MRSM/                                response spectrum runs
  06_LINEAR_TIME_HISTORY/                 LTHA runs
  07_NONLINEAR_TIME_HISTORY/              NLTHA runs
  08_ETABS_COMPARISONS/                    cross-solver comparisons
  09_SOFTWARE_DIAGNOSTICS/                 source/dedup/contract audits
  90_UPLOAD_PACKAGES/                     requested/approved evidence ZIPs
```

A new contract-aware run uses
`<stage>/RUNS/<state>/<case>/<unique-run-id>/` with
`00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`,
`04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP`.
The two existing `02_MODEL` and `02_GRAVITY` names are **distinct
historically adopted paths**; no unilateral stage renaming is performed
because it would break saved readers. A numerical folder-prefix
renumbering is a separate tested migration, not a cosmetic edit.

`OpenSees_Analysis_Results` and historical custom output folders remain
readable as **legacy aliases** until their exact producer/consumer
reopen tests pass. Do not create new root-level derived XLSX/CSV/JSON in a
consumer folder or silently duplicate saved evidence.

## 5. Duplicate and inconsistency classification

- **Shadowed definitions:** the same name defined twice in one lexical
  module/class/function scope. This can silently override earlier
  implementations and requires direct inspection/correction.
- **Identical function body across files:** normalized AST fingerprint
  with substantive minimum size, ignoring the function name/docstring.
  A candidate can be intentional compatibility or independent domain
  logic. It is NOT safe to delete based on matching fingerprints alone.
- **Exact file duplicates:** historical archived blobs can be duplicates,
  but are preserved for provenance; a content hash does not establish
  equal runtime role.
- **Versioned workbook literals:** old V10_0–V10_6 references are
  review candidates. Current selection is SHA- and model-based.
- **Writer/reader status:** composed from `audit_live_output_writers.py`
  and `audit_output_writer_reader_pairs.py`; no parallel scanner with
  conflicting output ownership.

## 6. Acceptance gates (explicit, not automatically passed)

| Gate | Evidence required |
|---|---|
| G1 — Active static AST/import/duplicate inventory | Complete CI report, resolved parse errors and triaged shadowed functions |
| G2 — Runtime module integration | Each solver/importer/GUI writer and reader pair reopens a saved run with identical model SHA |
| G3 — ETABS source identity | Actual EDB, current analyzed tables, native assignments and 12 m X-wall geometry verified |
| G4 — Gravity | Full load ledger and **point-by-point** 32/76/97 support comparison; 3,041/768 kN residuals not ignored |
| G5 — ESM/MRSM/NBC | Correct current NBC 105 values, ULS/SLS, spectral periods, scaling and native parity |
| G6 — NLTHA | First-step X-wall solver convergence and independent full-duration M0–M6 evidence |
| G7 — Windows release | Local Python 3.12/Spyder/ETABS v23/OpenSees stack, GUI reopen tests and production output contract |
| G8 — Archive provenance | Historical EDB/workbooks/logs/results unchanged unless explicitly authorized and byte verified |

**Do not mark all modules scientifically verified** from source AST, compilation, test discovery, or fixture-based CI alone. The integrated **static** source audit now passes after an obsolete source-SHA attestation was preserved in a historical ledger and withdrawn from current approval. Engineering, native solver and complete producer/consumer migration gates G2–G8 remain open. See [current integrated audit](../../REVIEW_MAIN/08_SOFTWARE_SECURITY/20261122_INTEGRATED_ENGINEERING_AND_MIGRATION_AUDIT.md).

## 2026-11-22 follow-up: relative-import edge accuracy

The previously reported `module_owner_import_links` omitted relative package imports. `tools/module_import_edges.py` now resolves physical relative modules for both `tools/audit_cross_module_consistency.py` and the output producer/consumer audit, with regression coverage in `tests/test_source_dependency_edges.py`. Regenerate the static reports after merging; prior edge counts are **not comparable**. This is not runtime graph or numerical engineering acceptance. [Full correction and still-open migration gates](../../REVIEW_MAIN/08_SOFTWARE_SECURITY/20261122_RELATIVE_IMPORT_GRAPH_CORRECTION.md).
