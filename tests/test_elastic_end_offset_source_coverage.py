"""Deterministic rigid-end-zone conversion provenance regressions.

These tests check unmodeled source assignments, not ETABS/OpenSees native
reaction equivalence.
"""
import pytest

from components.model.elastic_conversion_settings import (
    audit_native_end_offset_coverage,
    compile_settings,
)


def frame(obj, section):
    return {
        "object": str(obj), "category": "COLUMN" if "Col" in section else "BEAM",
        "start": 0., "end": 6., "length": 6.,
        "basis": ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.)),
        "properties": {"section": section, "A": 0.5, "J": 0.1,
                       "Iy": 0.1, "Iz": 0.1, "E": 2.5e7, "G": 1e7,
                       "As2": 0.4, "As3": 0.4},
    }


def metadata():
    return {"frames": {
        "1": {"GetEndLengthOffset": [True, 0.0, 0.8, 1.0, 0]},
        "2": {"GetEndLengthOffset": [True, 0.55, 0.55, 1.0, 0]},
        "3": {"GetEndLengthOffset": [True, 0.0, 0.0, 0.0, 0]},
    }}


FRAMES = [frame("1", "Col 1100*1100"), frame("2", "Beam 600*800"),
          frame("3", "BRACE")]


def test_native_rigid_zone_omission_is_visible_even_with_correct_section_modifiers():
    plan = compile_settings({"ULS": {"shear_flexible_sections": [
        "Col 1100*1100", "Beam 600*800"]}}, FRAMES, [], metadata())["ULS"]
    coverage = plan["native_end_offset_coverage"]
    assert coverage["assembled_unique_frame_objects"] == 3
    assert coverage["native_active_rigid_zone_objects"] == 2
    assert coverage["native_rigid_zone_on_selected_shear_flexible_objects"] == 2
    assert coverage["native_offsets_unmodeled_count"] == 2
    assert coverage["native_offsets_configured_exact_count"] == 0
    assert coverage["status"] == "NATIVE_RIGID_ZONE_COVERAGE_INCOMPLETE"
    assert coverage["engineering_acceptance"] == "NOT_VERIFIED"
    assert all(not any(row["joint_offsets_m"]) for row in plan["frame_segments"])


def test_exact_source_offset_entries_are_identified_but_not_accepted_as_native():
    options = {"end_offsets_m": {
        "1": {"i": 0., "j": 0.8, "rigid_fraction": 1.},
        "2": {"i": 0.55, "j": 0.55, "rigid_fraction": 1.},
    }}
    coverage = audit_native_end_offset_coverage(options, FRAMES, metadata())
    assert coverage["status"] == "NATIVE_RIGID_ZONE_INPUTS_MATCH_SOURCE_NOT_SOLVER_VALIDATION"
    assert coverage["native_offsets_configured_exact_count"] == 2
    assert coverage["native_offsets_unmodeled_count"] == 0
    assert coverage["native_rigid_zone_on_selected_shear_flexible_objects"] == 0
    assert coverage["engineering_acceptance"] == "NOT_VERIFIED"
    plan = compile_settings({"ULS": options}, FRAMES, [], metadata())["ULS"]
    assert plan["frame_segments"][0]["joint_offsets_m"][3:] == pytest.approx([-0.8,0,0])


def test_mismatched_source_rigid_length_is_flagged_not_silently_called_equivalent():
    options = {"end_offsets_m": {
        "1": {"i": 0., "j": 0.7, "rigid_fraction": 1.0},
    }}
    result = audit_native_end_offset_coverage(options, FRAMES, metadata())
    assert result["native_offsets_differ_from_source_count"] == 1
    assert result["native_offsets_unmodeled_count"] == 1
    assert result["status"] == "NATIVE_RIGID_ZONE_COVERAGE_INCOMPLETE"


def test_source_rigid_offsets_and_timoshenko_are_still_rejected_by_production_element():
    options = {"shear_flexible_sections": ["Col 1100*1100"],
               "end_offsets_m": {
                   "1": {"i": 0., "j": 0.8, "rigid_fraction": 1.}
               }}
    coverage = audit_native_end_offset_coverage(options, FRAMES, metadata())
    assert coverage["native_rigid_zone_on_selected_shear_flexible_objects"] == 1
    with pytest.raises(ValueError, match="combined Timoshenko and joint offsets"):
        compile_settings({"ULS": options}, FRAMES, [], metadata())


def test_unavailable_source_cannot_be_reported_as_a_pass():
    coverage = audit_native_end_offset_coverage({}, FRAMES, {})
    assert coverage["native_offset_metadata_missing_count"] == 3
    assert coverage["status"] == "NATIVE_RIGID_ZONE_SOURCE_METADATA_UNAVAILABLE"
    assert coverage["engineering_acceptance"] == "NOT_VERIFIED"
