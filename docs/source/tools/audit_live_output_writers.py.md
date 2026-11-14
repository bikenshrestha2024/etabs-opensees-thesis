# Repository-wide output writer and path-inventory audit

Source: [audit_live_output_writers.py](../../../tools/audit_live_output_writers.py)

## Purpose

Inventory potential output writers and literal legacy paths in *active* Python
sources without running an ETABS/OpenSees model or modifying historical outputs.
The scanner reads repository-root Python launchers and Python files under
`components/` and `tools/`. It intentionally excludes tests, literature PDFs,
historical snapshots and generated model results from the active-writer list.

The method parses Python AST rather than grepping prose; calls to
`Path.write_text`, `write_bytes`, `mkdir`, `save`, `savefig`,
`to_excel`, `to_csv`, `to_json`, `json.dump`, file `open`
in a literal write/append mode, and related file-writing methods are flagged as
**possible** writers. Literal references to canonical stage names and known
legacy output paths are recorded with file/line number and exact source-file SHA256.

These results are a navigation index, not a call graph or proof that a function
is executed, and not a certification that files are organized, engineering values
are correct, or all live writers have migrated. Dynamic paths and indirect calls
cannot reliably be classified statically. False positives include writing to an
in-memory buffer. A legacy literal may be a compatibility reader or warning.

## Commands

Read-only from the checked-out repository:

```powershell
python tools/audit_live_output_writers.py --repo .
```

Write a structured report to the selected ETABS export:

```powershell
python tools/audit_live_output_writers.py --repo . --export "D:\Thesis Opensees\ETABS 11-14-2026\3" --write
```

Only `--write` creates local report artifacts; `--export` is required with it:

```text
<EXPORT>/
  09_SOFTWARE_DIAGNOSTICS/
    WRITER_AUDITS/
      RUNS/
        <UTC>/
          JSON/Writer_Audit.json
          CSV/Writer_References.csv
          REPORT/READ_FIRST.md
```

The JSON contains source-relative file paths, exact source-byte hashes, literal
path markers and line numbers. The writer does not alter original EDB, Excel,
solver files, regression data or any historical reports. The saved JSON omits
the absolute repository path.

## Prioritization

Use `legacy_literal_occurrences` to select candidate modules. Trace each
module's actual writer, saved manifest, result reader, GUI callbacks, plotter,
Excel and ZIP publication, and model/case identity before migrating its output
location. Where a legacy writer must remain temporarily, retain explicit
compatibility readers and source-matched hashes; never bulk-move prior results.

The analysis must be followed by native Windows ETABS/OpenSees comparison.
Global gravity reaction equilibrium is not individual foundation equivalence.
MESH_04/08/16 shell–beam–wall load transfer, brace releases, stiffness, floor
inertia, initial P-Delta, nonlinear wall parameters, and complete NLTHA
remain separate engineering acceptance gates.

Validation: `tests/test_deep_output_inventory_v16.py` and
`.github/workflows/deep-output-audit.yml`.
