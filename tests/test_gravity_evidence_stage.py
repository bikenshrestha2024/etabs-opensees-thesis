"""Tests for real ETABS workbook staging; no ETABS installation required."""
import json
from pathlib import Path
from zipfile import ZipFile
import pytest
from components.inputs.gravity_evidence_stage import (
    stage_gravity_workbooks, staged_gravity_workbooks, manifest_path,
    file_sha256,
)


def workbook(path):
    """Minimal valid OOXML ZIP for staging (not structural data validation)."""
    with ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("xl/workbook.xml", "<workbook/>")
    return path


def test_stages_both_and_preserves_bytes(tmp_path):
    export = tmp_path / "export"
    export.mkdir()
    a = workbook(tmp_path / "assignment.xlsx")
    b = workbook(tmp_path / "full_table.xlsx")
    before = (file_sha256(a), file_sha256(b))
    manifest = stage_gravity_workbooks(export, assignment=a, full_table=b)
    assert manifest == manifest_path(export)
    staged = staged_gravity_workbooks(export)
    assert (file_sha256(staged["etabs_assignment"]),
            file_sha256(staged["etabs_full_table"])) == before
    assert json.loads(manifest.read_text())["status"] == "STAGED_NOT_ETABS_VALIDATED"


def test_lfs_pointer_is_rejected(tmp_path):
    export = tmp_path / "export"
    export.mkdir()
    pointer = tmp_path / "source.xlsx"
    pointer.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:fake")
    with pytest.raises(ValueError, match="Git LFS pointer"):
        stage_gravity_workbooks(export, assignment=pointer,
                                full_table=workbook(tmp_path / "real.xlsx"))


def test_tampered_staged_workbook_is_rejected(tmp_path):
    export = tmp_path / "export"
    export.mkdir()
    stage_gravity_workbooks(export, assignment=workbook(tmp_path / "a.xlsx"),
                            full_table=workbook(tmp_path / "b.xlsx"))
    staged = staged_gravity_workbooks(export)
    Path(staged["etabs_assignment"]).write_bytes(b"tampered")
    with pytest.raises(ValueError):
        staged_gravity_workbooks(export)


def test_unchanged_edb_is_hash_bound(tmp_path):
    export = tmp_path / "export"
    export.mkdir()
    edb = tmp_path / "source.edb"
    edb.write_bytes(b"original source")
    stage_gravity_workbooks(export, assignment=workbook(tmp_path / "a.xlsx"),
                            full_table=workbook(tmp_path / "b.xlsx"), source_edb=edb)
    assert len(staged_gravity_workbooks(export)) == 2
    edb.write_bytes(b"changed source")
    with pytest.raises(ValueError, match="EDB hash"):
        staged_gravity_workbooks(export)
