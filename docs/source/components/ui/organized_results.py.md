# Organized result snapshots and ZIP archives

Source: [organized_results.py](../../../../components/ui/organized_results.py)

## Purpose

Produce a **new**, timestamped, reviewable artifact tree without moving,
renaming, deleting or rewriting existing solver output. The existing gravity
case registry, ESM runners, modal cache, MRSM report readers and saved GUI
paths remain active. The organizer verifies every snapshot copy with SHA256.

## Structure

```text
<existing analysis_output_folder>/
  Organized_Results/
    LATEST_ORGANIZED_RESULT.txt
    <YYYYMMDD_HHMMSS_microseconds>/
      Gravity/
      ESM/
      Modal/
      MRSM/
      Comparisons/
      Unclassified/
      EVIDENCE_MANIFEST.json
      README_FIRST.txt
      ZIP_Exports/
        Gravity_Review_UPLOAD.zip
        ESM_Review_UPLOAD.zip
        Modal_Review_UPLOAD.zip
        MRSM_Review_UPLOAD.zip
        Comparisons_Review_UPLOAD.zip
        Unclassified_Review_UPLOAD.zip
        ALL_MODULES_Review_UPLOAD.zip
```

Each category retains an `Analysis/` or `GravityGUI/` subdirectory and
the original relative path; thus a ULS MRSM folder, case name, report and
node response remain distinguishable. An archive is created only for a
nonempty category. The combined archive contains all included categories.

Files such as `.edb`, `.bak`, lock files, unfinished processing-sidecar
files, old ZIPs and prior generated snapshots are excluded. As of V15,
source-manifest/ETABS-export and software-diagnostic directories, known private
manifests, and recognizable original-source workbooks are also excluded.
Other saved logs, JSON, scripts, graphics, tables, CSV, PDF and generated Excel
reports may be included, but **manual privacy review is still required**:
unknown secret-bearing filenames or log payloads cannot be proven safe by a
filename-only classifier. Never publish an archive without reviewing its manifest.
The manifest identifies the original absolute source path, module assignment,
original size and SHA256 for each included file. It also logs skipped
unclassified evidence if that optional exclusion is requested.

## Validation and limitations

These are forensic **copies**. They do not establish agreement between ETABS
and OpenSees, nor verify a native ETABS response, accepted first-storey
`Aw`, or NBC 105:2025 compliance. A missing SLS run is not reconstructed.
The source `.EDB` remains local and is not placed in upload ZIPs.
The independent native source and solver results must be reconciled before
design certification.

The method classifier is a filename/folder organizer only. It does not infer
model identity or case compatibility from names. Engineering equality checks
continue using existing case fingerprints and comparison gates.

Use `publish_organized_results(<existing results folder>,
gravity_root=<optional separate gravity GUI folder>)`; it returns the
exact ZIP and manifest paths. The new snapshot and archives require additional
disk space. Preserve original files for reproducibility.

Test: `tests/test_organized_results.py`.


## 2026-11-14 gravity-only review mode
The generic `publish_organized_results` still uses the legacy all-module snapshot directory and `ALL_MODULES` ZIP by default, preserving ESM/MRSM callers. New opt-in keyword arguments:
- `destination_parent`: specific case-specific snapshot root, e.g. `<ETABS export>/02_GRAVITY/REVIEW_SNAPSHOTS`.
- `selected_modules`: strict subset of `MODULES`; the gravity GUI requests only `Gravity` and `Comparisons`.
- `bundle_name`: independent archive label, `GRAVITY_REVIEW` in gravity GUI. Existing calls default to `ALL_MODULES`.

The gravity GUI determines the ETABS export root from the selected results directory's `OpenSees_Analysis_Results` ancestor, or falls back to a `REVIEW_SNAPSHOTS` child of its selected output root. Historical solvers and evidence remain in their original paths. SHA256-checked immutable copies are produced and prior `REVIEW_SNAPSHOTS` folders are excluded from rescanning. This is a **review snapshot output fix**, not yet the migration of all upstream gravity producer and downstream reader paths. 

Users should receive a `GRAVITY_REVIEW_Review_UPLOAD.zip` under `02_GRAVITY/REVIEW_SNAPSHOTS/<timestamp>/ZIP_Exports/` and a pointer at `02_GRAVITY/REVIEW_SNAPSHOTS/LATEST_ORGANIZED_RESULT.txt`. Sources may still be in legacy output directories until all module readers are migrated with regression tests. Non-gravity ESM, MRSM and modal reports should be published from their own module actions, not bundled by a gravity button.

**Acceptance:** Run `python -m unittest tests.test_organized_results` and current CI; then perform GUI smoke tests on Windows. Comparing total support reactions or packaging reports is not proof of native ETABS/OpenSees equivalence.


## Deep output integrity V15

The classifier now assigns ownership from canonical stage directory paths (`02_MODEL`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`) **before** reading ambiguous filenames. Source identity is still validated separately by native evidence code. A custom `destination_parent` inside the source tree is excluded from the scan, including older siblings: avoid feeding previously packaged results into new ZIPs. A separately supplied gravity directory already nested in the chosen source is not scanned again. The central `safe_component` validator rejects unsafe bundle names and Windows reserved devices before any new directory is made.

This does **not** convert the historical all-module publisher into a canonical writer for every analysis stage. It remains a read-only forensic snapshot tool; each live solver writer/reader pair must migrate separately. Tests: `test_organized_results.py` and `test_unified_output_contract.py`.

### V15 upload-manifest path privacy

The complete local `EVIDENCE_MANIFEST.json` retains absolute source paths for native provenance review. The **ZIP-internal** `EVIDENCE_MANIFEST.json` now replaces local absolute directory/file paths with `<REDACTED_LOCAL_PATH>`, while retaining archive relative snapshot paths, SHA256 and file sizes. It adds `source_path_policy=LOCAL_PATHS_REDACTED_FOR_UPLOAD_ZIP`. A subset ZIP contains only manifest entries for that subset. **Payloads are not scanned or sanitized**: run a private-data/secrets review of scripts, JSON, CSV, workbooks and logs before uploading to a public destination.


## 2026-11-15 transaction preflight and path-integrity follow-up

The snapshot generator now inventories and SHA256-fingerprints **all eligible source files before it creates the dated destination**. No classifiable files means no empty `Organized_Results/<timestamp>` run or new latest pointer. Source and optional gravity roots, explicit destination parent and `LATEST_ORGANIZED_RESULT.txt` are rejected if their original paths or ancestors are symbolic links, before `resolve()` could hide redirection. After each snapshot copy, the archived bytes and re-read source must both match the original preflight hash: a result that mutates during the copy is not certified as immutable evidence, and `LATEST_ORGANIZED_RESULT.txt` is not advanced when copy validation fails. Newly-created incomplete snapshots may remain as diagnostic evidence but are not presented as latest results.

`tests/test_organized_results.py` includes no-eligible-files, source-mutation-during-copy and linked selected source/pointer regressions. This is still a file-evidence publisher, not a full multi-file atomic transaction, native solver proof, sensitive-payload scanner or 3D gravity/earthquake equivalence check. Review ZIP payloads manually before public uploads.
