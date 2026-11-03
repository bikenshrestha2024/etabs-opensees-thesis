# JSON documentation strategy — 2026-11-03

**Baseline count:** 503 tracked JSON files in Git tree `869dc4d98440ea2be5d5e99821692a12b7ac501e` (before the addition of paper specimen register and subsequent new JSONs may change total).

- [All tracked JSON paths](00_TRACKED_JSON_INVENTORY.md) records source path, size, Git blob SHA and functional category for each JSON.
- Run `python tools/build_json_documentation.py` from the repository checkout. The script parses **every JSON** directly and writes one observed field/type guide per file to `docs/json/files/<source>.json.md` and `docs/json/00_ALL_JSON_FILES.md`.
- The generator does not mutate JSON source files, cannot infer undocumented units or specimen calibration, and runs entirely offline. It protects sensitive research inputs from external transmission.
- Run `python tools/build_json_documentation.py --check` after generating to identify stale pages.
- Examples of important families: ETABS geometry/section/mass/load audits; project and run configurations; Research_Components and Material_Catalog parameter cards; ground-motion metadata; validation/verification summaries; historical Saved_Project_V156 files and Worked_Example snapshots.
- **WARNING:** A historical output JSON is not automatically a current model input. Source SHA, code revision and record case ID must match before reuse.

The generated field tables are observational, not normative JSON Schema with formal constraints. Further engineering review is needed for parameter units, admissible ranges, lineage and physical validity.
