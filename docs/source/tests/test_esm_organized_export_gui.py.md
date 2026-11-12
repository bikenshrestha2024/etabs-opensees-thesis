# Static ESM combined-export GUI safety regression

**What:** tests/test_esm_organized_export_gui.py checks module-separated categorized file copies, Excel workbook, SHA manifest, unchanged original files, invalid input, map JSON type and UI actions.

**Why:** Regression protection for copy-only export and accurate engineering status.

**How:** Python unittest + openpyxl with synthetic files. No ETABS, OpenSees or Tk display. Run python -m unittest discover -s tests -p test_esm_organized_export_gui.py -v.

**When:** Before merging ESM GUI or exporter code.

**Where:** tests/test_esm_organized_export_gui.py, components/equivalent_static/organized_exports.py, components/validation/etabs_direct_api.py.

**Who:** Software maintainer verifies CI and real Windows workflow; engineering reviewer checks case values. Static tests are NOT native solver or code acceptance.
