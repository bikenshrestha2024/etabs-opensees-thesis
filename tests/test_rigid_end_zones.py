"""Deterministic tests for opt-in ETABS rigid end zones and the comparison preset."""
import json

import pytest

from components.model.elastic_conversion_settings import compile_settings
from components.model.etabs_comparison_preset import (
    ETABS_ELASTIC_GRAVITY_COMPARISON, apply_preset, preset_settings)
from components.model.rigid_end_zones import (
    SHEET, inject_end_offsets, read_end_offsets_metadata, read_end_offsets_workbook,
    resolve_end_offsets, validate_rigid_end_zone_config)


def _frame(obj="515", start=0., end=1.5, total=6.0, hinged=False):
    return dict(object=obj, category="BEAM", start=start, end=end, length=end - start,
                hinged_brace=hinged, basis=((1., 0., 0.), (0., 1., 0.), (0., 0., 1.)),
                properties={"section": "Beam 600*800", "A": .48, "J": .031102, "Iy": .0144,
                            "Iz": .0256, "E": 33541020., "G": 13975430.})


def _beam(obj="515"):
    return [_frame(obj, 0., 1.5), _frame(obj, 1.5, 4.5), _frame(obj, 4.5, 6.0)]


def _workbook(tmp_path, rows, unit="mm"):
    from openpyxl import Workbook
    book = Workbook()
    sheet = book.active
    sheet.title = SHEET
    sheet.append(["TABLE:  Frame Assignments - End Length Offsets"])
    sheet.append(["Story", "Label", "UniqueName", "Offset Option", "Offset I", "Offset J",
                  "Rigid Factor", "Self Weight Option"])
    sheet.append(["", "", "", "", unit, unit, None, ""])
    for row in rows:
        sheet.append(row)
    path = tmp_path / "assign.xlsx"
    book.save(path)
    return path


META = {"frames": {"515": {"GetEndLengthOffset": [True, .55, .625, 1.0, 0]},
                   "900": {"GetEndLengthOffset": [True, 0., 0., 1.0, 0]}}}


def test_workbook_reader_converts_mm_and_checks_columns(tmp_path):
    path = _workbook(tmp_path, [["Story25", "B1", "515", "Auto", 550, 625, 1, "Auto"],
                                ["Base", "L1", "900", "Auto", 0, 0, 1, "Auto"]])
    records = read_end_offsets_workbook(path)
    assert records["515"] == dict(option="Auto", i_m=pytest.approx(.55), j_m=pytest.approx(.625),
                                  rigid_factor=1.0)
    assert records["900"]["i_m"] == 0.0
    bad = _workbook(tmp_path, [["S", "B1", "515", "Auto", 550, 625, 1.5, "Auto"]])
    with pytest.raises(ValueError, match="Rigid Factor > 1"):
        read_end_offsets_workbook(bad)


def test_metadata_reader_matches_workbook_shape():
    records = read_end_offsets_metadata(META)
    assert records["515"]["j_m"] == .625 and records["515"]["option"] == "Auto"


def test_config_absent_or_disabled_is_none_and_unknown_keys_raise():
    assert validate_rigid_end_zone_config(None) is None
    assert validate_rigid_end_zone_config({"enabled": False}) is None
    with pytest.raises(ValueError, match="unknown keys"):
        validate_rigid_end_zone_config({"enabled": True, "rigid": 1})
    with pytest.raises(ValueError, match="<= 1"):
        validate_rigid_end_zone_config({"enabled": True, "factor": 1.2})
    with pytest.raises(ValueError, match="boolean"):
        validate_rigid_end_zone_config({"enabled": "yes"})


def test_resolve_from_workbook_cross_checks_metadata_and_drops_zero_zones(tmp_path):
    path = _workbook(tmp_path, [["S", "B1", "515", "Auto", 550, 625, 1, "Auto"],
                                ["S", "L1", "900", "Auto", 0, 0, 1, "Auto"]])
    frames = _beam() + [_frame("900", 0., 3.8)]
    offsets, audit = resolve_end_offsets({"enabled": True}, frames, metadata=META,
                                         default_workbook=str(path))
    assert offsets == {"515": {"i": pytest.approx(.55), "j": pytest.approx(.625),
                               "rigid_fraction": 1.0}}
    assert audit["frames_with_rigid_zone"] == 1 and audit["workbook_vs_metadata_mismatch_count"] == 0
    assert audit["total_rigid_length_m"] == pytest.approx(1.175)


def test_factor_override_hinged_brace_and_missing_record():
    offsets, audit = resolve_end_offsets({"enabled": True, "source": "SOURCE_METADATA", "factor": .5},
                                         _beam(), metadata=META)
    assert offsets["515"]["rigid_fraction"] == .5 and audit["frames_rigid_factor_overridden"] == 1
    with pytest.raises(ValueError, match="hinged brace"):
        resolve_end_offsets({"enabled": True, "source": "SOURCE_METADATA"},
                            [_frame("515", hinged=True)], metadata=META)
    with pytest.raises(ValueError, match="lack an end-offset"):
        resolve_end_offsets({"enabled": True, "source": "SOURCE_METADATA"},
                            [_frame("777")], metadata=META)
    with pytest.raises(ValueError, match="workbook_path"):
        resolve_end_offsets({"enabled": True}, _beam(), metadata=META)


def test_inject_and_compile_place_rigid_offsets_only_on_outer_segments():
    offsets, _ = resolve_end_offsets({"enabled": True, "source": "SOURCE_METADATA"}, _beam(),
                                     metadata=META)
    settings = inject_end_offsets({"ULS": {"frame_sections": {"Beam 600*800": {"J": 1.0}}}}, offsets)
    plan = compile_settings(settings, _beam(), [], {})["ULS"]["frame_segments"]
    assert plan[0]["joint_offsets_m"] == pytest.approx([.55, 0, 0, 0, 0, 0])
    assert plan[1]["joint_offsets_m"] == pytest.approx([0] * 6)
    assert plan[2]["joint_offsets_m"] == pytest.approx([0, 0, 0, -.625, 0, 0])
    # Axial and torsional flexibility stay over the full outer-segment length (CSI rule).
    assert plan[0]["properties"]["A"] == pytest.approx(.48 * (1.5 - .55) / 1.5)
    assert plan[2]["properties"]["J"] == pytest.approx(.031102 * (1.5 - .625) / 1.5)
    with pytest.raises(ValueError, match="already has end_offsets_m"):
        inject_end_offsets({"ULS": {"end_offsets_m": {"515": {}}}}, offsets)
    with pytest.raises(ValueError, match="non-empty elastic_etabs_comparison"):
        inject_end_offsets({}, offsets)


def test_preset_requires_verified_clear_beam_and_refuses_conflicts():
    base = {"etabs_beam_weight_policy": "ETABS_BEAM_CLEAR_LENGTH",
            "etabs_clear_beam_weight_confirmed": True, "floor_subdivisions": 4}
    out = apply_preset(base, ETABS_ELASTIC_GRAVITY_COMPARISON)
    assert "wall_max_cell_size_m" not in out   # ETABS walls: Wall Auto Mesh Default = unmeshed
    assert out["rigid_end_zones"]["enabled"] is True
    uls = out["elastic_etabs_comparison"]["ULS"]
    assert uls["use_native_frame_modifiers"] and uls["use_native_shell_modifiers"]
    assert "shear_flexible_sections" not in uls
    assert "comparison_preset" not in base and "rigid_end_zones" not in base
    with pytest.raises(ValueError, match="verified clear-beam"):
        apply_preset({"etabs_beam_weight_policy": "GROSS_SECTION_LENGTH"},
                     ETABS_ELASTIC_GRAVITY_COMPARISON)
    with pytest.raises(ValueError, match="differently"):
        apply_preset({**base, "rigid_end_zones": {"enabled": False}}, ETABS_ELASTIC_GRAVITY_COMPARISON)
    with pytest.raises(ValueError, match="Unknown comparison preset"):
        preset_settings("NOPE")
    json.dumps(out)


def test_no_superseded_gravity_literal_in_new_modules():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for rel in ("components/model/rigid_end_zones.py", "components/model/etabs_comparison_preset.py",
                "tools/etabs_comparison_ablation.py"):
        assert "9.80665" not in (root / rel).read_text(encoding="utf-8")
