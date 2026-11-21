"""Pure helpers of tools/etabs_comparison_ablation.py (no solver)."""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import etabs_comparison_ablation as T  # noqa: E402


def _reference(tmp_path):
    path = tmp_path / "support.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["status", "etabs_point", "opensees_node", "x_m", "y_m", "etabs_global_rz_kN"])
        w.writerow(["MATCHED_GLOBAL_Z", "1", "4", "0", "6", "100"])
        w.writerow(["MATCHED_GLOBAL_Z", "263", "24", "12", "6", "300"])
        w.writerow(["UNMATCHED_ETABS", "9", "", "", "", "0"])
    return T.read_etabs_reference(path)


def test_compare_reactions_statistics_and_groups(tmp_path):
    ref = _reference(tmp_path)
    rows, s = T.compare_reactions({4: 130.0, 24: 270.0}, ref)
    assert [r["group"] for r in rows] == ["PERIMETER", "CORE"]
    assert s["max_abs_diff_kN"] == pytest.approx(30.0)
    assert s["rms_diff_kN"] == pytest.approx(30.0)
    assert s["core_opensees_kN"] == 270.0 and s["perimeter_etabs_kN"] == 100.0
    assert s["total_opensees_kN"] == pytest.approx(s["total_etabs_kN"])
    with pytest.raises(ValueError, match="lacks reactions"):
        T.compare_reactions({4: 1.0}, ref)


def test_merge_config_replaces_and_deletes_without_mutating():
    base = {"a": {"x": 1}, "b": 2}
    out = T.merge_config(base, {"a": {"y": 3}, "b": None, "c": 4})
    assert out == {"a": {"y": 3}, "c": 4} and base == {"a": {"x": 1}, "b": 2}


def test_runner_sources_load_without_tkinter():
    src = T._runner_source_function()("m.py", "r.json", [1, 2], 10.0, 5)
    assert "run_gravity_stage" in src and "SUPPORT_NODES = [1, 2]" in src
    modal = T._modal_runner_source_function()("m.py", ".", 12, "PythonSparse", None, None, None)
    assert "run_nbc105_modal_audit" in modal


def test_first_translational_modes_pick_lowest_dominant_mode():
    rows = [dict(mode=1, period_s=2.4, UX_participation_percent=0.1, UY_participation_percent=65.0,
                 RZ_participation_percent=0.0),
            dict(mode=2, period_s=1.6, UX_participation_percent=60.0, UY_participation_percent=0.0,
                 RZ_participation_percent=5.0)]
    out = T.first_translational_modes({"rows": rows})
    assert out["Y"]["mode"] == 1 and out["X"]["period_s"] == 1.6


def test_lump_wall_base_reactions_by_linear_edge_weights():
    ref = {1: dict(point="A", x=6.0, y=6.0, etabs_kN=0.0), 2: dict(point="B", x=8.0, y=6.0, etabs_kN=0.0),
           3: dict(point="C", x=0.0, y=0.0, etabs_kN=0.0)}
    reactions = {1: 10.0, 2: 20.0, 3: 5.0, 9: 100.0}
    coords = {9: (6.5, 6.0, 0.0)}
    out, audit = T.lump_to_reference_supports(reactions, coords, ref)
    assert out[1] == pytest.approx(85.0) and out[2] == pytest.approx(45.0) and out[3] == 5.0
    assert sum(out.values()) == pytest.approx(sum(reactions.values()))
    assert audit["lumped_node_count"] == 1
    with pytest.raises(ValueError, match="no edge"):
        T.lump_to_reference_supports({7: 1.0}, {7: (3.0, 1.0, 0.0)}, ref)
