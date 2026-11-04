# ESM wall-area and ULS/SLS period provenance regression

Source: `tests/verify_esm_aw_period_provenance.py`.

This is a **synthetic software regression suite**; it does not inspect a real ETABS model, execute OpenSees or establish NBC compliance.

- Checks portable Windows .EDB source identification in scaling workbook discovery.
- Rejects a similarly named scaling workbook whose actual `SCALING SUMMARY!B4` points to another EDB.
- Requires explicit opt-in for non-Rayleigh adopted-period workbook references and rejects stale reference values when selected directional Aw has changed.
- Checks separate case-specific Rayleigh inputs for ULS/SLS (different stiffness configurations); missing SLS evidence must block combined calculation.
- Checks the NBC 105:2025 §5.1 directional empirical period and min(Rayleigh, 1.25 times empirical) are applied to the **matching limit state**.

Test command (conda-forge Python environment with openpyxl):
```powershell
python -m unittest tests.verify_esm_aw_period_provenance -v
python tests/verify_nbc105_periods.py
python tests/verify_esm_input_loader.py
python tests/verify_esm_source_selection.py
python tests/verify_esm_partial_input.py
```

No claim of successful local test execution is made by this documentation. GitHub CI results should be checked independently. For source engineering validation, compare input Aw segments (direction, wall Lwi, thickness, first-story extent and openings), matched ETABS ULS/SLS stiffness models, site classification, period outputs and base shear against the actual ETABS export. Do not put private exports into this public GitHub repository.
