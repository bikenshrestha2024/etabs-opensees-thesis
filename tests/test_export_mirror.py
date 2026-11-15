"""Export organization never mutates flat source files or existing evidence."""
import hashlib
import json
import pytest
from components.inputs.export_mirror import export_mirror

def test_mirror_preserves_source_and_categorizes(tmp_path):
    original=tmp_path/"OpenSees_Element_Connectivity.json"
    original.write_text('{"hello":1}')
    load=tmp_path/"OpenSees_Load_Conversion_Audit.csv"
    load.write_text("a,b\n1,2\n")
    e=tmp_path/"source.edb"
    e.write_bytes(b"never touched")
    before=hashlib.sha256(original.read_bytes()).hexdigest()
    manifest=export_mirror(tmp_path)
    data=json.loads(manifest.read_text())
    assert data["status"]=="MIRRORED_LEGACY_PATHS_PRESERVED"
    assert (tmp_path/"01_ETABS_EXPORT"/"02_MAPPING"/original.name).read_bytes()==original.read_bytes()
    assert (tmp_path/"01_ETABS_EXPORT"/"03_LOADS"/load.name).is_file()
    assert e.read_bytes()==b"never touched"
    assert hashlib.sha256(original.read_bytes()).hexdigest()==before
    assert len(data["files"])==2

def test_mirror_fails_before_clobbering_existing_different_file(tmp_path):
    (tmp_path/"OpenSees_Element_Connectivity.json").write_text("source")
    target=tmp_path/"01_ETABS_EXPORT"/"02_MAPPING"
    target.mkdir(parents=True)
    (target/"OpenSees_Element_Connectivity.json").write_text("different")
    with pytest.raises(ValueError, match="differs"):
        export_mirror(tmp_path)
    assert (target/"OpenSees_Element_Connectivity.json").read_text()=="different"

def test_mirror_refuses_symlinked_destination(tmp_path):
    original=tmp_path/"OpenSees_Element_Connectivity.json"
    original.write_text('{"real":true}')
    outside=tmp_path/"external"
    outside.mkdir()
    target=tmp_path/"01_ETABS_EXPORT"
    target.mkdir()
    try:
        (target/"02_MAPPING").symlink_to(outside,target_is_directory=True)
    except (OSError,NotImplementedError):
        pytest.skip("Creating symlinks is not permitted on this Windows runner")
    with pytest.raises(ValueError,match="symlink"):
        export_mirror(tmp_path)
    assert not (outside/original.name).exists()

def test_late_conflict_preflights_before_copying_anything(tmp_path):
    """A conflicting last file must not leave earlier new mirror copies."""
    (tmp_path / "A_Export.json").write_text("source-a", encoding="utf-8")
    (tmp_path / "Z_Export.json").write_text("source-z", encoding="utf-8")
    target = tmp_path / "01_ETABS_EXPORT" / "01_SOURCE"
    target.mkdir(parents=True)
    (target / "Z_Export.json").write_text("older-z", encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        export_mirror(tmp_path)
    assert not (target / "A_Export.json").exists()
    assert (target / "Z_Export.json").read_text() == "older-z"
    assert not (tmp_path / "01_ETABS_EXPORT" / "00_MANIFEST").exists()


def test_symlinked_export_root_rejected(tmp_path):
    actual = tmp_path / "real"
    actual.mkdir()
    (actual / "OpenSees_Element_Connectivity.json").write_text("source")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(actual, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable")
    with pytest.raises(ValueError, match="symlinked selected export root"):
        export_mirror(alias)
    assert not (actual / "01_ETABS_EXPORT").exists()
