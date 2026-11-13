# Short main launcher — static regression

**Source:** `tests/test_main_launcher_short_alias.py`. Tests the `01_MAIN_GUI.py` → `01.py` → `RUN_ETABS_TO_OPENSEES.py` chain and retained compatibility modules. No ETABS, Tk desktop or solver is invoked. Run with `python -m unittest discover -s tests -p 'test_main_launcher_short_alias.py' -v`.

The new launcher does not change load combinations, mesh, units, materials or analysis stages, and it does not establish numerical/engineering acceptance. A Windows/Spyder smoke test is still required.
