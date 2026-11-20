# ETABS ingestion hardening (Task 3)

Editor Claude Code (model label UNKNOWN). Base `ea6339b1b99e852747b646e9ef405fb42c147d37`, branch `feat/nltha-readiness-gate-20261120`.

Pure guards (working-copy helper, SetPresentUnits read-back, dropped-point accounting) were appended to the existing non-GUI `components/validation/gravity_etabs_direct.py`; `components/ui/application.py` keeps thin call sites (`_connect_etabs`, `_point_coords`, diaphragm loop, cleanup in `convert_model` finally). `components/model/assembly.py` `_material_table` now records skipped material rows in `assembly_errors`. Tests: `tests/test_etabs_ingest_guards.py` (fake sap, headless).

Native ETABS COM behaviour (OpenFile on the copy, GetPresentUnits read-back, side-file cleanup on Windows) is PENDING. No solver PASS is claimed as engineering acceptance.
