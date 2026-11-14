# Gravity evidence staging and material Excel — 2026-11-14

**Scope:** Locally stage the original ETABS assignment XLSX and the third-storey ULS compressed full export XLSX, without modifying either file, and provide a direct material/section Excel export.

**Code:** components/inputs/gravity_evidence_stage.py, components/gravity/gui_and_reports.py, 08_EXPORT_MATERIAL_SECTION_LIBRARY.py.

## Procedure
1. Choose the current OpenSees_Complete_Gravity_Model.py in Gravity Analysis. Browse for BOTH the original assignment and compressed full ETABS table XLSX files.
2. Click **Stage BOTH selected ETABS XLSX files locally (SHA256, no LFS)**. Copies are written to 01_ETABS_EXPORT/10_PRIVATE_ETABS_WORKBOOKS and an atomic gravity_evidence_manifest.json records absolute paths, bytes, source file names and SHA256.
3. When source EDB is specified and locally present, its SHA256 is recorded. Manifest reloading rejects changed EDB or changed staged Excel files.
4. A missing optional registered Git-LFS workbook no longer triggers a mandatory modal picker during ordinary OpenSees gravity GUI auto-selection. It must still be supplied for any explicit ETABS comparison requiring it.
5. Material/section source Excel is accessible from current components/ui/results.py (Export / open complete Excel library). If Windows is loading an older V116 runtime, use: python 08_EXPORT_MATERIAL_SECTION_LIBRARY.py "D:/Thesis Opensees/ETABS 11-14-2026/1". It exports under 02_MODEL/MATERIAL_SECTION_LIBRARY.

## Boundary of validation
- Excel XLSX is itself an OOXML ZIP container; the staging helper validates ZIP format and CRC but does not change the data or formatting.
- A file-level SHA does not establish that assignment and analysis workbooks came from the same ETABS EDB. Verify native sheet names, actual assigned sections/end offsets, completed ULS Joint Reactions, ETABS case, and source identity independently.
- STAGED_NOT_ETABS_VALIDATED explicitly means source evidence staging only, not ETABS/OpenSees force, gravity, seismic mass or nonlinear acceptance.
- No solver, ETABS COM or original EDB is run or changed by staging.
- Workbooks are sensitive project evidence. The private staging directory is in .gitignore; do not upload the source XLSX or private manifest to the public repository.

## Tests and reference
Run python -m pytest tests/test_gravity_evidence_stage.py -q. Native tests are not claimed as executed.
OpenSees ShellMITC4: https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html
ETABS frame release documentation: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Releases_and_Partial_Fixity.htm