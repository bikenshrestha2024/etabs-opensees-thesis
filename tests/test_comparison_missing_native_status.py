"""Missing native ETABS values are explicit, never silently zero-filled.

[REF docs/source/components/validation/etabs_comparison.py.md]
Synthetic rows only, no ETABS COM or Tk display.
"""
from components.validation.etabs_comparison import comparison_display_rows


def _open_row():
    return {"method": "MRSM", "limit_state": "ULS", "case": "X_E0",
            "axis": "X", "location": "BASE", "metric": "base_shear",
            "unit": "kN", "basis": "CQC_force_scaled", "value": 29849.6}


def test_no_native_csv_shows_missing_evidence_not_empty_status():
    source = _open_row()
    rows = comparison_display_rows([source], native_loaded=False)
    assert source == _open_row()  # No input mutation
    assert len(rows) == 1
    assert rows[0]["value"] == 29849.6
    assert rows[0]["etabs_value"] is None
    assert rows[0]["percent_difference"] is None
    assert rows[0]["status"] == "ETABS_DATA_NOT_LOADED"
    assert "Direct ETABS API" in rows[0]["note"]


def test_loaded_unmatched_reference_retains_engineering_comparison_status():
    source = {**_open_row(), "etabs_value": None,
              "status": "MISSING_ETABS", "note": "No exact normalized key"}
    assert comparison_display_rows([source], native_loaded=True) == [source]


def test_existing_matched_etabs_value_is_never_hidden():
    source = {**_open_row(), "etabs_value": 29500.0,
              "status": "NOT_COMPARABLE", "percent_difference": 1.18}
    assert comparison_display_rows([source], native_loaded=False) == [source]
