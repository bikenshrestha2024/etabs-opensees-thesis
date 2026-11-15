# src/etabs_adapter/bridge.py — lazy existing-implementation lookup

**Source:** `src/etabs_adapter/bridge.py`. Functions: `available_existing_adapters()` returns symbolic routes without importing ETABS; `existing_adapter(name)` validates the name and lazily resolves a callable using `import_module`. Declared routes are `native_quantity` → `components.validation.etabs_native_quantity_tables.export_native_quantity_tables`, `eq_pdelta` → `components.validation.etabs_eq_pdelta_native_extract.export_eq_pdelta_native_evidence`, `project_workbook` → `components.inputs.project_workbooks.source_limit_state`.

**Engineering boundary:** No source EDB is modified by the bridge itself. The target routine controls its own side effects and needs separate source/permission review. No neutral model converter or native full-building import is implemented here. `tests/verify_etabs_adapter_boundary.py` checks that the referenced sources and function names exist; this is not an ETABS OAPI execution test.
