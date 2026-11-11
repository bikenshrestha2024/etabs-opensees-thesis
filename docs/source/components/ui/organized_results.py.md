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
files, old ZIPs and prior generated snapshots are excluded. Other saved logs,
JSON, scripts, graphics, tables, CSV, PDF and Excel documents are included.
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
