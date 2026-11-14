"""Deterministic label tests: no native solver/ETABS renumbering."""
import pytest
from components.model.display_ids import display_label, build_labels


def test_storey_examples():
    assert display_label("N", 0, 1) == "N1"
    assert display_label("N", 1, 1) == "N101"
    assert display_label("N", 2, 2) == "N202"
    assert display_label("B", 7, 1) == "B701"
    assert display_label("C", 25, 1) == "C2501"
    assert display_label("SW", 25, 1) == "SW2501"


def test_overflow_never_collides_with_next_storey():
    assert display_label("N", 1, 99) == "N199"
    assert display_label("N", 1, 100) == "N-S01-0100"
    assert display_label("N", 2, 1) == "N201"


def test_deterministic_and_native_ids_preserved():
    rows = [
        {"native_id": 900, "storey": 1, "category": "BEAM"},
        {"native_id": 450, "storey": 1, "category": "BEAM"},
        {"native_id": 2, "storey": 0, "category": "NODE"},
    ]
    original = [dict(r) for r in rows]
    assert build_labels(rows) == build_labels(list(reversed(rows)))
    assert build_labels(rows) == {"2": "N1", "450": "B101", "900": "B102"}
    assert rows == original


def test_fail_closed_unknown_classification_and_duplicates():
    with pytest.raises(ValueError, match="Unclassified"):
        build_labels([{"native_id": 1, "storey": 3, "category": "OUTRIGGER"}])
    with pytest.raises(ValueError, match="Duplicate native"):
        build_labels([{"native_id": 1, "storey": 1, "category": "NODE"},
                      {"native_id": 1, "storey": 2, "category": "NODE"}])
    with pytest.raises(ValueError):
        display_label("N", -1, 1)
