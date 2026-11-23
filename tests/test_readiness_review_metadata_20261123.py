"""Readiness GUI review inputs require named, dated human evidence."""
from components.model.readiness_gui import review_metadata_problems


def test_checked_evidence_requires_named_reviewer_date_and_nonplaceholder_reference():
    checked={"wall_opening_and_coupling_beam_mesh_reviewed":True,"modal_periods_modes_and_mass_participation_reviewed":False}
    ev={"wall_opening_and_coupling_beam_mesh_reviewed":"AVAILABLE FOR REVIEW: mesh.json"}
    assert "reference" in ";".join(review_metadata_problems(checked,ev,{},{})).lower()
    ev["wall_opening_and_coupling_beam_mesh_reviewed"]="Model-specific reviewed wall drawing and mesh audit 2026"
    issues=review_metadata_problems(checked,ev,{}, {})
    assert any("reviewer" in x for x in issues)
    issues=review_metadata_problems(checked,ev,{"wall_opening_and_coupling_beam_mesh_reviewed":"Civil reviewer"},
                                     {"wall_opening_and_coupling_beam_mesh_reviewed":"not a date"})
    assert any("ISO" in x for x in issues)
    issues=review_metadata_problems(checked,ev,{"wall_opening_and_coupling_beam_mesh_reviewed":"Civil reviewer"},
                                     {"wall_opening_and_coupling_beam_mesh_reviewed":"2026-11-23"})
    assert issues==[]


def test_unchecked_items_cannot_be_automatically_promoted():
    checked={"a":False}
    issues=review_metadata_problems(checked,{"a":"AVAILABLE FOR REVIEW: model.json"},{},{})
    assert issues==[]
