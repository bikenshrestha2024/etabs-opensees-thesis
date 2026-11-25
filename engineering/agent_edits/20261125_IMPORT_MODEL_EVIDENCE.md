# Import and Model evidence handoff

Editor OpenAI Codex desktop. Base `1ff7053d30591936b4566df5aa5aeb42d5f03a01`. Extended the existing Import and Model callbacks, mapping workbook exporter and area-evidence publisher. Checked the existing area evidence and tolerance changes before editing. New source files are unnecessary.

Regressions exercise the selected folder, an active Import worker, a switched folder during worker completion, workbook snapshot preservation, stale area source/configuration/mapping, and a wall-only run beside an existing floor. Full pytest passed 1,905 tests and 824 subtests, with 44 skipped. Windows Tk exercised the main Import-to-Model callback and the Area source-evidence dialog. A native OpenSeesPy smoke test created one synthetic ShellMITC4 and packaged its source-bound report. Native ETABS/OpenSees equivalence and project NLTHA remain unverified.

The source EDB, exported mesh, support classification, gravity factors, seismic mass, material assignments and analysis tolerance are preserved. Project-specific evidence remains in the local case folders.
