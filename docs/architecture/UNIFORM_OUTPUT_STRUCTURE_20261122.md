# Unified project output ownership and migration policy — 2026-11-22

## One model, one export root, one canonical path vocabulary

**Source of truth:** `components/inputs/output_layout.py` provides stage names,
and `components/inputs/output_contract.py` provides the immutable case
manifest, run-folder taxonomy, and safe path/status rules. Module-specific
output ownership must reuse these, not create competing top-level run roots.

```text
<EXACT_SOURCE_EXPORT>/
  00_SOURCE_MANIFEST/             # source EDB identity, private fingerprints
  01_ETABS_EXPORT/                # raw ETABS source extraction and input audits
    00_MANIFEST/                  # canonical private source registrations
    RUNS/SOURCE_ONLY/BEAM_FORCES/<run-id>/
      00_INPUT_SOURCE/CASE_MANIFEST.json
      01_LOGS/
      02_RESULTS/                 # consolidated ETABS beam force CSV + source manifest
      03_EXCEL/
      04_FIGURES/
      05_COMPARISONS/
      06_REVIEW/
      07_EXPORT_ZIP/
  02_MODEL/                       # immutable rebuilt model variants
  02_GRAVITY/
  03_ESM/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
```

Each **new, contract-aware analysis run** uses
`<STAGE>/RUNS/<state>/<case-id>/<unique-run-id>/` with exactly the shared
eight run subfolders. For ESM/MRSM etc, `state` is ULS or SLS as
appropriate. Source-only ETABS imports use `SOURCE_ONLY`, have status
`INCOMPLETE` rather than implying solver completion, and never claim
structural equivalence. Stage-specific auxiliary directories remain distinct.

## Ownership, naming and consistency requirements

| Concern | Rule |
|---|---|
| Unique run | Never silently overwrite previous solver/evidence directories |
| Case names | Windows-safe `safe_component`; prohibit path traversal and reserved names |
| Source authority | Record original EDB and model SHA-256 where available; never infer from filename |
| Units | Explicit kN-m-s or kN-mm-s, no silent unit conversion |
| Status | Solver completion, source interpretation and engineering acceptance are distinct |
| Outputs | CSV/JSON numerical results in `02_RESULTS`; optional workbooks in `03_EXCEL`; figures in `04_FIGURES` |
| Comparison | Matched ETABS/OpenSees evidence in `05_COMPARISONS`, never a source-only result folder |
| Review | Issue-by-issue rationale, evidence and open-gate reports in `06_REVIEW` |
| Upload | Export ZIP packages under `07_EXPORT_ZIP`; private source spreadsheets and EDB remain local |
| Logs | Time-stamped workflow/solver logs in `01_LOGS` |
| Navigation | Canonical indices and registries; do not duplicate or silently overwrite historical sources |

**Current implementation scope:** the ETABS beam-force GUI producer has
been redirected to the shared contract. Other active producers already
using `create_case_run` retain their behavior. Remaining historical or
bespoke writers are **not** restructured automatically: native result
consumers may rely on their existing paths. Any migration must update
writers, readers, saved references and regression tests together.

## Metadata-only audit

```powershell
python tools/audit_uniform_output_structure.py --export-root "D:\Thesis Opensees\ETABS 11-22-2026" --output "D:\Thesis Opensees\ETABS 11-22-2026\09_SOFTWARE_DIAGNOSTICS\output_structure_audit.json"
```

Reports stage presence, case-manifest validity, historical path presence,
noncanonical or incomplete run directories, loose root-level **and stage-level** CSV/JSON/Excel/ZIP/plot artifacts requiring ownership review, and recorded engineering
status. It **never** relocates files, interprets solver equations, reads
source XLSX/EDB contents, or changes analysis files. Private names/paths
are not published to GitHub automatically. An explicit local execution
is still required to audit the user's Windows output folder.

## Unresolved production-wide migration gates

1. Inventory every active producer/consumer of
   `OpenSees_Analysis_Results`, nested `02_MODEL` rebuilds and custom
   root-level Excel/JSON/HTML outputs.
2. Establish actual per-module writer/reader matching with saved-case
   reopen tests on existing user artifacts.
3. Move only new outputs to canonical folders; preserve historical files,
   references and backward-compatible readers.
4. Reconcile private source hashing and current 12 m X-wall geometry
   independently; a folder name or copied workbook is not valid evidence.
5. Verify on Windows ETABS and OpenSees with at least one full native
   case per stage and 32/76/97 support strategy where applicable.

**Engineering acceptance remains open.** This document defines software
organization and evidence handling, not NBC 105, structural equivalence or
nonlinear convergence approval.

## Enforcement added to main

- `tests/test_uniform_output_structure.py`: exercises stage names and
  manifests for ETABS, Gravity, ESM, Modal, MRSM, LTHA and NLTHA;
  verifies legacy preservation, missing-manifest detection and root artifact
  inventory without moving files.
- `tests/test_gravity_beam_force_gui_integration.py`: checks the active
  GUI creates SOURCE_ONLY beam runs using the shared contract, verifies the
  EDB fingerprint and records source-validation errors explicitly.
- `.github/workflows/repository-integrity.yml`: runs these tests.

**Execution evidence:** changes are committed, but live GitHub Actions
success and private Windows output inspection were not independently
verified during this edit. Do not claim that every historical module writer
has already migrated solely because the shared policy and tests exist.

## 2026-11-22 comprehensive producer/consumer evidence (implemented)

`tools/audit_live_output_writers.py` inventories **both potential
readers and writers**, using AST rather than trying to infer ownership from
filenames. `tools/audit_output_writer_reader_pairs.py` scans *every active
Python source file* and associates possible read/write sites with the owning
module. The source/line references, import edges and unresolved statuses
are **static review candidates**, not proof of actual runtime file use.

The complete owner matrix can be generated with:

```powershell
python tools/audit_output_writer_reader_pairs.py --repo . --report-dir "audit/output_pairs" --fail-on-parse
```

The canonical read-only all-module Windows audit is:

```powershell
python tools/RUN_FULL_OUTPUT_MIGRATION_AUDIT.py --export-root "D:\\Thesis Opensees\\ETABS 11-22-2026"
```

That command inventories all active code, all nested real output-file
metadata, canonical/legacy run manifests and stage ownership; it publishes a
new source-only report under
`09_SOFTWARE_DIAGNOSTICS/RUNS/SOURCE_ONLY/ALL_MODULE_OUTPUT_MIGRATION_AUDIT/<run-id>/02_RESULTS`.
The tool does **not** silently copy, delete, migrate or rewrite existing
artifacts and does **not** run ETABS/OpenSees. The return code is 2 while
producer-consumer evidence or layout acceptance remains open; this is
intentional, not a completed migration flag.

`components/validation/etabs_comparison.py` now discovers native
GRAVITY/ESM/MODAL/MRSM/LTHA/NLTHA stage roots as well as the historical
shared result tree, retaining strict model-hash and limit-state filtering.

The Windows GitHub Action
`.github/workflows/windows-output-contracts.yml` runs direct Python
filesystem and reader regressions on a hosted Windows VM. It cannot
execute private ETABS COM, Spyder GUI, or native 32/76/97 comparisons.

**Unfinished:** A complete all-module migration requires verifying every
actual live writer/reader pair and its saved-case reopen contract on matching
native Windows model data. No automatic bulk relocation is authorized in
the absence of source identity and numerical parity checks.


## 2026-11-26 — complete local inventory and optional deep format audit

`python tools/RUN_FULL_OUTPUT_MIGRATION_AUDIT.py --export-root <case> --hash-duplicates --validate-files` now records every enumerated file path in `05_ALL_OUTPUT_FILE_INVENTORY.json`, not just the largest 50. SHA duplicate groups are report-only. Optional format checks parse JSON/JSONL, read UTF-8 text/CSV/logs, check ZIP/Office container CRC and workbook XML presence, and PNG signatures. They do not validate Excel formulas or numerical data, render images, execute archive members, or evaluate engineering acceptance. Errors are counted in the summary and cause a review-required CLI exit. Run only when other writers are idle. Main GUI Results exposes the same local audit; originals remain untouched. The selected model folder resolves to its owning export root.


The all-module file audit distinguishes archive CRC integrity, embedded evidence parse failures, workbook formula-cache availability, and engineering acceptance. Formula-only exports need Excel recalculation or independently sourced numerical evidence before cached-value readers can use them. Nothing is recalculated or overwritten by the audit; nested ZIPs and oversized embedded workbooks are explicit review items.
